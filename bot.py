import time
import telebot
import google.generativeai as genai

# Token និង API Key របស់អ្នក
TELEGRAM_TOKEN = "8712045754:AAFqrOF86IRBGBoW6846QsjjEXIRXV85koI"
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

if __name__ == "__main__":
    print("Cloud Bot is running...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"Reconnecting: {e}")
            time.sleep(5)
