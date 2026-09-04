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

print("🤖 Bot ishga tushmoqda...")
print("=========================")

@app.route('/')
def home():
    return "Bot ishlamoqda!"

# /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(
            message,
            "👑 Salom, xo'jayin! Bot ishga tayyor.\n"
            "👑 Здравствуйте, хозяин! Бот готов к работе."
        )
    else:
        bot.reply_to(
            message,
            "👋 Assalomu alaykum! Savolingizni yozing, u @oxrnn ga yuboriladi.\n"
            "👋 Здравствуйте! Напишите ваш вопрос, он будет отправлен @oxrnn."
        )

# Foydalanuvchi xabarlarini adminga yuborish
@bot.message_handler(func=lambda message: message.from_user.id != ADMIN_ID)
def forward_to_admin(message):
    try:
        # "Javob berish" tugmasi
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(
            "✍️ Javob berish / Ответить", 
            callback_data=f"reply_{message.from_user.id}"
        )
        markup.add(btn)
        
        # Adminga yuborish
        username = message.from_user.username or "Username yo'q / Нет username"
        bot.send_message(
            ADMIN_ID,
            f"📩 YANGI XABAR / НОВОЕ СООБЩЕНИЕ\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👤 Kimdan / От: @{username}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💬 Xabar / Сообщение:\n{message.text}",
            reply_markup=markup
        )
        
        # Foydalanuvchiga javob
        bot.reply_to(
            message,
            "✅ Xabaringiz yuborildi!\n"
            "✅ Сообщение отправлено!"
        )
    except Exception as e:
        print(f"Xato: {e}")

# "Javob berish" tugmasi bosilganda
@bot.callback_query_handler(func=lambda call: call.data.startswith('reply_'))
def ask_reply(call):
    try:
        user_id = call.data.split('_')[1]
        
        # "Bekor qilish" tugmasi
        markup = types.InlineKeyboardMarkup()
        cancel_btn = types.InlineKeyboardButton(
            "❌ Bekor qilish / Отмена", 
            callback_data="cancel_reply"
        )
        markup.add(cancel_btn)
        
        msg = bot.send_message(
            call.message.chat.id,
            f"✍️ {user_id} foydalanuvchiga javob yozing / Напишите ответ:",
            reply_markup=markup
        )
        
        # Javobni kutish
        bot.register_next_step_handler(msg, process_reply, user_id)
    except Exception as e:
        print(f"Xato: {e}")

# Javobni bekor qilish
@bot.callback_query_handler(func=lambda call: call.data == "cancel_reply")
def cancel_reply(call):
    bot.edit_message_text(
        "❌ Javob yozish bekor qilindi / Ответ отменён",
        call.message.chat.id,
        call.message.message_id
    )

# Foydalanuvchiga javob yuborish
def process_reply(message, user_id):
    try:
        bot.send_message(
            user_id,
            f"📨  javob / Ответ:\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{message.text}"
        )
        bot.reply_to(
            message,
            "✅ Javob yuborildi!\n"
            "✅ Ответ отправлен!"
        )
    except Exception as e:
        bot.reply_to(
            message,
            f"❌ Yuborib bo'lmadi / Ошибка: {e}"
        )

# /help komandasi
@bot.message_handler(commands=['help'])
def help_command(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(
            message,
            "📋 MAVJUD KOMANDALAR / КОМАНДЫ:\n"
            "/start - Botni tekshirish / Проверить бота\n"
            "/help - Bu xabar / Это сообщение\n\n"
            "💡 Odamlar botga yozadi — siz bu yerga olasiz.\n"
            "💡 Люди пишут боту — вы получаете сюда."
        )
    else:
        bot.reply_to(
            message,
            "📝 Savolingizni yozing / Напишите ваш вопрос"
        )

# Botni ishga tushirish
if __name__ == '__main__':
    print("✅ Bot muvaffaqiyatli ishga tushdi!")
    
    # Botni alohida thread'da ishga tushirish
    threading.Thread(target=bot.polling, kwargs={'none_stop': True}).start()
    
    # Web serverni ishga tushirish
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)