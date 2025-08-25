import os
import requests
import telebot
from flask import Flask
import tempfile

app = Flask(__name__)
API_TOKEN = os.environ['TELEGRAM_TOKEN'].strip()
bot = telebot.TeleBot(API_TOKEN)

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку на видео из TikTok!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if 'tiktok.com' in url:
        try:
            msg = bot.reply_to(message, "Скачиваю видео...")
            
            # Простая заглушка пока не настроим скачивание
            bot.delete_message(msg.chat.id, msg.message_id)
            bot.reply_to(message, "Видео получено! Функция скачивания настраивается.")
            
        except Exception as e:
            bot.reply_to(message, f"Ошибка: {str(e)}")
    else:
        bot.reply_to(message, "Отправьте ссылку TikTok")

def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    import threading
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
