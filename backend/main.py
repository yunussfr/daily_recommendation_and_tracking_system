from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from database import engine, get_db
import models
from sqlalchemy.orm import Session

# Veritabanı tablolarını oluştur
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Daily Motivation and Tracking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DailyHabitsInput(BaseModel):
    pages_read: int = 0
    workout_minutes: int = 0
    water_glasses: int = 0
    coding_hours: float = 0.0

class DailyEntryInput(BaseModel):
    telegram_chat_id: str
    answer: str
    habits: DailyHabitsInput

class MotivationResponse(BaseModel):
    message: str
    suggested_activity: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Welcome to Daily Motivation API. See /docs for endpoints."}

@app.post("/submit_daily", response_model=MotivationResponse)
def submit_daily_entry(entry: DailyEntryInput, db: Session = Depends(get_db)):
    # 1. Kullanıcıyı bul veya oluştur
    user = db.query(models.User).filter(models.User.platform_id == entry.telegram_chat_id).first()
    if not user:
        user = models.User(username=f"user_{entry.telegram_chat_id}", platform_id=entry.telegram_chat_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # 3. Hava durumu API'sinden veri alınacak (Şimdilik mock)
    weather = "Güneşli" # buraya sonradan bir url konulacak orada onun verisi çekilecek 
    
    # 4. Günlük yanıtı kaydet
    daily_entry = models.DailyEntry(
        user_id=user.id,
        answer=entry.answer,

        weather=weather
    )
    db.add(daily_entry)

    # 5. Günlük alışkanlıkları kaydet
    daily_habits = models.DailyHabits(
        user_id=user.id,
        pages_read=entry.habits.pages_read,
        workout_minutes=entry.habits.workout_minutes,
        water_glasses=entry.habits.water_glasses,
        coding_hours=entry.habits.coding_hours
    )
    db.add(daily_habits)
    db.commit()
    
    # 6. Motivasyon mesajı ve aktivite önerisi üretilecek
    message = (
        f"Dün {entry.habits.pages_read} sayfa kitap okudun ve {entry.habits.coding_hours} saat kod yazdın, "
    )
    activity = "Bugün hava güneşli, belki parkta biraz yürüyüş yapıp podcast dinleyebilirsin."
    
    return MotivationResponse(message=message, suggested_activity=activity)
