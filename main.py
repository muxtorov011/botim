# -*- coding: utf-8 -*-
import telebot
from telebot import types
import os
import threading
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8949249150:AAExkt42L6uSHrGnDeU53ygEMUPjfGcn41o')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '6926482253'))

bot = telebot.TeleBot(BOT_TOKEN)

user_data = {}

print("🤖 Bot ishga tushmoqda...")

@app.route('/')
def home():
    return "Bot ishlamoqda!"

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "👑 Salom, xo'jayin! Bot ishga tayyor.")
    else:
        bot.send_message(message.chat.id, "👋 Assalomu alaykum! Savolingizni yozing, u @oxrnn ga yuboriladi.")
        bot.send_message(message.chat.id, "👋 Здравствуйте! Напишите ваш вопрос, он будет отправлен @oxrnn.")

@bot.message_handler(func=lambda message: message.from_user.id != ADMIN_ID)
def forward_to_admin(message):
    try:
        user_data[message.from_user.id] = {
            'username': message.from_user.username or "Username yo'q",
            'first_name': message.from_user.first_name or ""
        }
        
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("✍️ Javob berish", callback_data=f"reply_{message.from_user.id}")
        markup.add(btn)
        
        username = message.from_user.username or "Username yo'q"
        first_name = message.from_user.first_name or ""
        
        bot.send_message(
            ADMIN_ID,
            f"📩 Yangi xabar\n\n"
            f"👤 Ism: {first_name}\n"
            f"👤 Username: @{username}\n"
            f"🆔 ID: {message.from_user.id}\n\n"
            f"💬 Xabar:\n{message.text}",
            reply_markup=markup
        )
        
        bot.send_message(message.chat.id, "✅ Xabaringiz yuborildi!")
        bot.send_message(message.chat.id, "✅ Сообщение отправлено!")
    except Exception as e:
        print(f"Xato: {e}")
        bot.send_message(ADMIN_ID, f"❌ Xato: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def ask_reply(call):
    try:
        user_id = call.data.split('_')[1]
        user_data['admin_reply_to'] = user_id
        
        markup = types.InlineKeyboardMarkup()
        cancel_btn = types.InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel_reply")
        markup.add(cancel_btn)
        
        bot.edit_message_text(
            f"✍️ {user_id} foydalanuvchiga javob yozing:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
        
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        print(f"Xato: {e}")
        bot.send_message(ADMIN_ID, f"❌ Xato: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "cancel_reply")
def cancel_reply(call):
    if 'admin_reply_to' in user_data:
        del user_data['admin_reply_to']
    
    bot.edit_message_text(
        "❌ Javob yozish bekor qilindi",
        call.message.chat.id,
        call.message.message_id
    )
    bot.answer_callback_query(call.id, "Bekor qilindi")

@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and 'admin_reply_to' in user_data)
def process_reply(message):
    try:
        user_id = user_data['admin_reply_to']
        
        bot.send_message(
            int(user_id),
            f"📨 Admin javobi:\n\n{message.text}"
        )
        
        bot.send_message(message.chat.id, "✅ Javob yuborildi!")
        
        del user_data['admin_reply_to']
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Yuborib bo'lmadi: {e}")
        del user_data['admin_reply_to']

@bot.message_handler(commands=['help'])
def help_command(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "📋 Komandalar:\n"
            "/start - Botni tekshirish\n"
            "/help - Bu xabar\n\n"
            "💡 Odamlar botga yozadi — siz bu yerga olasiz."
        )
    else:
        bot.send_message(message.chat.id, "📝 Savolingizni yozing")
        bot.send_message(message.chat.id, "📝 Напишите ваш вопрос")

# Botni ishga tushirish
def run_bot():
    print("✅ Bot muvaffaqiyatli ishga tushdi!")
    bot.polling(none_stop=True)

# Botni alohida thread'da ishga tushirish
threading.Thread(target=run_bot).start()

# Web serverni ishga tushirish
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)