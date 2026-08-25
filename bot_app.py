import json
import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# API Keys
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

# Render Health Check Server
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def log_message(self, format, *args):
        return

def run_server():
    port = int(os.getenv("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Gemini API Function with updated stable Gemini 3.6 Flash model
def get_gemini_response(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return "API Key లోపం: GEMINI_API_KEY ఎన్విరాన్‌మెంట్ వేరియబుల్ సరిగ్గా సెట్ కాలేదు."

    # Using the latest stable gemini-3.6-flash model endpoint
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-3.6-flash:generateContent?key={GEMINI_API_KEY}"
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

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=45)
        if response.status_code == 200:
            res_json = response.json()
            candidates = res_json.get("candidates", [])
            if candidates:
                return candidates[0]["content"]["parts"][0]["text"]
            return "క్షమించండి, సమాధానం రూపొందించడంలో సమస్య ఎదురైంది."
        else:
            return f"API Error Code: {response.status_code} - {response.text[:120]}"
    except requests.exceptions.Timeout:
        return "సమాధానం ఇవ్వడానికి ఎక్కువ సమయం పట్టింది (Timeout). దయచేసి మళ్లీ ప్రయత్నించండి."
    except Exception as e:
        return f"Error: {str(e)}"

# Telegram Handlers
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
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()

    print("Telegram Bot is starting...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )

    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
