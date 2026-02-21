function analyzeEmotion() {
    const text = document.getElementById("userInput").value;

    // 🔮 BURAYA HUGGING FACE MODELİ GELECEK
    const emotion = fakeEmotionModel(text);

    document.getElementById("emotionResult").innerText =
        "Algılanan duygu: " + emotion;

    document.getElementById("suggestionResult").innerText =
        getMotivation(emotion);

    document.getElementById("weatherSuggestion").innerText =
        getWeatherSuggestion();
}


// 🧠 GEÇİCİ MODEL
function fakeEmotionModel(text) {
    if (text.includes("mutlu")) return "Mutlu";
    if (text.includes("üzgün")) return "Üzgün";
    return "Nötr";
}


// 💬 MOTİVASYON
function getMotivation(emotion) {
    const messages = {
        "Mutlu": "Harika! Enerjini koru ✨",
        "Üzgün": "Her şey geçer, kendine nazik ol 💛",
        "Nötr": "Bugün küçük bir şeyle kendini mutlu etmeye ne dersin?"
    };

    return messages[emotion];
}


// 🌤️ BURAYA HAVA DURUMU API GELECEK
function getWeatherSuggestion() {
    return "Hava verisi yakında eklenecek ☀️";
}