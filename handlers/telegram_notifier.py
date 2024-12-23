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

if not TG_BOT_TOKEN or not TG_CHANNEL_ID:
    logger.error("TG_BOT_TOKEN или TG_CHANNEL_ID не указаны в .env файле")
    raise ValueError("TG_BOT_TOKEN и TG_CHANNEL_ID должны быть определены")

if not PAGE_ACCESS_TOKEN:
    logger.error("PAGE_ACCESS_TOKEN не указан в .env файле")
    raise ValueError("PAGE_ACCESS_TOKEN должен быть определён")


def get_user_name(user_id):
    """Получение Имени и Фамилии пользователя из Facebook Messenger."""
    url = f"https://graph.facebook.com/{user_id}"
    params = {
        'fields': 'first_name,last_name',
        'access_token': PAGE_ACCESS_TOKEN
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        first_name = data.get("first_name", "Неизвестно")
        last_name = data.get("last_name", "Неизвестно")
        return f"{first_name} {last_name}"
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при получении имени пользователя: {e}")
        return "Неизвестный пользователь"


def send_telegram_notification_to_channel(user_id, message_text):
    """Отправляет уведомление в Telegram канал."""
    try:
        user_name = get_user_name(user_id)
        text = f"Новое сообщение от пользователя {user_name}:\n{message_text}"
        url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        data = {
            'chat_id': TG_CHANNEL_ID,
            'text': text
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            logger.info("Уведомление в Telegram канал успешно отправлено")
        else:
            logger.error(f"Ошибка при отправке уведомления: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления в Telegram: {e}")
