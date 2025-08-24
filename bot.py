import os
import requests
import telebot
from flask import Flask

app = Flask(__name__)

# Получаем токен из переменных окружения Railway
API_TOKEN = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку на видео из TikTok!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if 'tiktok.com' in url:
        try:
            # Ваш код для обработки TikTok ссылки
            bot.reply_to(message, "Обрабатываю видео...")
        except Exception as e:
            bot.reply_to(message, f"Ошибка: {str(e)}")
    else:
        bot.reply_to(message, "Отправьте ссылку TikTok")

if name == '__main__':
    # Запускаем бота в отдельном потоке
    import threading
    threading.Thread(target=bot.polling, kwargs={'none_stop': True}).start()
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
