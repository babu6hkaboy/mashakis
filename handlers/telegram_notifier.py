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

# Набор ключевых слов для проверки
KEYWORDS = set([
    "Please", "give", "minutes", "pass", "information", "manager", "thank", "beautiful", 
])

# Минимальное количество совпадений для отправки уведомления
MIN_MATCH_COUNT = 5

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

def should_notify(response_text):
    """Проверка, стоит ли отправлять уведомление в Telegram."""
    # Преобразуем текст ответа и ключевые слова в множества
    response_words = set(response_text.lower().split())
    # Считаем пересечение с ключевыми словами
    match_count = len(response_words & KEYWORDS)
    logger.info(f"Совпадение ключевых слов: {match_count} (необходимо: {MIN_MATCH_COUNT})")
    return match_count >= MIN_MATCH_COUNT

def send_telegram_notification_to_channel(user_id, message_text):
    """Отправка уведомления о новом сообщении в Telegram канал."""
    user_name = get_user_name(user_id)  # Получаем Имя и Фамилию
    text = f"Новое сообщение от пользователя {user_name}:\n{message_text}"
    
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TG_CHANNEL_ID,
        'text': text
    }

    logger.info(f"Отправка уведомления в Telegram канал с данными: {data}")

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        logger.info("Telegram notification sent to channel successfully")
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при отправке уведомления в Telegram: {e}")
