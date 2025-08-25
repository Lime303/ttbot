import requests
import time
import os

while True:
    try:
        # Замените на ваш реальный URL Render
        url = os.environ.get('RENDER_URL', 'https://ttbot-wo14.onrender.com')
        response = requests.get(f"{url}/ping", timeout=10)
        print(f"Ping sent: {response.status_code}")
    except Exception as e:
        print(f"Ping error: {e}")
    time.sleep(240)  # Каждые 4 минуты
