import json
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# మీ API Keys
GEMINI_API_KEY = "AQ.Ab8RN6Jp-pCkpJwSELBgRyA4zDtMMdprM6HkkBij5_GJe4LnKA"
TELEGRAM_BOT_TOKEN = "8488523290:AAHpuufgz_aROs_FmGowM7TOzbnAo_AUZ3E"

SYSTEM_INSTRUCTION = """
నువ్వు తెలంగాణ రెవెన్యూ చట్టాలు (RoR Act, సాదా బైనామా, వారసత్వ బదిలీ/Succession, భూమి కొలతలు, రికార్డుల సవరణ మొదలైనవి) తెలిసిన లీగల్ అసిస్టెంట్‌వి.
సూచనలు:
1. యూజర్ తన సమస్యను చెప్పినప్పుడు, దానికి సంబంధించిన చట్టబద్ధమైన పరిష్కారాన్ని సులభమైన తెలుగులో వివరించు.
2. సంబంధిత ఫారాలు, ధరణి పోర్టల్ ప్రాసెస్, అవసరమైన పత్రాల వివరాలు అందించు.
"""

def get_gemini_response(prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [{"text": f"{SYSTEM_INSTRUCTION}\n\nయూజర్ ప్రశ్న: {prompt}"}]
            }
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    
    if response.status_code == 200:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    else:
        return f"API Error: {data.get('error', {}).get('message', 'సమస్య ఎదురైంది')}"

# 1. Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = "నమస్కారం! నేను మీ తెలంగాణ రెవెన్యూ చట్టాల అసిస్టెంట్‌ని. మీ సమస్యను ఇక్కడ అడగండి."
    await update.message.reply_text(welcome_text)

# 2. Message Handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    try:
        reply_text = get_gemini_response(user_text)
        await update.message.reply_text(reply_text)
    except Exception as e:
        await update.message.reply_text(f"సమస్య ఎదురైంది: {e}")

# 3. Main Function
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
