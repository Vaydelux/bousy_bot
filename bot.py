import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# === ENV CONFIG ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
MODEL_NAME = "gemini-1.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/{MODEL_NAME}:generateContent?key={GEMINI_API_KEY}"

# === Chat memory: (chat_id, user_id) → (last_user_msg, last_bot_reply)
chat_memory = {}

# === Gemini Query Function ===
async def ask_gemini(chat_id: int, user_id: int, prompt: str) -> str:
    headers = {"Content-Type": "application/json"}

    system_instruction = (
        "You are a helpful AI tutor for LET review students. "
        "Auto-detect the language (Filipino or English). "
        "Translate the answer to the same language. "
        "Start your reply with 1 appropriate emoji. "
        "Be concise, friendly, and easy to understand."
        "You don't use bold italic or anything just plain text"
    )

    # Build conversation context
    context = [{"role": "user", "parts": [{"text": system_instruction}]}]

    key = (chat_id, user_id)
    if key in chat_memory:
        last_user, last_bot = chat_memory[key]
        context.append({"role": "user", "parts": [{"text": last_user}]})
        context.append({"role": "model", "parts": [{"text": last_bot}]})

    context.append({"role": "user", "parts": [{"text": prompt}]})
    payload = {"contents": context}

    try:
        res = requests.post(GEMINI_URL, headers=headers, json=payload)
        res.raise_for_status()
        reply = res.json()["candidates"][0]["content"]["parts"][0]["text"]

        # Update chat memory
        chat_memory[key] = (prompt, reply)
        return reply
    except Exception as e:
        print("Gemini API error:", e)
        return f"⚠️ Gemini Error: {e}"

# === Telegram Message Handler ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    user_input = message.text

    # In group: only respond if bot is mentioned
    if message.chat.type in ["group", "supergroup"]:
        bot_username = context.bot.username.lower()
        if f"@{bot_username}" not in user_input.lower():
            return

    print(f"[{chat_id}] User {user_id} asked: {user_input}")
    response = await ask_gemini(chat_id, user_id, user_input)
    await message.reply_text(response)

# === Start Bot ===
if __name__ == "__main__":
    print("🚀 Gemini Telegram Bot with Memory is running...")
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
