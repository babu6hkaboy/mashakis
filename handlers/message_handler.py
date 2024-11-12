import requests
from config import PAGE_ACCESS_TOKEN
from handlers.gpt_handler import generate_response
from handlers.telegram_notifier import send_telegram_notification
from handlers.database import save_client_message
from utils.logger import logger

def handle_message(data):
    # Извлечение информации из входящего сообщения
    messaging_events = data['entry'][0]['messaging']
    for event in messaging_events:
        if 'message' in event:
            sender_id = event['sender']['id']
            message_text = event['message'].get('text')

            if message_text:
                logger.info(f"Message from {sender_id}: {message_text}")

                # Сохранение сообщения в базе данных
                save_client_message(sender_id, message_text)

                # Генерация ответа с помощью ChatGPT
                bot_response = generate_response(sender_id, message_text)

                # Отправка ответа клиенту
                send_message(sender_id, bot_response)
            else:
                # Обработка других типов сообщений (например, вложений)
                send_message(sender_id, "Извините, я могу обрабатывать только текстовые сообщения.")

def send_message(recipient_id, message_text):
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
        'https://graph.facebook.com/v11.0/me/messages',
        params=params,
        headers=headers,
        json=data
    )
    if response.status_code != 200:
        logger.error(f"Failed to send message: {response.text}")
    else:
        logger.info(f"Sent message to {recipient_id}")
