import os
import requests
import re
import json
import telebot
from flask import Flask
from urllib.parse import quote

app = Flask(__name__)

# Получаем токен из переменных окружения Render
API_TOKEN = os.environ['TELEGRAM_TOKEN']
bot = telebot.TeleBot(API_TOKEN)

@app.route('/')
def home():
    return "TikTok Bot is running!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку на видео из TikTok, и я скачаю его без водяного знака.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if 'tiktok.com' in url:
        try:
            processing_msg = bot.reply_to(message, "⏳ Обрабатываю видео...")
            video_url = download_tiktok_simple(url)
            
            if video_url:
                bot.delete_message(processing_msg.chat.id, processing_msg.message_id)
                bot.send_video(message.chat.id, video_url, caption="✅ Вот ваше видео! 🎬")
            else:
                bot.delete_message(processing_msg.chat.id, processing_msg.message_id)
                bot.reply_to(message, "❌ Не удалось скачать видео. Попробуйте другую ссылку.")
                
        except Exception as e:
            bot.reply_to(message, f"⚠️ Ошибка: {str(e)}")
    else:
        bot.reply_to(message, "📛 Пожалуйста, отправьте действительную ссылку на видео TikTok.")

def download_tiktok_simple(tiktok_url):
    """Простой метод скачивания через мобильный User-Agent"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15',
            'Accept': 'video/mp4,video/*;q=0.9',
            'Referer': 'https://www.tiktok.com/',
            'Origin': 'https://www.tiktok.com'
        }
        
        response = requests.get(tiktok_url, headers=headers, timeout=15, allow_redirects=True)
        
        if 'video/mp4' in response.headers.get('content-type', ''):
            return response.url
        
        html = response.text
        patterns = [
            r'"downloadAddr":"([^"]+)"',
            r'"playAddr":"([^"]+)"', 
            r'<meta property="og:video" content="([^"]+)"',
            r'src="(https://[^"]+\.mp4)"'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                video_url = match.group(1).replace('\\u002F', '/')
                if video_url.startswith('http'):
                    return video_url
                
    except Exception as e:
        print(f"Ошибка скачивания: {e}")
    
    return None

def run_bot():
    """Запуск бота в отдельном потоке"""
    bot.polling(none_stop=True)

if name == '__main__':
    # Запускаем бот в отдельном потоке
    import threading
    threading.Thread(target=run_bot).start()
    # Запускаем Flask сервер
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
