from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from backend.utils.database import get_db
from backend.schemas.schemas import (
    InsightResponse, InsightCreate, PatternResponse,
    DailyInsightResponse
)
from backend.models.models import User, HealthRecord, Insight, Pattern, WellnessScore
from backend.services.pattern_detection_service import PatternDetectionService
from backend.services.wellness_score_service import WellnessScoreService

router = APIRouter(prefix="/insights", tags=["Insights"])

@router.get("/daily", response_model=DailyInsightResponse)
async def get_daily_insight(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    today_records = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.date >= today,
        HealthRecord.date < tomorrow
    ).all()
    
    patterns = db.query(Pattern).filter(
        Pattern.user_id == user_id,
        Pattern.detected_at >= today - timedelta(days=7)
    ).order_by(Pattern.detected_at.desc()).all()
    
    today_score = db.query(WellnessScore).filter(
        WellnessScore.user_id == user_id,
        WellnessScore.date >= today,
        WellnessScore.date < tomorrow
    ).first()
    
    if not today_records:
        return DailyInsightResponse(
            insight="",
            suggestions=[],
            patterns=[],
            wellness_score=None
        )
    
    today_data = today_records[0]
    health_dict = {
        "sleep_hours": today_data.sleep_hours,
        "stress_level": today_data.stress_level,
        "steps": today_data.steps,
        "heart_rate": today_data.heart_rate,
        "calories": today_data.calories
    }
    
    latest_insight = db.query(Insight).filter(
        Insight.user_id == user_id,
        Insight.insight_type == "daily",
        Insight.date >= today
    ).first()
    
    if latest_insight:
        return DailyInsightResponse(
            insight=latest_insight.insight_text,
            suggestions=latest_insight.suggestions.split(", ") if latest_insight.suggestions else [],
            patterns=patterns[:3],
            wellness_score=today_score
        )
    
    # If health records exist but no insight, try to generate one
    from backend.ai.chains.insight_chain import generate_ai_insight
    try:
        ai_insight = generate_ai_insight(user_id, "daily", db)
        
        new_insight = Insight(
            user_id=user_id,
            insight_text=ai_insight.get("insight", ""),
            suggestions=ai_insight.get("suggestions", ""),
            ai_model=ai_insight.get("model", "mistralai/mistral-7b-instruct"),
            insight_type="daily"
        )
        
        db.add(new_insight)
        db.commit()
        db.refresh(new_insight)
        
        return DailyInsightResponse(
            insight=new_insight.insight_text,
            suggestions=new_insight.suggestions.split(", ") if new_insight.suggestions else [],
            patterns=patterns[:3],
            wellness_score=today_score
        )
    except Exception as e:
        print(f"Failed to auto-generate insight: {e}")
        return DailyInsightResponse(
            insight="Start tracking your health data to get personalized insights.",
            suggestions=[
                "Connect Google Fit for automatic data sync",
                "Log your daily sleep, stress, and activity"
            ],
            patterns=patterns[:3],
            wellness_score=today_score
        )

@router.get("/weekly", response_model=InsightResponse)
async def get_weekly_insight(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    week_insight = db.query(Insight).filter(
        Insight.user_id == user_id,
        Insight.insight_type == "weekly",
        Insight.date >= week_ago
    ).first()
    
    if week_insight:
        return week_insight
    
    records = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.date >= week_ago
    ).order_by(HealthRecord.date).all()
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No health records found for the past week"
        )
    
    return InsightResponse(
        id=0,
        user_id=user_id,
        date=datetime.utcnow(),
        insight_text="Not enough data for weekly summary. Keep tracking your health!",
        suggestions="Log at least 5 days of data",
        ai_model=None,
        insight_type="weekly"
    )

@router.get("/patterns", response_model=List[PatternResponse])
async def get_patterns(user_id: int, limit: int = 10, db: Session = Depends(get_db)):
    patterns = db.query(Pattern).filter(
        Pattern.user_id == user_id
    ).order_by(Pattern.detected_at.desc()).limit(limit).all()
    
    return patterns

@router.get("/alerts", response_model=List[PatternResponse])
async def get_alerts(user_id: int, db: Session = Depends(get_db)):
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    alerts = db.query(Pattern).filter(
        Pattern.user_id == user_id,
        Pattern.detected_at >= week_ago,
        Pattern.severity.in_(["high", "critical"])
    ).order_by(Pattern.detected_at.desc()).all()
    
    return alerts

@router.post("/generate")
async def generate_insight(user_id: int, insight_type: str = "daily", db: Session = Depends(get_db)):
    from backend.ai.chains.insight_chain import generate_ai_insight
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        ai_insight = generate_ai_insight(user_id, insight_type, db)
        
        insight = Insight(
            user_id=user_id,
            insight_text=ai_insight.get("insight", ""),
            suggestions=ai_insight.get("suggestions", ""),
            ai_model=ai_insight.get("model", "mistralai/mistral-7b-instruct"),
            insight_type=insight_type
        )
        
        db.add(insight)
        db.commit()
        db.refresh(insight)
        
        return {"message": "Insight generated successfully", "insight": insight}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insight: {str(e)}"
        )
