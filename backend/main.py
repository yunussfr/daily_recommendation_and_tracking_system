import json
import random
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
    raw_label = prediction["label"]

    print("\n" + "="*50)
    print("MODEL ÇIKTISI:", prediction)
    print("="*50)

    label = raw_label.lower().strip()

    print("RAW LABEL:", raw_label)
    print("LOWER LABEL:", label)

    # 3️⃣ Etiket eşleme
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

    mapped_label = label_mapping.get(label)

    print("MAPPED LABEL:", mapped_label)
    print("JSON KEY VAR MI:", mapped_label in motivation_messages)

    if not mapped_label or mapped_label not in motivation_messages:
        print("KEY YOK → NEUTRAL'A DÜŞTÜ")
        mapped_label = "neutral"

    # 4️⃣ Veritabanına kaydedilecek Türkçe duygu adı
    emotion_map = {
        "joy": "Mutlu",
        "sadness": "Üzgün",
        "anger": "Kızgın",
        "fear": "Korkmuş",
        "love": "Sevgi Dolu",
        "neutral": "Nötr"
    }

    detected_feeling = emotion_map.get(mapped_label, "Nötr")

    # 5️⃣ Günlük kaydı oluştur
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
    category_list = motivation_messages.get(
        mapped_label,
        motivation_messages["neutral"]
    )

    random_motivation = random.choice(category_list)

    message = (
        f"{random_motivation} Dün {entry.habits.pages_read} sayfa kitap okudun "
        f"ve {entry.habits.coding_hours} saat kod yazdın. Harika gidiyorsun!"
    )

    activity = "Bugün hava güneşli, belki parkta biraz yürüyüş yapıp podcast dinleyebilirsin."

    return MotivationResponse(
        message=message,
        suggested_activity=activity
    )
