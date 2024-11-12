import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from utils.logger import logger

def send_telegram_notification(user_id, message_text):
    text = f"Новое сообщение от пользователя {user_id}:\n{message_text}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        logger.error(f"Failed to send Telegram notification: {response.text}")
    else:
        logger.info("Telegram notification sent successfully")
