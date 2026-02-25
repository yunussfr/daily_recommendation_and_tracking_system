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
    raw_label = str(prediction["label"]).lower().strip()

    print("\n" + "🔍" * 20)
    print(f"MODELİN VERDİĞİ HAM ETİKET: '{raw_label}'")

    # 3️⃣ IF-ELSE ile Etiket Eşleme (Karakter hatalarını engellemek için)
    if raw_label in ["mutlu", "mutluluk", "joy", "label_0"]:
        mapped_label = "joy"
        print("DURUM: Mutluluk (Joy) bloğuna girildi.")
    elif raw_label in ["üzgün", "uzgun", "üzüntü", "sadness", "label_1"]:
        mapped_label = "sadness"
        print("DURUM: Üzüntü (Sadness) bloğuna girildi.")
    elif raw_label in ["kızgın", "kizgin", "öfke", "anger", "label_2"]:
        mapped_label = "anger"
        print("DURUM: Öfke (Anger) bloğuna girildi.")
    elif raw_label in ["korku", "korkmuş", "korkmus", "fear", "label_3"]:
        mapped_label = "fear"
        print("DURUM: Korku (Fear) bloğuna girildi.")
    elif raw_label in ["sevgi", "love", "label_4"]:
        mapped_label = "love"
        print("DURUM: Sevgi (Love) bloğuna girildi.")
    else:
        mapped_label = "neutral"
        print(f"DURUM: Eşleşme yok, '{raw_label}' bilinmiyor. Nötr seçildi.")

    # 4️⃣ Veritabanı Duygu Adı (Yine if-else garantisiyle)
    if mapped_label == "joy": detected_feeling = "Mutlu"
    elif mapped_label == "sadness": detected_feeling = "Üzgün"
    elif mapped_label == "anger": detected_feeling = "Kızgın"
    elif mapped_label == "fear": detected_feeling = "Korkmuş"
    elif mapped_label == "love": detected_feeling = "Sevgi Dolu"
    else: detected_feeling = "Nötr"

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

    # 6️⃣ IF-ELSE ile Motivasyon Mesajı Seçimi
    # JSON key hatalarını kontrol etmek için if-elif kullanıyoruz
    if mapped_label == "joy" and "joy" in motivation_messages:
        category_list = motivation_messages["joy"]
    elif mapped_label == "sadness" and "sadness" in motivation_messages:
        category_list = motivation_messages["sadness"]
    elif mapped_label == "anger" and "anger" in motivation_messages:
        category_list = motivation_messages["anger"]
    elif mapped_label == "fear" and "fear" in motivation_messages:
        category_list = motivation_messages["fear"]
    elif mapped_label == "love" and "love" in motivation_messages:
        category_list = motivation_messages["love"]
    else:
        print("DİKKAT: JSON anahtarı bulunamadı, Nötr mesajlar yükleniyor.")
        category_list = motivation_messages.get("neutral", ["Harika gidiyorsun!"])

    random_motivation = random.choice(category_list)
    print(f"SEÇİLEN MESAJ KATEGORİSİ: {mapped_label}")
    print("🔍" * 20 + "\n")

    message = (
        f"{random_motivation} Dün {entry.habits.pages_read} sayfa kitap okudun "
        f"ve {entry.habits.coding_hours} saat kod yazdın. Harika gidiyorsun!"
    )

    activity = "Bugün hava güneşli, belki parkta biraz yürüyüş yapıp podcast dinleyebilirsin."

    return MotivationResponse(message=message, suggested_activity=activity)
