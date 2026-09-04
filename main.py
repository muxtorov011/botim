# -*- coding: utf-8 -*-
import telebot
from telebot import types
import os
import threading
from flask import Flask

app = Flask(__name__)

# ====== SOZLAMALAR ======
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8949249150:AAExkt42L6uSHrGnDeU53ygEMUPjfGcn41o')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '6926482253'))

bot = telebot.TeleBot(BOT_TOKEN)

# Foydalanuvchi ma'lumotlarini saqlash
user_data = {}

print("🤖 Bot ishga tushmoqda...")
print("=========================")

@app.route('/')
def home():
    return "Bot ishlamoqda!"

# /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "👑 Salom, xo'jayin! Bot ishga tayyor.")
    else:
        bot.send_message(message.chat.id, "👋 Assalomu alaykum! Savolingizni yozing, u @oxrnn ga yuboriladi.")
        bot.send_message(message.chat.id, "👋 Здравствуйте! Напишите ваш вопрос, он будет отправлен @oxrnn.")

# Foydalanuvchi xabarlarini adminga yuborish
@bot.message_handler(func=lambda message: message.from_user.id != ADMIN_ID and message.text not in ['📝 Savolingizni yozing', '📝 Напишите ваш вопрос'])
def forward_to_admin(message):
    try:
        # Foydalanuvchi ID'sini saqlash
        user_data[message.from_user.id] = {
            'username': message.from_user.username or "Username yo'q",
            'first_name': message.from_user.first_name or ""
        }
        
        # "Javob berish" tugmasi
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(
            "✍️ Javob berish", 
            callback_data=f"reply_{message.from_user.id}"
        )
        markup.add(btn)
        
        # Adminga yuborish (Faqat O'zbekcha)
        username = message.from_user.username or "Username yo'q"
        first_name = message.from_user.first_name or ""
        
        bot.send_message(
            ADMIN_ID,
            f"📩 YANGI XABAR\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👤 Ism: {first_name}\n"
            f"👤 Username: @{username}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💬 Xabar:\n{message.text}",
            reply_markup=markup
        )
        
        # Foydalanuvchiga javob
        bot.send_message(message.chat.id, "✅ Xabaringiz yuborildi!")
        bot.send_message(message.chat.id, "✅ Сообщение отправлено!")
    except Exception as e:
        print(f"Xato: {e}")
        bot.send_message(ADMIN_ID, f"❌ Xato: {e}")

# "Javob berish" tugmasi bosilganda
@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def ask_reply(call):
    try:
        user_id = call.data.split('_')[1]
        
        # Javob berish holatini saqlash
        user_data['admin_reply_to'] = user_id
        
        # "Bekor qilish" tugmasi
        markup = types.InlineKeyboardMarkup()
        cancel_btn = types.InlineKeyboardButton(
            "❌ Bekor qilish", 
            callback_data="cancel_reply"
        )
        markup.add(cancel_btn)
        
        # Admin xabarini tahrirlash
        bot.edit_message_text(
            f"📩 YANGI XABAR\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🆔 ID: {user_id}\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"✍️ Javob yozing:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
        
        # Adminga xabar
        bot.send_message(
            call.message.chat.id,
            f"✍️ {user_id} foydalanuvchiga javob yozing:"
        )
        
    except Exception as e:
        print(f"Xato: {e}")
        bot.send_message(ADMIN_ID, f"❌ Xato: {e}")

# Javobni bekor qilish
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

# Admin javobini qayta ishlash
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and 'admin_reply_to' in user_data)
def process_reply(message):
    try:
        user_id = user_data['admin_reply_to']
        
        # Foydalanuvchiga javob yuborish
        bot.send_message(
            int(user_id),
            f"📨 Admin javobi:\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{message.text}"
        )
        
        # Adminga tasdiqlash
        bot.send_message(message.chat.id, "✅ Javob yuborildi!")
        
        # Holatni tozalash
        del user_data['admin_reply_to']
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Yuborib bo'lmadi: {e}")
        del user_data['admin_reply_to']

# /help komandasi
@bot.message_handler(commands=['help'])
def help_command(message):
    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "📋 MAVJUD KOMANDALAR:\n"
            "/start - Botni tekshirish\n"
            "/help - Bu xabar\n\n"
            "💡 Odamlar botga yozadi — siz bu yerga olasiz."
        )
    else:
        bot.send_message(message.chat.id, "📝 Savolingizni yozing")
        bot.send_message(message.chat.id, "📝 Напишите ваш вопрос")

# Botni ishga tushirish
if __name__ == '__main__':
    print("✅ Bot muvaffaqiyatli ishga tushdi!")
    
    # Botni alohida thread'da ishga tushirish
    threading.Thread(target=bot.polling, kwargs={'none_stop': True}).start()
    
    # Web serverni ishga tushirish
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)