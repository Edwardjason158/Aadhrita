from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from backend.utils.database import get_db
from backend.schemas.schemas import WellnessScoreResponse, WellnessScoreCreate
from backend.models.models import User, HealthRecord, WellnessScore
from backend.services.wellness_score_service import WellnessScoreService

router = APIRouter(prefix="/score", tags=["Score"])

@router.get("/today", response_model=WellnessScoreResponse)
async def get_today_score(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    existing_score = db.query(WellnessScore).filter(
        WellnessScore.user_id == user_id,
        WellnessScore.date >= today,
        WellnessScore.date < tomorrow
    ).order_by(WellnessScore.date.desc()).first()
    
    if existing_score:
        return existing_score
    
    today_record = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.date >= today,
        HealthRecord.date < tomorrow
    ).first()
    
    if not today_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No health data available for today"
        )
    
    health_data = {
        "sleep_hours": today_record.sleep_hours,
        "steps": today_record.steps,
        "calories": today_record.calories,
        "heart_rate": today_record.heart_rate,
        "stress_level": today_record.stress_level
    }
    
    scores = WellnessScoreService.calculate_overall_score(health_data)
    
    score_record = WellnessScore(
        user_id=user_id,
        date=datetime.utcnow(),
        overall_score=scores["overall_score"],
        sleep_score=scores["sleep_score"],
        activity_score=scores["activity_score"],
        heart_rate_score=scores["heart_rate_score"],
        stress_score=scores["stress_score"]
    )
    
    db.add(score_record)
    db.commit()
    db.refresh(score_record)
    
    return score_record

@router.get("/history", response_model=List[WellnessScoreResponse])
async def get_score_history(
    user_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    start_date = datetime.utcnow() - timedelta(days=days)
    
    scores = db.query(WellnessScore).filter(
        WellnessScore.user_id == user_id,
        WellnessScore.date >= start_date
    ).order_by(WellnessScore.date.desc()).all()
    
    return scores

@router.post("/calculate")
async def calculate_score(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    records = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.date >= today,
        HealthRecord.date < tomorrow
    ).all()
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No health data available for today"
        )
    
    # Aggregate data from all records for today, taking the latest non-null value for each metric
    aggregated_data = {
        "sleep_hours": None,
        "steps": None,
        "calories": None,
        "heart_rate": None,
        "stress_level": None
    }
    
    for record in records:
        if record.sleep_hours is not None: aggregated_data["sleep_hours"] = record.sleep_hours
        if record.steps is not None: aggregated_data["steps"] = record.steps
        if record.calories is not None: aggregated_data["calories"] = record.calories
        if record.heart_rate is not None: aggregated_data["heart_rate"] = record.heart_rate
        if record.stress_level is not None: aggregated_data["stress_level"] = record.stress_level
    
    scores = WellnessScoreService.calculate_overall_score(aggregated_data)
    
    # Check if a score for today already exists to update it
    existing_score = db.query(WellnessScore).filter(
        WellnessScore.user_id == user_id,
        WellnessScore.date >= today,
        WellnessScore.date < tomorrow
    ).first()
    
    if existing_score:
        existing_score.overall_score = scores["overall_score"]
        existing_score.sleep_score = scores["sleep_score"]
        existing_score.activity_score = scores["activity_score"]
        existing_score.heart_rate_score = scores["heart_rate_score"]
        existing_score.stress_score = scores["stress_score"]
        existing_score.date = datetime.utcnow()
        score_record = existing_score
    else:
        score_record = WellnessScore(
            user_id=user_id,
            date=datetime.utcnow(),
            overall_score=scores["overall_score"],
            sleep_score=scores["sleep_score"],
            activity_score=scores["activity_score"],
            heart_rate_score=scores["heart_rate_score"],
            stress_score=scores["stress_score"]
        )
        db.add(score_record)
    
    # Invalidate existing daily insight so it can be regenerated with new data
    from backend.models.models import Insight
    db.query(Insight).filter(
        Insight.user_id == user_id,
        Insight.insight_type == "daily",
        Insight.date >= today,
        Insight.date < tomorrow
    ).delete()
    
    db.commit()
    db.refresh(score_record)
    
    return {
        "message": "Score calculated successfully",
        "score": scores,
        "color": WellnessScoreService.get_score_color(scores["overall_score"]),
        "label": WellnessScoreService.get_score_label(scores["overall_score"])
    }
