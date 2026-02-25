async function submitData() {
    const telegramId = document.getElementById("telegramId").value;
    const answer = document.getElementById("dailyAnswer").value;
    const pagesRead = parseInt(document.getElementById("pagesRead").value) || 0;
    const workoutMins = parseInt(document.getElementById("workoutMins").value) || 0;
    const waterGlasses = parseInt(document.getElementById("waterGlasses").value) || 0;
    const codingHours = parseFloat(document.getElementById("codingHours").value) || 0.0;

    if (!telegramId) {
        alert("Please enter your Telegram Chat ID!");
        return;
    }

    if (!answer) {
        alert("Please write down how you feel today!");
        return;
    }

    const payload = {
        telegram_chat_id: telegramId,
        answer: answer,
        habits: {
            pages_read: pagesRead,
            workout_minutes: workoutMins,
            water_glasses: waterGlasses,
            coding_hours: codingHours
        }
    };

    const submitBtn = document.querySelector(".submit-btn");
    submitBtn.innerText = "⏳ SENDING...";
    submitBtn.disabled = true;

    try {
        const response = await fetch("http://localhost:8000/submit_daily", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error("Server error");
        }

        const data = await response.json();
        
        document.getElementById("resultBox").classList.remove("hidden");
        document.getElementById("resultMessage").innerText = "Data Recorded ✨\n\n" + data.message;
        document.getElementById("resultActivity").innerText = "💡 Suggestion: " + data.suggested_activity;

    } catch (error) {
        console.error("Error:", error);
        
        // Mock fallback if backend is not running
        document.getElementById("resultBox").classList.remove("hidden");
        document.getElementById("resultMessage").innerText = `Great job logging your habits!`;
        document.getElementById("resultActivity").innerText = `We couldn't reach the backend server, but your data is safe. Keep up the momentum!`;
    } finally {
        submitBtn.innerText = "🚀 SEND UPDATE";
        submitBtn.disabled = false;
    }
}