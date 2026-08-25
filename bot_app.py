import json
import logging
import os
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# API Keys (Render Environment Variables నుండి రీడ్ చేస్తుంది)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8488523290:AAHpuufgz_aROs_FmGowM7TOzbnAo_AUZ3E")

SYSTEM_INSTRUCTION = """
నువ్వు తెలంగాణ రెవెన్యూ చట్టాలు (RoR Act, సాదా బైనామా, వారసత్వ బదిలీ/Succession/విరాసత్, మ్యుటేషన్, భూమి కొలతలు, రికార్డుల సవరణ) పై సమాధానాలు ఇచ్చే లీగల్ అసిస్టెంట్ బాట్వి.
సూచనలు:
1. యూజర్ తన సమస్యను చెప్పినప్పుడు, దానికి సంబంధించిన చట్టబద్ధమైన పరిష్కారాన్ని సులభమైన తెలుగులో వివరించు.
2. సంబంధిత ఫారాలు, ధరణి పోర్టల్ ప్రాసెస్, అవసరమైన పత్రాల వివరాలు స్పష్టంగా అందించు.
"""

# Logging Setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

def get_gemini_response(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return "API Key లోపం: GEMINI_API_KEY ఎన్విరాన్‌మెంట్ వేరియబుల్ సరిగ్గా సెట్ కాలేదు."

    # అందుబాటులో ఉన్న మోడల్స్ లిస్ట్
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-1.5-flash"
    ]

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{SYSTEM_INSTRUCTION}\n\nయూజర్ ప్రశ్న: {prompt}"}
                ]
            }
        ]
    }

    last_error = ""
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response_json = response.json()

            if response.status_code == 200:
                candidates = response_json.get("candidates", [])
                if candidates:
                    return candidates[0]["content"]["parts"][0]["text"]
            else:
                last_error = response_json.get("error", {}).get("message", "Unknown error")
        except Exception as e:
            last_error = str(e)

    return f"API Error: {last_error}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "నమస్కారం! 🙏\n"
        "నేను మీ తెలంగాణ రెవెన్యూ మరియు లీగల్ అసిస్టెంట్ బాట్‌ని.\n"
        "ధరణి, మ్యుటేషన్, సాదా బైనామా, విరాసత్/వారసత్వం, భూ రికార్డులు లేదా ఇతర రెవెన్యూ సమస్యలపై మీ సందేహాన్ని అడగండి."
    )
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )
    reply = get_gemini_response(user_text)
    await update.message.reply_text(reply)

def main():
    print("Bot is running...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    app.run_polling()

if __name__ == "__main__":
    main()
