import os
import requests
import telebot
from flask import Flask
from urllib.parse import quote
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
            processing_msg = bot.reply_to(message, "⏳ Скачиваю видео...")
            
            # Скачиваем видео на сервер и отправляем файлом
            video_path = download_and_save_video(url)
            
            if video_path:
                with open(video_path, 'rb') as video_file:
                    bot.delete_message(processing_msg.chat.id, processing_msg.message_id)
                    bot.send_video(message.chat.id, video_file, caption="✅ Вот ваше видео!")
                # Удаляем временный файл
                os.remove(video_path)
            else:
                bot.delete_message(processing_msg.chat.id, processing_msg.message_id)
                bot.reply_to(message, "❌ Не удалось скачать видео")
                
        except Exception as e:
            bot.reply_to(message, f"⚠️ Ошибка: {str(e)}")
    else:
        bot.reply_to(message, "📛 Отправьте ссылку TikTok")

def download_and_save_video(tiktok_url):
    """Скачиваем видео на сервер и возвращаем путь к файлу"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15',
            'Referer': 'https://www.tiktok.com/'
        }
        
        # Получаем конечную ссылку после редиректов
        response = requests.get(tiktok_url, headers=headers, timeout=15, allow_redirects=True)
        final_url = response.url
        
        # Скачиваем видео
        video_response = requests.get(final_url, headers=headers, timeout=30, stream=True)
        
        if video_response.status_code == 200:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                for chunk in video_response.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
                return tmp_file.name
                
    except Exception as e:
        print(f"Ошибка скачивания: {e}")
    
    return None

def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    import threading
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
