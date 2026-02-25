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

    print("\n" + "==================================================")
    print(f"YAPAY ZEKA MODELİ ŞUNU BULDU: {prediction}")
    print(f"HAM ETİKET (TEMİZLENMİŞ): '{raw_label}'")
    print("==================================================")

    # 3️⃣ ETİKET EŞLEME (IF-ELIF-ELSE YAPISI)
    # Burada tek tek kontrol ediyoruz ki hata payı kalmasın
    if raw_label == "mutlu" or raw_label == "joy" or raw_label == "label_0":
        mapped_label = "joy"
        print("SİSTEM NOTU: Mutluluk (Joy) tespit edildi.")
    elif raw_label == "üzgün" or raw_label == "sadness" or raw_label == "label_1":
        mapped_label = "sadness"
        print("SİSTEM NOTU: Üzüntü (Sadness) tespit edildi.")
    elif raw_label == "kızgın" or raw_label == "anger" or raw_label == "label_2":
        mapped_label = "anger"
        print("SİSTEM NOTU: Öfke (Anger) tespit edildi.")
    elif raw_label == "korkmuş" or raw_label == "fear" or raw_label == "label_3":
        mapped_label = "fear"
        print("SİSTEM NOTU: Korku (Fear) tespit edildi.")
    elif raw_label == "sevgi" or raw_label == "love" or raw_label == "label_4":
        mapped_label = "love"
        print("SİSTEM NOTU: Sevgi (Love) tespit edildi.")
    else:
        mapped_label = "neutral"
        print(f"SİSTEM NOTU: Tanımlanamayan etiket ('{raw_label}'), Nötr'e düşüldü.")

    # 4️⃣ VERİTABANINA KAYDEDİLECEK TÜRKÇE DUYGU ADI (IF-ELIF-ELSE)
    if mapped_label == "joy":
        detected_feeling = "Mutlu"
    elif mapped_label == "sadness":
        detected_feeling = "Üzgün"
    elif mapped_label == "anger":
        detected_feeling = "Kızgın"
    elif mapped_label == "fear":
        detected_feeling = "Korkmuş"
    elif mapped_label == "love":
        detected_feeling = "Sevgi Dolu"
    else:
        detected_feeling = "Nötr"

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

    # 6️⃣ MOTİVASYON MESAJI ÜRET (IF-ELIF-ELSE İLE GARANTİYE ALMA)
    # Burada direkt mapped_label üzerinden JSON listesini çekiyoruz
    if mapped_label == "joy":
        category_list = motivation_messages.get("joy")
    elif mapped_label == "sadness":
        category_list = motivation_messages.get("sadness")
    elif mapped_label == "anger":
        category_list = motivation_messages.get("anger")
    elif mapped_label == "fear":
        category_list = motivation_messages.get("fear")
    elif mapped_label == "love":
        category_list = motivation_messages.get("love")
    else:
        category_list = motivation_messages.get("neutral")

    # Eğer bir şekilde category_list boş gelirse (JSON hatası vs.)
    if not category_list:
        print("KRİTİK HATA: JSON kategorisi bulunamadı!")
        category_list = motivation_messages["neutral"]

    random_motivation = random.choice(category_list)

    print(f"SEÇİLEN KATEGORİ: {mapped_label}")
    print(f"SEÇİLEN MESAJ: {random_motivation}")
    print("==================================================\n")

    message = (
        f"{random_motivation} Dün {entry.habits.pages_read} sayfa kitap okudun "
        f"ve {entry.habits.coding_hours} saat kod yazdın. Harika gidiyorsun!"
    )

    activity = "Bugün hava güneşli, belki parkta biraz yürüyüş yapıp podcast dinleyebilirsin."

    return MotivationResponse(
        message=message,
        suggested_activity=activity
    )
