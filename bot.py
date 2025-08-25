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

    bot.reply_to(message, "Привет! Отправь мне ссылку на видео из TikTok, и я скачаю его без водяного знака!")



@bot.message_handler(func=lambda message: True)

def handle_message(message):

    url = message.text

    if 'tiktok.com' in url:

        try:

            msg = bot.reply_to(message, " Скачиваю видео...")



            # Пробуем скачать видео

            success = download_and_send_video(url, message.chat.id)



            if success:

                bot.delete_message(msg.chat.id, msg.message_id)

            else:

                bot.delete_message(msg.chat.id, msg.message_id)

                bot.reply_to(message, " Не удалось скачать видео. Попробуйте другую ссылку.")



        except Exception as e:

            bot.reply_to(message, f" Ошибка: {str(e)}")

    else:

        bot.reply_to(message, " Это не ссылка TikTok")



def download_and_send_video(tiktok_url, chat_id):

    """Пробуем скачать видео разными методами"""

    try:

        # Метод 1: Через мобильные заголовки

        headers = {

            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15',

            'Accept': 'video/mp4,video/*;q=0.9',

            'Referer': 'https://www.tiktok.com/',

            'Origin': 'https://www.tiktok.com'

        }



        # Получаем конечную ссылку

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



                # Проверяем что файл не пустой

                if os.path.getsize(tmp_file.name) > 1024:

                    # Отправляем видео

                    with open(tmp_file.name, 'rb') as video_file:

                        bot.send_video(chat_id, video_file, caption=" Вот ваше видео без водяного знака!")



                    os.remove(tmp_file.name)

                    return True



        # Метод 2: Если первый не сработал

        return try_alternative_method(tiktok_url, chat_id)



    except Exception as e:

        print(f"Download error: {e}")

        return False



def try_alternative_method(tiktok_url, chat_id):

    """Альтернативный метод через API"""

    try:

        # Пробуем разные API

        apis = [

            f"https://api.tikwm.com/api/?url={tiktok_url}",

            f"https://www.tiktokdownloadr.com/api?url={tiktok_url}"

        ]



        for api_url in apis:

            try:

                response = requests.get(api_url, timeout=10)

                if response.status_code == 200:

                    data = response.json()

                    video_url = data.get('data', {}).get('play') or data.get('video_url')



                    if video_url:

                        # Скачиваем по полученной ссылке

                        video_response = requests.get(video_url, stream=True, timeout=20)

                        if video_response.status_code == 200:

                            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:

                                for chunk in video_response.iter_content(chunk_size=8192):

                                    tmp_file.write(chunk)



                                with open(tmp_file.name, 'rb') as video_file:

                                    bot.send_video(chat_id, video_file, caption=" Вот ваше видео!")



                                os.remove(tmp_file.name)

                                return True

            except:

                continue



    except Exception as e:

        print(f"Alternative method error: {e}")



    return False



def run_bot():

    """Запуск бота с обработкой ошибок"""

    while True:

        try:

            bot.polling(none_stop=True, timeout=60)

        except Exception as e:

            print(f"Bot error: {e}")

            import time

            time.sleep(10)



if __name__ == '__main__':

    import threading

    # Запускаем бот в отдельном потоке

    bot_thread = threading.Thread(target=run_bot)

    bot_thread.daemon = True

    bot_thread.start()



    # Запускаем Flask

    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))








