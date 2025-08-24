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
            processing_msg = bot.reply_to(message, "⏳ Обрабатываю ссылку...")

            # Получаем полную ссылку из короткой
            full_url = get_full_tiktok_url(url)
            if not full_url:
                bot.delete_message(processing_msg.chat.id, processing_msg.message_id)
                bot.reply_to(message, "❌ Неверная ссылка TikTok")
                return

            # Получаем видео через API
            video_data = get_video_from_api(full_url)

            if video_data and 'video_url' in video_data:
                # Скачиваем и отправляем видео
                success = download_and_send_video(
                    video_data['video_url'],
                    message.chat.id,
                    video_data.get('caption', 'Вот ваше видео без водяного знака! ✅')
                )
                bot.delete_message(processing_msg.chat.id, processing_msg.message_id)
                if not success:
                    bot.reply_to(message, "❌ Ошибка при отправке видео")
            else:
                bot.delete_message(processing_msg.chat.id, processing_msg.message_id)
                bot.reply_to(message, "❌ Не удалось скачать видео")

        except Exception as e:
            bot.reply_to(message, f"⚠️ Ошибка: {str(e)}")
    else:
        bot.reply_to(message, "📛 Отправьте ссылку TikTok")

def get_full_tiktok_url(short_url):
    """Преобразуем короткую ссылку в полную"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }

        # Получаем конечный URL после всех редиректов
        response = requests.get(short_url, headers=headers, timeout=10, allow_redirects=True)
        return response.url

    except:
        return None

def get_video_from_api(tiktok_url):
    """Получаем видео через TikTok API"""
    try:
        # Используем API который работает с прямыми ссылками
        api_url = f"https://api.tikwm.com/api/?url={tiktok_url}"

        response = requests.get(api_url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        })

        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                return {
                    'video_url': data['data']['play'],
                    'caption': data['data'].get('title', 'Вот ваше видео без водяного знака! ✅')
                }

        # Fallback: пробуем другой API
        api_url2 = f"https://www.tiktokdownloadr.com/api?url={tiktok_url}"
        response2 = requests.get(api_url2, timeout=10)
        if response2.status_code == 200:
            data = response2.json()
            if data.get('success'):
                return {
                    'video_url': data['video_url'],
                    'caption': 'Вот ваше видео без водяного знака! ✅'
                }

    except Exception as e:
        print(f"API error: {e}")

    return None

def download_and_send_video(video_url, chat_id, caption):
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

                # Проверяем что файл не пустой
                if os.path.getsize(tmp_file.name) > 0:
                    # Отправляем видео
                    with open(tmp_file.name, 'rb') as video_file:
                        bot.send_video(chat_id, video_file, caption=caption)

                    # Удаляем временный файл
                    os.unlink(tmp_file.name)
                    return True
                else:
                    print("Скачанный файл пустой")
                    return False

    except Exception as e:
        print(f"Download error: {e}")

    return False

def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    import threading
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
	
