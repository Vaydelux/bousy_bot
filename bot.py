import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# === CONFIG ===
GEMINI_API_KEY = "AIzaSyDNGUMPz1qw8Z_9e14pHDlWayw8bachUVE"
TELEGRAM_BOT_TOKEN = "7534508542:AAFXegnF2zFiGUVmuq9Kiu3shdYj82jnnUY"
MODEL_NAME = "gemini-1.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"

# === Gemini Query Function ===
async def ask_gemini(prompt: str) -> str:
    headers = {"Content-Type": "application/json"}

    system_instruction = (
        "You are a helpful AI tutor for LET review students. "
        "Auto-detect the language (Filipino or English) based on the question. "
        "Translate the answer to the same language. "
        "Start your reply with 1 appropriate emoji based on the topic or tone. "
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
        return f"⚠️ Gemini Error: {e}"

# === Telegram Message Handler ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    # Only respond in groups if bot is mentioned
    if message.chat.type in ["group", "supergroup"]:
        bot_username = context.bot.username.lower()
        if f"@{bot_username}" not in message.text.lower():
            return  # Ignore if bot not mentioned

    user_input = message.text
    response = await ask_gemini(user_input)
    await message.reply_text(response)

# === Main Runner ===
if __name__ == "__main__":
    print("🤖 Gemini Telegram Bot is running...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
