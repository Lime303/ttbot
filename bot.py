import os
import requests
import telebot
from flask import Flask
import threading
import time

app = Flask(__name__)
API_TOKEN = os.environ['TELEGRAM_TOKEN'].strip()
bot = telebot.TeleBot(API_TOKEN)

# Флаг для отслеживания состояния бота
bot_running = False

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/ping')
def ping():
    return "Pong! Bot is alive"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку на видео из TikTok!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if 'tiktok.com' in url:
        bot.reply_to(message, " Видео получено! Обрабатываю...")
    else:
        bot.reply_to(message, " Отправьте ссылку TikTok")

def keep_alive():
    """Постоянный пинг чтобы Render не засыпал"""
    while True:
        try:
            requests.get("https://your-render-app.onrender.com/ping", timeout=5)
            print("Ping sent to keep alive")
        except:
            print("Ping failed")
        time.sleep(300)  # Пинг каждые 5 минут

def run_bot():
    """Запуск бота с перезапуском при падении"""
    global bot_running
    while True:
        try:
            if not bot_running:
                print("Starting bot polling...")
                bot_running = True
                bot.polling(none_stop=True, timeout=60)
            else:
                time.sleep(10)
        except Exception as e:
            print(f"Bot crashed: {e}")
            bot_running = False
            time.sleep(10)
            print("Restarting bot...")

if __name __ == '__main__':
    # Запускаем бот в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем пинг в отдельном потоке
    ping_thread = threading.Thread(target=keep_alive, daemon=True)
    ping_thread.start()
    
    # Запускаем Flask
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
