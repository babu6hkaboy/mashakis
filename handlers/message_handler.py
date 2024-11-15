import requests
from handlers.gpt_handler import chat_with_assistant
from handlers.telegram_notifier import send_telegram_notification_to_channel
from handlers.database import save_client_message
from utils.logger import logger
from handlers.gpt_handler import chat_with_assistant
from database import save_client_message
import asyncio

# Укажите Page Access Token напрямую
PAGE_ACCESS_TOKEN = "EAANHNDy9q1IBO56pyfTAboXhL8SwcFQpi5NhitfPckvkInLpKU8lbbe0q8R3PSmRp8FIabOKlQe1euPnwJNLGGAKj7sZAdyFBFZAEsrm9ZCBkm6olaALHLh6jhWjfeetAZBI7gQEC7e0oqLznwkZCMY1IQ6pHzSZA3ZABZCGNqnjH18k72LGF6QRMPGUkrp8P2yn"



def handle_message(data):
    try:
        for entry in data.get('entry', []):
            for messaging in entry.get('messaging', []):
                sender_id = messaging['sender']['id']
                user_message = messaging['message']['text']

                # Логируем входящее сообщение
                logger.info(f"Сообщение от {sender_id}: {user_message}")

                # Получаем ответ от ассистента
                assistant_reply = asyncio.run(chat_with_assistant(sender_id, user_message))

                # Логируем ответ ассистента
                logger.info(f"Ответ ассистента: {assistant_reply}")

                # Отправляем ответ пользователю через Messenger API
                send_message(sender_id, assistant_reply)

    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")

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
    response = requests.post(
        'https://graph.facebook.com/v16.0/me/messages',  # Убедитесь, что используется актуальная версия API
        params=params,
        headers=headers,
        json=data
    )
    logger.info(f"Отправка сообщения с данными: {data}")  # Отладочный вывод
    if response.status_code != 200:
        logger.error(f"Не удалось отправить сообщение: {response.status_code} - {response.text}")
    else:
        logger.info(f"Сообщение отправлено клиенту {recipient_id} успешно")
    return response.json() if response.status_code == 200 else {"error": response.text}
