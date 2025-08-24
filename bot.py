import os
import requests
import telebot
from flask import Flask
import tempfile
import re

app = Flask(__name__)
API_TOKEN = os.environ['TELEGRAM_TOKEN'].strip()
bot = telebot.TeleBot(API_TOKEN)

@app.route('/')
def home():
    return "TikTok Downloader Bot is running!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку на видео из TikTok, и я скачаю его без водяного знака.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if 'tiktok.com' in url:
        try:
            processing_msg = bot.reply_to(message, "⏳ Скачиваю видео...")
            
            # Используем рабочий API
            video_url = get_video_from_api(url)
            
            if video_url:
                # Скачиваем и отправляем видео
                success = download_and_send_video(video_url, message.chat.id)
                bot.delete_message(processing_msg.chat.id, processing_msg.message_id)
                if not success:
                    bot.reply_to(message, "❌ Ошибка при отправке видео")
            else:
                bot.delete_message(processing_msg.chat.id, processing_msg.message_id)
                bot.reply_to(message, "❌ Не удалось обработать видео")
                
        except Exception as e:
            bot.reply_to(message, f"⚠️ Ошибка: {str(e)}")
    else:
        bot.reply_to(message, "📛 Отправьте ссылку TikTok")

def get_video_from_api(tiktok_url):
    """Получаем рабочую ссылку на видео через API"""
    try:
        # Попробуем несколько рабочих API
        apis = [
            f"https://api16-normal-c-useast1a.tiktokv.com/aweme/v1/feed/?aweme_id={extract_aweme_id(tiktok_url)}",
            f"https://api.tikwm.com/api/?url={tiktok_url}",
            f"https://www.tiktokdownloadr.com/api?url={tiktok_url}"
        ]
        
        for api_url in apis:
            try:
                response = requests.get(api_url, timeout=10, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Парсим разные форматы ответов
                    video_url = (
                        data.get('aweme_list', [{}])[0].get('video', {}).get('play_addr', {}).get('url_list', [''])[0]
                        or data.get('data', {}).get('play')
                        or data.get('video_url')
                    )
                    
                    if video_url and video_url.startswith('http'):
                        return video_url
                        
            except:
                continue
                
    except Exception as e:
        print(f"API error: {e}")
    
    return None

def extract_aweme_id(url):
    """Извлекаем aweme_id из ссылки"""
    try:
        # Пробуем разные паттерны ссылок
        patterns = [
            r'/video/(\d+)',
            r'%2Fvideo%2F(\d+)',
            r'(\d{19})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
    except:
        pass
    return ""

def download_and_send_video(video_url, chat_id):
    """Скачиваем и отправляем видео"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.tiktok.com/'
        }
        
        # Скачиваем видео
        response = requests.get(video_url, headers=headers, timeout=30, stream=True)
        
        if response.status_code == 200:
            # Создаем временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
                
                # Отправляем видео
with open(tmp_file.name, 'rb') as video_file:
                    bot.send_video(chat_id, video_file, caption="✅ Вот ваше видео без водяного знака!")
                
                # Удаляем временный файл
                os.unlink(tmp_file.name)
                return True
                
    except Exception as e:
        print(f"Download error: {e}")
    
    return False

def run_bot():
    bot.polling(none_stop=True)

if name == '__main__':
    import threading
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
