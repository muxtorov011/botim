# -*- coding: utf-8 -*-
import telebot
from telebot import types

# ====== SOZLAMALAR ======
BOT_TOKEN = "8949249150:AAExkt42L6uSHrGnDeU53ygEMUPjfGcn41o"  # ← BotFather dan olingan token
ADMIN_ID = 6926482253  # ← O'zingizning ID raqamingiz

bot = telebot.TeleBot(BOT_TOKEN)

print("🤖 Bot ishga tushmoqda...")
print("=========================")

# /start komandasi
@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "👑 Salom, xo'jayin! Bot ishga tayyor.")
    else:
        bot.reply_to(message, "👋 Assalomu alaykum! Xabaringizni yozing, u @oxrnn ga yuboriladi.")

# Foydalanuvchi xabarlarini adminga yuborish
@bot.message_handler(func=lambda message: message.from_user.id != ADMIN_ID)
def forward_to_admin(message):
    try:
        # "Javob berish" tugmasi
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(
            "✍️ Javob berish", 
            callback_data=f"reply_{message.from_user.id}"
        )
        markup.add(btn)
        
        # Adminga yuborish
        username = message.from_user.username or "Username yo'q"
        bot.send_message(
            ADMIN_ID,
            f"📩 YANGI XABAR\n"
            f"━━━━━━━━━━━━━━━\n"
            f"👤 Kimdan: @{username}\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💬 Xabar:\n{message.text}",
            reply_markup=markup
        )
        
        # Foydalanuvchiga javob
        bot.reply_to(message, "✅ Xabaringiz yuborildi!")
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
            "❌ Bekor qilish", 
            callback_data="cancel_reply"
        )
        markup.add(cancel_btn)
        
        msg = bot.send_message(
            call.message.chat.id,
            f"✍️ {user_id} foydalanuvchiga javob yozing:",
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
        "❌ Javob yozish bekor qilindi",
        call.message.chat.id,
        call.message.message_id
    )

# Foydalanuvchiga javob yuborish
def process_reply(message, user_id):
    try:
        bot.send_message(
            user_id,
            f"📨 Admin javobi:\n"
            f"━━━━━━━━━━━━━━━\n"
            f"{message.text}"
        )
        bot.reply_to(message, "✅ Javob yuborildi!")
    except Exception as e:
        bot.reply_to(message, f"❌ Yuborib bo'lmadi: {e}")

# /help komandasi (admin uchun)
@bot.message_handler(commands=['help'])
def help_admin(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(
            message,
            "📋 MAVJUD KOMANDALAR:\n"
            "/start - Botni tekshirish\n"
            "/help - Bu xabar\n\n"
            "💡 Odamlar botga yozadi — siz bu yerga olasiz."
        )

# Botni ishga tushirish
print("✅ Bot muvaffaqiyatli ishga tushdi!")
print("To'xtatish uchun Ctrl+C bosing")
bot.polling(none_stop=True)