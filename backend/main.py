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
    prediction = classifier(entry.answer)[0]
    raw_label = prediction['label']
    
    # HATA AYIKLAMA (DEBUG): Terminalde modelin gerçekte ne döndürdüğünü görmek için
    print(f"\n{'='*50}")
    print(f"YAPAY ZEKA MODELİ ŞUNU BULDU: {prediction}")
    print(f"{'='*50}\n")
    
    label = raw_label.lower()
    
    # ETİKET ÇEVİRİCİ: Modelden gelebilecek formatları (Türkçe, İngilizce veya Sayı) yakalıyoruz
   label_mapping = {
    "mutlu": "joy",
    "mutluluk": "joy",
    "joy": "joy",
    "label_0": "joy",

    "üzgün": "sadness",
    "uzgun": "sadness",
    "üzüntü": "sadness",
    "sadness": "sadness",
    "label_1": "sadness",

    "kızgın": "anger",
    "kizgin": "anger",
    "kızgınlık": "anger",
    "öfke": "anger",
    "ofke": "anger",
    "anger": "anger",
    "label_2": "anger",

    "korkmuş": "fear",
    "korkmus": "fear",
    "korku": "fear",
    "fear": "fear",
    "label_3": "fear",

    "sevgi": "love",
    "love": "love",
    "label_4": "love"
}
    
    # Modelin etiketini JSON anahtarlarımıza çeviriyoruz (bulamazsa nötr kalır)
    mapped_label = label_mapping.get(label, "neutral")
    
    # Veritabanına kaydedilecek isim için Türkçeleştirme
    emotion_map = {
        "joy": "Mutlu", "sadness": "Üzgün", "anger": "Kızgın", 
        "fear": "Korkmuş", "love": "Sevgi Dolu", "neutral": "Nötr"
    }
    detected_feeling = emotion_map.get(mapped_label, "Nötr")
    
    # 4. Hava durumu API'sinden veri alınacak (Şimdilik mock)
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
    category_list = motivation_messages.get(mapped_label, motivation_messages["neutral"])
    random_motivation = random.choice(category_list)

    message = (
        f"{random_motivation} Dün {entry.habits.pages_read} sayfa kitap okudun ve "
        f"{entry.habits.coding_hours} saat kod yazdın. Harika gidiyorsun!"
    )
    
    activity = "Bugün hava güneşli, belki parkta biraz yürüyüş yapıp podcast dinleyebilirsin."
    
    return MotivationResponse(message=message, suggested_activity=activity)
