from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from backend.utils.database import get_db
from backend.schemas.schemas import (
    HealthRecordCreate, HealthRecordResponse, 
    ManualHealthInput, HealthDataResponse
)
from backend.models.models import User, HealthRecord, DataSource
from backend.services.data_processing_service import DataProcessingService
from backend.services.google_fit_service import GoogleFitService

router = APIRouter(prefix="/health", tags=["Health"])

@router.post("/manual", response_model=HealthRecordResponse)
async def add_manual_health_data(
    user_id: int,
    input_data: ManualHealthInput,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    cleaned_data = DataProcessingService.clean_health_data(input_data.dict(exclude_none=True))
    
    record = HealthRecord(
        user_id=user_id,
        date=input_data.date or datetime.utcnow(),
        data_source=DataSource.MANUAL,
        **cleaned_data
    )
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return record

@router.get("/today", response_model=HealthDataResponse)
async def get_today_health_data(user_id: int, db: Session = Depends(get_db)):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    records = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.date >= today,
        HealthRecord.date < tomorrow
    ).order_by(HealthRecord.date.asc()).all()
    
    if not records:
        return HealthDataResponse(
            records=[],
            date_range={"start": today.isoformat(), "end": tomorrow.isoformat()}
        )
    
    # Aggregate data from all records for today
    aggregated_data = {
        "sleep_hours": None,
        "steps": None,
        "calories": None,
        "heart_rate": None,
        "stress_level": None,
        "screen_time": None
    }
    
    for record in records:
        if record.sleep_hours is not None: aggregated_data["sleep_hours"] = record.sleep_hours
        if record.steps is not None: aggregated_data["steps"] = record.steps
        if record.calories is not None: aggregated_data["calories"] = record.calories
        if record.heart_rate is not None: aggregated_data["heart_rate"] = record.heart_rate
        if record.stress_level is not None: aggregated_data["stress_level"] = record.stress_level
        if record.screen_time is not None: aggregated_data["screen_time"] = record.screen_time
        
    # Create a summary record that fulfills the schema
    summary = HealthRecordResponse(
        id=records[0].id,
        user_id=user_id,
        date=records[-1].date,
        data_source=records[-1].data_source,
        created_at=records[0].created_at,
        **aggregated_data
    )
    
    return HealthDataResponse(
        records=[summary],
        date_range={"start": today.isoformat(), "end": tomorrow.isoformat()}
    )

@router.get("/week", response_model=HealthDataResponse)
async def get_week_health_data(user_id: int, db: Session = Depends(get_db)):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    
    records = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.date >= week_ago,
        HealthRecord.date < today + timedelta(days=1)
    ).order_by(HealthRecord.date).all()
    
    return HealthDataResponse(
        records=records,
        date_range={"start": week_ago.isoformat(), "end": today.isoformat()}
    )

@router.get("/month", response_model=HealthDataResponse)
async def get_month_health_data(user_id: int, db: Session = Depends(get_db)):
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    month_ago = today - timedelta(days=30)
    
    records = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.date >= month_ago,
        HealthRecord.date < today + timedelta(days=1)
    ).order_by(HealthRecord.date).all()
    
    return HealthDataResponse(
        records=records,
        date_range={"start": month_ago.isoformat(), "end": today.isoformat()}
    )

@router.post("/sync")
async def sync_google_fit_data(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.google_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google Fit not connected. Please go to Settings to connect."
        )
    
    google_service = GoogleFitService(
        access_token=user.google_access_token,
        refresh_token=user.google_refresh_token
    )
    
    # Try to sync data. If it fails, try refreshing the token once.
    health_data = google_service.sync_health_data()
    
    # If all metrics are None, it might be an expired token
    if all(v is None for k, v in health_data.items() if k != "date" and k != "data_source"):
        if google_service.refresh_access_token():
            user.google_access_token = google_service.access_token
            db.commit()
            health_data = google_service.sync_health_data()
    
    record = HealthRecord(
        user_id=user_id,
        date=datetime.utcnow(),
        data_source=DataSource.GOOGLE_FIT,
        sleep_hours=health_data.get("sleep_hours"),
        steps=health_data.get("steps"),
        heart_rate=health_data.get("heart_rate"),
        calories=health_data.get("calories")
    )
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    # Trigger score recalculation after sync
    from backend.routers.score import calculate_score
    try:
        await calculate_score(user_id, db)
    except Exception as e:
        print(f"Failed to auto-calculate score after sync: {e}")
    
    return {"message": "Data synced successfully", "data": health_data}

@router.get("/records", response_model=list[HealthRecordResponse])
async def get_health_records(
    user_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 30,
    db: Session = Depends(get_db)
):
    query = db.query(HealthRecord).filter(HealthRecord.user_id == user_id)
    
    if start_date:
        query = query.filter(HealthRecord.date >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(HealthRecord.date <= datetime.fromisoformat(end_date))
    
    records = query.order_by(HealthRecord.date.desc()).limit(limit).all()
    
    return records
