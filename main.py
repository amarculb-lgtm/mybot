import telebot
import requests
import json
import os
from flask import Flask
from threading import Thread

# আপনার তথ্য
BOT_TOKEN = "8618969073:AAGAduq5aK5KSxBOC_6Bv6nlVMkHnvTt5rE"
DB_URL = "https://poiuuy-85dd5-default-rtdb.firebaseio.com"
WEB_APP_URL = "https://newads18.blogspot.com/?m=1"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def get_user(uid):
    response = requests.get(f"{DB_URL}/users/{uid}.json")
    return response.json()

def update_user(uid, data):
    requests.patch(f"{DB_URL}/users/{uid}.json", data=json.dumps(data))

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    
    photos = bot.get_user_profile_photos(user_id)
    uphoto = ""
    if photos.total_count > 0:
        file_id = photos.photos[0][-1].file_id
        file_info = bot.get_file(file_id)
        uphoto = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

    args = message.text.split()
    existing_user = get_user(user_id)

    if existing_user is None:
        if len(args) > 1:
            referrer_id = args[1]
            if referrer_id != user_id:
                ref_data = get_user(referrer_id)
                if ref_data:
                    new_count = ref_data.get('refCount', 0) + 1
                    update_user(referrer_id, {"refCount": new_count})
        
        new_user_data = {
            "id": user_id,
            "uname": user_name,
            "uphoto": uphoto,
            "balance": 0,
            "refCount": 0,
            "banned": False
        }
        update_user(user_id, new_user_data)
    else:
        update_user(user_id, {"uphoto": uphoto, "uname": user_name})

    markup = telebot.types.InlineKeyboardMarkup()
    web_info = telebot.types.WebAppInfo(WEB_APP_URL)
    btn = telebot.types.InlineKeyboardButton("🚀 Open Dashboard", web_app=web_info)
    markup.add(btn)

    bot.send_message(chat_id, f"স্বাগতম {user_name}!\nনিচের বাটনে ক্লিক করে কাজ শুরু করুন।", reply_markup=markup)

def start_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    start_bot()
