import os
import time
import threading
import telebot
import google.generativeai as genai
from flask import Flask

# 1. បង្កើត Web Server តូចមួយ ដើម្បីបំពេញលក្ខខណ្ឌ Free Web Service ของ Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Telegram Bot is running smoothly!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# 2. កូដ Telegram Bot និង Gemini API
TELEGRAM_TOKEN = "8824502901:AAHQg7qz6T0Vi5wItDESeMciI1in62j0ZMA"
GEMINI_API_KEY = "AQ.Ab8RN6IUnCqBPSTUtEF1IONFYz_7tp1Rs8nGpnnDguE7vUwPZg"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3.6-flash")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True)
def chat_with_gemini(message):
    try:
        user_text = message.text
        response = model.generate_content(user_text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

def run_bot():
    print("Cloud Bot is running...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"Reconnecting: {e}")
            time.sleep(5)

# 3. ដំណើរការទាំង Web Server និង Bot ພ້ອມគ្នា
if __name__ == "__main__":
    t_web = threading.Thread(target=run_web)
    t_web.start()
    
    run_bot()
