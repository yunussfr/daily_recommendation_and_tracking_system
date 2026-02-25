import json
import random
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from database import engine, get_db
import models
from sqlalchemy.orm import Session
# --- EKLEDİĞİMİZ KISIM 1: Model ve JSON İçin Gerekli Kütüphaneler ---
from transformers import pipeline

# Veritabanı tablolarını oluştur
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Daily Motivation and Tracking API")

# --- EKLEDİĞİMİZ KISIM 2: Modelin ve Mesajların Yüklenmesi ---
# Bu işlem uygulama başlarken bir kez yapılır, performansı korur.
classifier = pipeline("text-classification", model="maymuni/bert-base-turkish-cased-emotion-analysis")

with open("messages.json", "r") as f:
    motivation_messages = json.load(f)

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

    # --- DEĞİŞTİRDİĞİMİZ KISIM 3: Gerçek Yapay Zeka Analizi ---
    # Mock (sahte) mantık yerine BERT modelini kullanıyoruz
    prediction = classifier(entry.answer)[0]
    label = prediction['label'].lower() # 'joy', 'sadness', 'anger' vb. olur
    
    # Veritabanına kaydedilecek isim için Türkçeleştirme (opsiyonel)
    emotion_map = {
        "joy": "Mutlu", "sadness": "Üzgün", "anger": "Kızgın", 
        "fear": "Korkmuş", "love": "Sevgi Dolu", "neutral": "Nötr"
    }
    detected_feeling = emotion_map.get(label, "Nötr")
    
    # 4. Hava durumu API'sinden veri alınacak (Şimdilik mock kalabilir)
    weather = "Güneşli"
    
    # 5. Günlük yanıtı kaydet
    daily_entry = models.DailyEntry(
        user_id=user.id,
        answer=entry.answer,
        detected_feeling=detected_feeling,
        weather=weather
    )
    db.add(daily_entry)

    # 6. Günlük alışkanlıkları kaydet
    daily_habits = models.DailyHabits(
        user_id=user.id,
        pages_read=entry.habits.pages_read,
        workout_minutes=entry.habits.workout_minutes,
        water_glasses=entry.habits.water_glasses,
        coding_hours=entry.habits.coding_hours
    )
    db.add(daily_habits)
    db.commit()
    
    # --- DEĞİŞTİRDİĞİMİZ KISIM 4: Dinamik Motivasyon Mesajı ---
    # Modelin bulduğu duyguya göre JSON'dan rastgele mesaj çekiyoruz
    category_list = motivation_messages.get(label, motivation_messages["neutral"])
    random_motivation = random.choice(category_list)

    # Senin mevcut formatınla birleştiriyoruz
    message = (
        f"{random_motivation} Dün {entry.habits.pages_read} sayfa kitap okudun ve "
        f"{entry.habits.coding_hours} saat kod yazdın. Harika gidiyorsun!"
    )
    
    activity = "Bugün hava güneşli, belki parkta biraz yürüyüş yapıp podcast dinleyebilirsin."
    
    return MotivationResponse(message=message, suggested_activity=activity)
