from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class DataSource(str, enum.Enum):
    MANUAL = "manual"
    GOOGLE_FIT = "google_fit"

class InsightType(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    PATTERN = "pattern"

class SeverityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    google_id = Column(String(255), unique=True, index=True, nullable=True)
    google_access_token = Column(Text, nullable=True)
    google_refresh_token = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)

    health_records = relationship("HealthRecord", back_populates="user")
    wellness_scores = relationship("WellnessScore", back_populates="user")
    patterns = relationship("Pattern", back_populates="user")
    insights = relationship("Insight", back_populates="user")

class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    sleep_hours = Column(Float, nullable=True)
    stress_level = Column(Integer, nullable=True)
    steps = Column(Integer, nullable=True)
    screen_time = Column(Float, nullable=True)
    heart_rate = Column(Integer, nullable=True)
    calories = Column(Float, nullable=True)
    data_source = Column(Enum(DataSource), default=DataSource.MANUAL)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="health_records")

class WellnessScore(Base):
    __tablename__ = "wellness_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    overall_score = Column(Float, nullable=False)
    sleep_score = Column(Float, nullable=True)
    activity_score = Column(Float, nullable=True)
    heart_rate_score = Column(Float, nullable=True)
    stress_score = Column(Float, nullable=True)

    user = relationship("User", back_populates="wellness_scores")

class Pattern(Base):
    __tablename__ = "patterns"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pattern_type = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    signals_involved = Column(Text, nullable=True)
    severity = Column(Enum(SeverityLevel), default=SeverityLevel.MEDIUM)
    detected_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="patterns")

class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    insight_text = Column(Text, nullable=False)
    suggestions = Column(Text, nullable=True)
    ai_model = Column(String(255), nullable=True)
    insight_type = Column(Enum(InsightType), default=InsightType.DAILY)

    user = relationship("User", back_populates="insights")
