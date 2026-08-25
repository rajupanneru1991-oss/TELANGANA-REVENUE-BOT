import logging
import os
import google.generativeai as genai
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

# Configure Gemini AI
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
నువ్వు తెలంగాణ రెవెన్యూ చట్టాలు (RoR Act, సాదా బైనామా, వారసత్వ బదిలీ/Succession, భూమి కొలతలు, రికార్డుల సవరణ) పై సమాధానాలు ఇచ్చే లీగల్ అసిస్టెంట్ బాట్వి.
సూచనలు:
1. యూజర్ తన సమస్యను చెప్పినప్పుడు, దానికి సంబంధించిన చట్టబద్ధమైన పరిష్కారాన్ని సులభమైన తెలుగులో వివరించు.
2. సంబంధిత ఫారాలు, ధరణి పోర్టల్ ప్రాసెస్, అవసరమైన పత్రాల వివరాలు అందించు.
"""

# Logging Setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

def get_gemini_response(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return "API Key లోపం: GEMINI_API_KEY ఎన్విరాన్‌మెంట్ వేరియబుల్ సెట్ కాలేదు."
    
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
        return "క్షమించండి, సమాధానం రూపొందించడంలో సమస్య ఎదురైంది."
    except Exception as e:
        return f"AI Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "నమస్కారం! 🙏\n"
        "నేను మీ తెలంగాణ రెవెన్యూ మరియు లీగల్ అసిస్టెంట్ బాట్‌ని.\n"
        "ధరణి, సాదా బైనామా, విరాసత్/వారసత్వం, భూ రికార్డులు లేదా ఇతర రెవెన్యూ సమస్యలపై మీ సందేహాన్ని అడగండి."
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
