import os
import requests
from utils.logger import logger
from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()

# Получение значений из .env
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHANNEL_ID = os.getenv("TG_CHANNEL_ID")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

def get_user_name(user_id):
    """Получение Имени и Фамилии пользователя из Facebook Messenger."""
    url = f"https://graph.facebook.com/{user_id}"
    params = {
        'fields': 'first_name,last_name',
        'access_token': PAGE_ACCESS_TOKEN
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        first_name = data.get("first_name", "Неизвестно")
        last_name = data.get("last_name", "Неизвестно")
        return f"{first_name} {last_name}"
    else:
        logger.error(f"Не удалось получить Имя и Фамилию пользователя: {response.text}")
        return "Неизвестный пользователь"

def send_telegram_notification_to_channel(user_id, message_text):
    user_name = get_user_name(user_id)  # Получаем Имя и Фамилию
    text = f"Новое сообщение от пользователя {user_name}:\n{message_text}"
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TG_CHANNEL_ID,
        'text': text
    }
    logger.info(f"Отправка уведомления в Telegram канал с данными: {data}")
    
    response = requests.post(url, json=data)
    if response.status_code != 200:
        logger.error(f"Failed to send Telegram notification to channel: {response.status_code} - {response.text}")
    else:
        logger.info("Telegram notification sent to channel successfully")
