from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class DataSourceEnum(str, Enum):
    MANUAL = "manual"
    GOOGLE_FIT = "google_fit"

class InsightTypeEnum(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    PATTERN = "pattern"

class SeverityLevelEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class UserBase(BaseModel):
    name: Optional[str] = None
    email: EmailStr

class UserCreate(UserBase):
    google_id: Optional[str] = None

class UserResponse(UserBase):
    id: int
    google_id: Optional[str] = None
    created_at: datetime
    last_login: datetime

    class Config:
        from_attributes = True

class HealthRecordBase(BaseModel):
    date: Optional[datetime] = None
    sleep_hours: Optional[float] = None
    stress_level: Optional[int] = None
    steps: Optional[int] = None
    screen_time: Optional[float] = None
    heart_rate: Optional[int] = None
    calories: Optional[float] = None

class HealthRecordCreate(HealthRecordBase):
    data_source: DataSourceEnum = DataSourceEnum.MANUAL

class HealthRecordResponse(HealthRecordBase):
    id: int
    user_id: int
    data_source: DataSourceEnum
    created_at: datetime

    class Config:
        from_attributes = True

class WellnessScoreBase(BaseModel):
    overall_score: float
    sleep_score: Optional[float] = None
    activity_score: Optional[float] = None
    heart_rate_score: Optional[float] = None
    stress_score: Optional[float] = None

class WellnessScoreCreate(WellnessScoreBase):
    pass

class WellnessScoreResponse(WellnessScoreBase):
    id: int
    user_id: int
    date: datetime

    class Config:
        from_attributes = True

class PatternBase(BaseModel):
    pattern_type: str
    description: str
    signals_involved: Optional[str] = None
    severity: SeverityLevelEnum = SeverityLevelEnum.MEDIUM

class PatternCreate(PatternBase):
    pass

class PatternResponse(PatternBase):
    id: int
    user_id: int
    detected_at: datetime

    class Config:
        from_attributes = True

class InsightBase(BaseModel):
    insight_text: str
    suggestions: Optional[str] = None
    ai_model: Optional[str] = None
    insight_type: InsightTypeEnum = InsightTypeEnum.DAILY

class InsightCreate(InsightBase):
    pass

class InsightResponse(InsightBase):
    id: int
    user_id: int
    date: datetime

    class Config:
        from_attributes = True

class GoogleOAuthRequest(BaseModel):
    code: str

class ManualHealthInput(BaseModel):
    sleep_hours: Optional[float] = None
    stress_level: Optional[int] = None
    steps: Optional[int] = None
    screen_time: Optional[float] = None
    heart_rate: Optional[int] = None
    calories: Optional[float] = None
    date: Optional[datetime] = None

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class HealthDataResponse(BaseModel):
    records: List[HealthRecordResponse]
    date_range: dict

class DailyInsightResponse(BaseModel):
    insight: str
    suggestions: List[str]
    patterns: List[PatternResponse]
    wellness_score: Optional[WellnessScoreResponse] = None
