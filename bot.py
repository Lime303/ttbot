import os
import requests
import telebot
from flask import Flask

app = Flask(__name__)
API_TOKEN = os.environ['TELEGRAM_TOKEN'].strip()
bot = telebot.TeleBot(API_TOKEN)

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я бот для скачивания видео из TikTok. Просто отправь мне ссылку!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if 'tiktok.com' in url:
        try:
            # Просто отвечаем что получили ссылку
            bot.reply_to(message, " Ссылка получена! К сожалению, функция скачивания временно на техническом обслуживании. Попробуйте позже.")
            
            # Для отладки - посмотрим что приходит
            print(f"Получена ссылка: {url}")
            
        except Exception as e:
            bot.reply_to(message, f" Ошибка: {str(e)}")
    else:
        bot.reply_to(message, " Это не похоже на ссылку TikTok. Пример: https://vm.tiktok.com/...")

def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    import threading
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
