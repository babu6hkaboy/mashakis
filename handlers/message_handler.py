import requests
from handlers.telegram_notifier import send_telegram_notification_to_channel
from handlers.database import save_client_message, get_client_messages
from utils.logger import logger
from handlers.gpt_handler import chat_with_assistant_sync
import asyncio

# Укажите Page Access Token напрямую
PAGE_ACCESS_TOKEN = "EAANHNDy9q1IBO56pyfTAboXhL8SwcFQpi5NhitfPckvkInLpKU8lbbe0q8R3PSmRp8FIabOKlQe1euPnwJNLGGAKj7sZAdyFBFZAEsrm9ZCBkm6olaALHLh6jhWjfeetAZBI7gQEC7e0oqLznwkZCMY1IQ6pHzSZA3ZABZCGNqnjH18k72LGF6QRMPGUkrp8P2yn"



def handle_message(data):
    try:
        entry = data['entry'][0]
        messaging = entry['messaging'][0]

        sender_id = messaging['sender']['id']
        message_text = messaging['message']['text']

        logger.info(f"Сообщение от {sender_id}: {message_text}")

        # Генерация ответа
        bot_response = chat_with_assistant_sync(sender_id, message_text)  # Синхронная версия
        logger.info(f"Ответ ассистента: {bot_response}")

        # Отправка сообщения клиенту
        send_message(sender_id, bot_response)
    except Exception as e:
        logger.error(f"Ошибка в handle_message: {e}")

    

def send_message(recipient_id, message_text):
    """Отправляет сообщение клиенту через Messenger API"""
    logger.info(f"Подготовка к отправке сообщения клиенту {recipient_id}")
    params = {
        'access_token': PAGE_ACCESS_TOKEN
    }
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        'recipient': {'id': recipient_id},
        'message': {'text': message_text}
    }
    try:
        response = requests.post(
            'https://graph.facebook.com/v16.0/me/messages',
            params=params,
            headers=headers,
            json=data
        )
        logger.info(f"Запрос к Facebook API: {response.url}")
        logger.info(f"Данные запроса: {data}")
        logger.info(f"Ответ Facebook API: {response.status_code} - {response.text}")
        if response.status_code != 200:
            logger.error(f"Ошибка при отправке сообщения: {response.text}")
        else:
            logger.info(f"Сообщение успешно отправлено клиенту {recipient_id}")
    except Exception as e:
        logger.error(f"Исключение при отправке сообщения: {e}")
    return response.json() if response.status_code == 200 else {"error": response.text}

