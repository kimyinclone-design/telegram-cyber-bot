import os
import time
import threading
import telebot
from telebot import types
from flask import Flask

import database

# 1. Web Server សម្រាប់ Render Web Service
app = Flask(__name__)

@app.route('/')
def home():
    return "Modular E-commerce Bot with Channel Auto-Post is running smoothly!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# 2. ព័ត៌មានសម្ងាត់ (Token និង Channel ID)
TELEGRAM_TOKEN = "8824502901:AAHQg7qz6T0Vi5wItDESeMciI1in62j0ZMA"
CHANNEL_ID = -1004306979832  # Channel ID របស់អ្នក

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ចាប់ផ្ដើមបង្កើត Database
database.init_db()

# រក្សាទុកស្ថានភាពអតិថិជនបណ្តោះអាសន្នពេលកំពុងជ្រើសរើសទំនិញ
user_cart = {}

# 3. មុខងារសម្រាប់ផុសទំនិញលក់ចូល Channel ស្វ័យប្រវត្ត
def post_products_to_channel():
    time.sleep(4)  # រໍាបន្តិចឱ្យ Bot ចាប់ផ្តើមរួចរាល់សិន
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_item1 = types.InlineKeyboardButton("💻 ទិញ Laptop Security Tool - $25", callback_data="buy_laptop")
    btn_item2 = types.InlineKeyboardButton("📱 ទិញ Smart Phone Accessory - $10", callback_data="buy_phone")
    markup.add(btn_item1, btn_item2)
    
    product_text = (
        "🔥 <b>ហាងអនឡាញសុវត្ថិភាពខ្ពស់ (Secure E-Commerce)</b> 🔥\n\n"
        "📦 <b>មុខទំនិញមានក្នុងស្តុក៖</b>\n"
        "1. 💻 Laptop Security Tool - តម្លៃ <b>$25</b>\n"
        "2. 📱 Smart Phone Accessory - តម្លៃ <b>$10</b>\n\n"
        "👇 សូមចុចប៊ូតុងខាងក្រោមដើម្បីជ្រើសរើសទំនិញដែលអ្នកចង់ទិញ!"
    )
    
    try:
        bot.send_message(CHANNEL_ID, product_text, reply_markup=markup, parse_mode="HTML")
        print("Product catalog posted to channel successfully!")
    except Exception as e:
        print(f"Error posting to channel: {e}")

# 4. មុខងារ /start (សម្រាប់អ្នកចុចតបជាមួយ Bot ផ្ទាល់ខ្លួន)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("🛍️ មើលទំនិញ (Products)", callback_data="view_products")
    btn2 = types.InlineKeyboardButton("📦 ប្រវត្តិការកុម្មង់របស់ខ្ញុំ", callback_data="my_orders")
    btn3 = types.InlineKeyboardButton("📞 ទំនាក់ទំនង (Contact)", callback_data="contact")
    markup.add(btn1, btn2, btn3)
    
    welcome_text = (
        f"សួស្តី! <b>{message.from_user.first_name}</b> 👋\n"
        "សូមស្វាគមន៍មកកាន់ហាងអនឡាញរបស់យើង!\n"
        "តើអ្នកចង់ធ្វើអ្វីបន្តទៀត?"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="HTML")

# 5. គ្រប់គ្រងការចុចប៊ូតុង (Inline Buttons)
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    chat_id = call.message.chat.id
    
    if call.data == "view_products":
        markup = types.InlineKeyboardMarkup(row_width=1)
        btn_item1 = types.InlineKeyboardButton("💻 Laptop Security Tool - $25", callback_data="buy_laptop")
        btn_item2 = types.InlineKeyboardButton("📱 Smart Phone Accessory - $10", callback_data="buy_phone")
        btn_back = types.InlineKeyboardButton("🔙 ថយក្រោយវិញ", callback_data="back_home")
        markup.add(btn_item1, btn_item2, btn_back)
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="📦 <b>បញ្ជីមុខទំនិញដែលមានក្នុងស្តុក៖</b>\nសូមជ្រើសរើសទំនិញដែលអ្នកចង់ទិញ៖",
            reply_markup=markup,
            parse_mode="HTML"
        )
        
    elif call.data.startswith("buy_"):
        item_name = "Laptop Security Tool" if call.data == "buy_laptop" else "Smart Phone Accessory"
        price = "$25" if call.data == "buy_laptop" else "$10"
        
        user_cart[chat_id] = {"item": item_name, "price": price}
        
        bot.answer_callback_query(call.id, f"បានជ្រើសរើស {item_name}")
        bot.send_message(
            chat_id,
            f"✅ អ្នកបានជ្រើសរើស៖ <b>{item_name}</b> ({price})\n\n"
            "សូមផ្ញើ **ឈ្មោះ លេខទូរស័ព្ទ និងទីតាំងដឹកជញ្ជូន** មកជាអត្ថបទទីនេះដើម្បីបញ្ជាក់ការកុម្មង់!",
            parse_mode="HTML"
        )
        
    elif call.data == "my_orders":
        rows = database.get_user_orders(chat_id)
        
        if rows:
            text = "📜 <b>ប្រវត្តិការកុម្មង់របស់អ្នក៖</b>\n\n"
            for row in rows:
                text += f"• {row[0]} ({row[1]}) - <i>{row[2]}</i>\n"
        else:
            text = "វាមិនទាន់មានប្រវត្តិការកុម្មង់ទំនិញនៅឡើយទេ!"
            
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔙 ថយក្រោយវិញ", callback_data="back_home"))
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        
    elif call.data == "contact":
        bot.answer_callback_query(call.id, "Contact")
        bot.send_message(chat_id, "📞 សម្រាប់ជំនួយសង្គ្រោះបន្ទាន់ សូមទាក់ទងមកកាន់ Admin ផ្ទាល់។")
        
    elif call.data == "back_home":
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton("🛍️ មើលទំនិញ (Products)", callback_data="view_products")
        btn2 = types.InlineKeyboardButton("📦 ប្រវត្តិការកុម្មង់របស់ខ្ញុំ", callback_data="my_orders")
        btn3 = types.InlineKeyboardButton("📞 ទំនាក់ទំនង (Contact)", callback_data="contact")
        markup.add(btn1, btn2, btn3)
        
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text="សួស្តី! សូមស្វាគមន៍ត្រឡប់មកកាន់ម៉ឺនុយដើមវិញ។",
            reply_markup=markup
        )

# 6. ទទួលព័ត៌មានអតិថិជន រក្សាទុក Database និងផ្ញើ Order ចូល Channel
@bot.message_handler(func=lambda message: True)
def handle_customer_info(message):
    chat_id = message.chat.id
    
    if chat_id in user_cart:
        order_info = user_cart[chat_id]
        customer_name = message.from_user.first_name
        customer_username = f"@{message.from_user.username}" if message.from_user.username else "None"
        info_text = message.text
        
        # រក្សាទុកចូល SQLite Database
        database.save_order(chat_id, customer_username, customer_name, order_info['item'], order_info['price'], info_text)
        
        # ផ្ញើព័ត៌មានកុម្មង់ចូលទៅក្នុង Channel ផ្ទាល់
        channel_order_msg = (
            f"🚨 <b>មានការបញ្ជាទិញថ្មី (New Order)!</b> 🚨\n\n"
            f"🛍️ <b>ទំនិញ:</b> {order_info['item']} ({order_info['price']})\n"
            f"👤 <b>អតិថិជន:</b> {customer_name} ({customer_username})\n"
            f"🆔 <b>User ID:</b> {chat_id}\n"
            f"📍 <b>ព័ត៌មានអតិថិជន:</b>\n{info_text}"
        )
        try:
            bot.send_message(CHANNEL_ID, channel_order_msg, parse_mode="HTML")
        except Exception as e:
            print(f"Error sending order to channel: {e}")
            
        bot.reply_to(message, "🎉 ការកុម្មង់របស់អ្នកត្រូវបានកត់ត្រាក្នុងប្រព័ន្ធដោយជោគជ័យ! យើងនឹងរៀបចំការដឹកជញ្ជូនជូន។")
        del user_cart[chat_id]
    else:
        bot.reply_to(message, "សូមចុចពាក្យ /start ដើម្បីចាប់ផ្តើមប្រើប្រាស់ហាងរបស់យើងខ្ញុំ!")

# 7. ដំណើរការ Bot និង Web Server
def run_bot():
    print("Modular Shopping Bot is running...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"Reconnecting: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # បើក Web Server សម្រាប់ Render
    t_web = threading.Thread(target=run_web)
    t_web.start()
    
    # ផុសទំនិញចូល Channel ស្វ័យប្រវត្តពេល Bot ចាប់ផ្តើម
    threading.Thread(target=post_products_to_channel).start()
    
    # ចាប់ផ្តើម Bot
    run_bot()
