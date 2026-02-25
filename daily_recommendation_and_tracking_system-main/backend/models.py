from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    platform_id = Column(String, unique=True, index=True) # e.g. Telegram Chat ID
    
    entries = relationship("DailyEntry", back_populates="user")
    habits = relationship("DailyHabits", back_populates="user")

class DailyEntry(Base):
    __tablename__ = "daily_entries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, default=datetime.date.today)
    answer = Column(String)
    detected_feeling = Column(String)
    weather = Column(String)
    suggested_activity = Column(String)

    user = relationship("User", back_populates="entries")

class DailyHabits(Base):
    __tablename__ = "daily_habits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date, default=datetime.date.today)
    
    # Sabit Hedefler (Fixed Goals)
    pages_read = Column(Integer, default=0)
    workout_minutes = Column(Integer, default=0)
    water_glasses = Column(Integer, default=0)
    coding_hours = Column(Float, default=0.0)
    
    user = relationship("User", back_populates="habits")
