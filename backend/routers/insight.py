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
async def get_daily_insight(user_id: int, lang: str = "en", db: Session = Depends(get_db)):
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
    
    if latest_insight and getattr(latest_insight, 'ai_model', '').endswith(f'|lang={lang}'):
        return DailyInsightResponse(
            insight=latest_insight.insight_text,
            suggestions=latest_insight.suggestions.split(", ") if latest_insight.suggestions else [],
            patterns=patterns[:3],
            wellness_score=today_score
        )
    
    # If health records exist but no insight, try to generate one
    from backend.ai.chains.insight_chain import generate_ai_insight

    fallback_msgs = {
        "en": {
            "start": "Start tracking your health data to get personalized insights.",
            "s1": "Connect Google Fit for automatic data sync",
            "s2": "Log your daily sleep, stress, and activity"
        },
        "hi": {
            "start": "व्यक्तिगत अंतर्दृष्टि पाने के लिए अपना स्वास्थ्य डेटा ट्रैक करना शुरू करें।",
            "s1": "स्वचालित डेटा सिंक के लिए Google Fit से कनेक्ट करें",
            "s2": "अपनी दैनिक नींद, तनाव और गतिविधि लॉग करें"
        },
        "te": {
            "start": "వ్యక్తిగతీకరించిన అంతర్దృష్టులు పొందడానికి మీ ఆరోగ్య డేటాను ట్రాక్ చేయడం ప్రారంభించండి.",
            "s1": "స్వయంచాలక డేటా సమకాలీకరణ కోసం Google Fitని కనెక్ట్ చేయండి",
            "s2": "మీ రోజువారీ నిద్ర, ఒత్తిడి మరియు కార్యకలాపాలను లాగ్ చేయండి"
        }
    }
    fb = fallback_msgs.get(lang, fallback_msgs["en"])

    try:
        ai_insight = generate_ai_insight(user_id, "daily", db, lang=lang)
        
        new_insight = Insight(
            user_id=user_id,
            insight_text=ai_insight.get("insight", ""),
            suggestions=ai_insight.get("suggestions", ""),
            ai_model=f"{ai_insight.get('model', 'mistralai/mistral-7b-instruct')}|lang={lang}",
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
            insight=fb["start"],
            suggestions=[fb["s1"], fb["s2"]],
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

@router.get("/alerts")
async def get_alerts(user_id: int, lang: str = "en", db: Session = Depends(get_db)):
    week_ago = datetime.utcnow() - timedelta(days=7)
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)

    # Fetch today's health records for real-time rule-based alerts
    today_records = db.query(HealthRecord).filter(
        HealthRecord.user_id == user_id,
        HealthRecord.date >= today,
        HealthRecord.date < tomorrow
    ).all()

    dynamic_alerts = []

    if today_records:
        # Aggregate all of today's records (same logic as /health/today)
        agg = {
            "sleep_hours": None, "steps": None, "heart_rate": None,
            "stress_level": None, "screen_time": None, "calories": None
        }
        for rec in today_records:
            if rec.sleep_hours  is not None: agg["sleep_hours"]  = rec.sleep_hours
            if rec.steps        is not None: agg["steps"]        = rec.steps
            if rec.heart_rate   is not None: agg["heart_rate"]   = rec.heart_rate
            if rec.stress_level is not None: agg["stress_level"] = rec.stress_level
            if rec.screen_time  is not None: agg["screen_time"]  = rec.screen_time
            if rec.calories     is not None: agg["calories"]     = rec.calories

        alert_id = 9000

        # Multilingual alert messages
        def alert_msg(key, **kwargs):
            msgs = {
                "en": {
                    "low_sleep": f"You only slept {kwargs.get('hours')} hours today. Adults need 7–9 hours for optimal health.",
                    "high_stress": f"Your stress level is {kwargs.get('level')}/10. Try breathing exercises or a short walk.",
                    "low_activity": f"You've only taken {int(kwargs.get('steps', 0)):,} steps today. Aim for at least 8,000 steps daily.",
                    "elevated_heart_rate": f"Your resting heart rate is {kwargs.get('hr')} bpm, above the normal range of 60–100 bpm.",
                    "high_screen_time": f"You've had {kwargs.get('hours')} hours of screen time today. Take regular breaks to protect your eyes."
                },
                "hi": {
                    "low_sleep": f"आज आप केवल {kwargs.get('hours')} घंटे सोए। वयस्कों को बेहतर स्वास्थ्य के लिए 7–9 घंटे की नींद चाहिए।",
                    "high_stress": f"आपका तनाव स्तर {kwargs.get('level')}/10 है। सांस लेने के व्यायाम या छोटी सैर करें।",
                    "low_activity": f"आपने आज केवल {int(kwargs.get('steps', 0)):,} कदम चले हैं। प्रतिदिन कम से कम 8,000 कदम चलें।",
                    "elevated_heart_rate": f"आपकी हृदय गति {kwargs.get('hr')} bpm है, जो 60–100 bpm की सामान्य सीमा से अधिक है।",
                    "high_screen_time": f"आज आपने {kwargs.get('hours')} घंटे स्क्रीन देखी। अपनी आँखों को बचाने के लिए नियमित विराम लें।"
                },
                "te": {
                    "low_sleep": f"మీరు ఈరోజు కేవలం {kwargs.get('hours')} గంటలు మాత్రమే నిద్రపోయారు. పెద్దలకు 7–9 గంటల నిద్ర అవసరం.",
                    "high_stress": f"మీ ఒత్తిడి స్థాయి {kwargs.get('level')}/10. శ్వాస వ్యాయామాలు లేదా చిన్న నడకను ప్రయత్నించండి.",
                    "low_activity": f"మీరు ఈరోజు కేవలం {int(kwargs.get('steps', 0)):,} అడుగులు మాత్రమే వేశారు. రోజుకు కనీసం 8,000 అడుగులు వేయండి.",
                    "elevated_heart_rate": f"మీ విశ్రాంతి హృదయ స్పందన రేటు {kwargs.get('hr')} bpm, ఇది 60–100 bpm పరిధి కంటే ఎక్కువ.",
                    "high_screen_time": f"మీరు ఈరోజు {kwargs.get('hours')} గంటలు స్క్రీన్ సమయం గడిపారు. మీ కళ్ళను రక్షించుకోవడానికి క్రమం తప్పకుండా విరామాలు తీసుకోండి."
                }
            }
            lang_msgs = msgs.get(lang, msgs["en"])
            return lang_msgs.get(key, "")

        if agg["sleep_hours"] is not None and agg["sleep_hours"] < 6:
            dynamic_alerts.append({
                "id": alert_id, "user_id": user_id,
                "pattern_type": "low_sleep",
                "description": alert_msg("low_sleep", hours=agg['sleep_hours']),
                "severity": "high" if agg["sleep_hours"] < 5 else "medium",
                "detected_at": datetime.utcnow()
            })
            alert_id += 1

        if agg["stress_level"] is not None and agg["stress_level"] >= 7:
            dynamic_alerts.append({
                "id": alert_id, "user_id": user_id,
                "pattern_type": "high_stress",
                "description": alert_msg("high_stress", level=agg['stress_level']),
                "severity": "critical" if agg["stress_level"] >= 9 else "high",
                "detected_at": datetime.utcnow()
            })
            alert_id += 1

        if agg["steps"] is not None and agg["steps"] < 4000:
            dynamic_alerts.append({
                "id": alert_id, "user_id": user_id,
                "pattern_type": "low_activity",
                "description": alert_msg("low_activity", steps=agg['steps']),
                "severity": "medium",
                "detected_at": datetime.utcnow()
            })
            alert_id += 1

        if agg["heart_rate"] is not None and agg["heart_rate"] > 100:
            dynamic_alerts.append({
                "id": alert_id, "user_id": user_id,
                "pattern_type": "elevated_heart_rate",
                "description": alert_msg("elevated_heart_rate", hr=agg['heart_rate']),
                "severity": "high",
                "detected_at": datetime.utcnow()
            })
            alert_id += 1

        if agg["screen_time"] is not None and agg["screen_time"] > 6:
            dynamic_alerts.append({
                "id": alert_id, "user_id": user_id,
                "pattern_type": "high_screen_time",
                "description": alert_msg("high_screen_time", hours=agg['screen_time']),
                "severity": "medium",
                "detected_at": datetime.utcnow()
            })
            alert_id += 1

    # Also include any DB-stored high severity patterns from past week
    db_alerts = db.query(Pattern).filter(
        Pattern.user_id == user_id,
        Pattern.detected_at >= week_ago,
        Pattern.severity.in_(["high", "critical"])
    ).order_by(Pattern.detected_at.desc()).all()

    db_alert_dicts = [
        {
            "id": p.id, "user_id": p.user_id,
            "pattern_type": p.pattern_type,
            "description": p.description,
            "severity": p.severity,
            "detected_at": p.detected_at
        }
        for p in db_alerts
    ]

    return dynamic_alerts + db_alert_dicts


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
