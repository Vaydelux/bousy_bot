import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# === ENV CONFIG ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MODEL_NAME = "gemini-1.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"

# === Gemini Function ===
async def ask_gemini(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}

    system_instruction = (
        "You are a helpful AI tutor for LET review students. "
        "Auto-detect the language (Filipino or English). "
        "Translate the answer to the same language. "
        "Start your reply with 1 appropriate emoji. "
        "Be concise, friendly, and easy to understand."
    )

    payload = {
        "contents": [
            {"role": "user", "parts": [{"text": system_instruction}]},
            {"role": "user", "parts": [{"text": prompt}]}
        ]
    }

    try:
        res = requests.post(GEMINI_URL, headers=headers, json=payload)
        res.raise_for_status()
        return res.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("Gemini Error:", e)
        return f"⚠️ Gemini Error: {e}"

# === Telegram Bot Handler ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # In group, only respond if bot is mentioned
    if message.chat.type in ["group", "supergroup"]:
        bot_username = context.bot.username.lower()
        if f"@{bot_username}" not in message.text.lower():
            return

    user_input = message.text
    print("User:", user_input)

    response = await ask_gemini(user_input)
    print("Bot:", response)

    await message.reply_text(response)

# === Main App ===
if __name__ == "__main__":
    print("🚀 Bot started on Railway")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
