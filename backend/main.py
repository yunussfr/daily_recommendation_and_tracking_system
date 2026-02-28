import json
import random
import unicodedata # Karakter hatalarını çözmek için ekledik
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from database import engine, get_db
import models
from sqlalchemy.orm import Session
from transformers import pipeline

# Veritabanı tablolarını oluştur
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Daily Motivation and Tracking API")

# Modeli yükle
classifier = pipeline(
    "text-classification",
    model="maymuni/bert-base-turkish-cased-emotion-analysis"
)

# JSON mesajları yükle
with open("messages.json", "r", encoding="utf-8") as f:
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

    # 1️⃣ Kullanıcıyı bul veya oluştur
    user = db.query(models.User).filter(
        models.User.platform_id == entry.telegram_chat_id
    ).first()

    if not user:
        user = models.User(
            username=f"user_{entry.telegram_chat_id}",
            platform_id=entry.telegram_chat_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
 

    # 2️⃣ Yapay zeka analizi
    prediction = classifier(entry.answer)[0]
    # NFKC normalizasyonu 'ü' harfinin farklı kodlanma (encoding) sorunlarını çözer
    raw_label = unicodedata.normalize('NFKC', str(prediction["label"]).lower().strip())

    print("\n" + "X" * 50)
    print(f"YAPAY ZEKA MODELİ ŞUNU BULDU: {prediction}")
    print(f"TEMİZLENMİŞ ETİKET: '{raw_label}'")

    # 3️⃣ ETİKET EŞLEME (IF-ELIF-ELSE - SİLİNMEDİ!)
    # 'in' operatörü kullanarak karakter hatalarının önüne geçiyoruz
    if "mutlu" in raw_label or "joy" in raw_label or "label_0" in raw_label:
        mapped_label = "joy"
    elif "üzgün" in raw_label or "uzgun" in raw_label or "sadness" in raw_label or "label_1" in raw_label:
        mapped_label = "sadness"
    elif "kızgın" in raw_label or "kizgin" in raw_label or "anger" in raw_label or "label_2" in raw_label:
        mapped_label = "anger"
    elif "kork" in raw_label or "fear" in raw_label or "label_3" in raw_label:
        mapped_label = "fear"
    elif "sevgi" in raw_label or "love" in raw_label or "label_4" in raw_label:
        mapped_label = "love"
    else:
        mapped_label = "neutral"

    print(f"EŞLEŞEN KATEGORİ: {mapped_label}")

    # 4️⃣ Veritabanı Etiketi
    if mapped_label == "joy": detected_feeling = "Mutlu"
    elif mapped_label == "sadness": detected_feeling = "Üzgün"
    elif mapped_label == "anger": detected_feeling = "Kızgın"
    elif mapped_label == "fear": detected_feeling = "Korkmuş"
    elif mapped_label == "love": detected_feeling = "Sevgi Dolu"
    else: detected_feeling = "Nötr"

    # 5️⃣ Günlük kayıt oluştur (SİLİNMEDİ!)
    daily_entry = models.DailyEntry(
        user_id=user.id,
        answer=entry.answer,
        detected_feeling=detected_feeling,
        weather="Güneşli"
    )
    db.add(daily_entry)

    daily_habits = models.DailyHabits(
        user_id=user.id,
        pages_read=entry.habits.pages_read,
        workout_minutes=entry.habits.workout_minutes,
        water_glasses=entry.habits.water_glasses,
        coding_hours=entry.habits.coding_hours
    )
    db.add(daily_habits)
    db.commit()

    # 6️⃣ Motivasyon mesajı üret
    if mapped_label in motivation_messages:
        category_list = motivation_messages[mapped_label]
    else:
        print(f"UYARI: {mapped_label} JSON'da yok, Nötr'e gidiliyor.")
        category_list = motivation_messages["neutral"]

    random_motivation = random.choice(category_list)
    print(f"EKRANA GİDEN MESAJ: {random_motivation}")
    print("X" * 50 + "\n")

    message = (
        f"{random_motivation} Dün {entry.habits.pages_read} sayfa kitap okudun "
        f"ve {entry.habits.coding_hours} saat kod yazdın. Harika gidiyorsun!"
    )

    activity = "Bugün hava güneşli, belki parkta biraz yürüyüş yapıp podcast dinleyebilirsin."

    return MotivationResponse(message=message, suggested_activity=activity)
