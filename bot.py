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
    return "TikTok Bot is running!"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Отправь мне ссылку на видео из TikTok!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if 'tiktok.com' in url:
        try:
            msg = bot.reply_to(message, "⏳ Скачиваю видео...")
            
            # Прямое скачивание
            success = download_and_send_direct(url, message.chat.id)
            
            if success:
                bot.delete_message(msg.chat.id, msg.message_id)
            else:
                bot.delete_message(msg.chat.id, msg.message_id)
                bot.reply_to(message, "❌ Не удалось скачать видео")
                
        except Exception as e:
            bot.reply_to(message, f"⚠️ Ошибка: {str(e)}")
    else:
        bot.reply_to(message, "📛 Отправьте ссылку TikTok")

def download_and_send_direct(tiktok_url, chat_id):
    """Прямое скачивание через мобильные заголовки"""
    try:
        # Мобильные заголовки
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15',
            'Accept': 'video/mp4,video/*;q=0.9',
            'Referer': 'https://www.tiktok.com/',
            'Origin': 'https://www.tiktok.com'
        }
        
        # Получаем конечный URL
        response = requests.get(tiktok_url, headers=headers, timeout=15, allow_redirects=True)
        final_url = response.url
        
        # Скачиваем видео
        video_response = requests.get(final_url, headers=headers, timeout=30, stream=True)
        
        if video_response.status_code == 200:
            # Сохраняем во временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                for chunk in video_response.iter_content(chunk_size=8192):
                    if chunk:
                        tmp_file.write(chunk)
                
                # Проверяем размер файла
                if os.path.getsize(tmp_file.name) > 1024:  # Не менее 1KB
                    # Отправляем видео
                    with open(tmp_file.name, 'rb') as video_file:
                        bot.send_video(chat_id, video_file, caption="✅ Вот ваше видео!")
                    
                    os.remove(tmp_file.name)
                    return True
                
        return False
        
    except Exception as e:
        print(f"Direct download error: {e}")
        return False

def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    import threading
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
