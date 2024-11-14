import requests
from handlers.gpt_handler import generate_response
from handlers.telegram_notifier import send_telegram_notification_to_channel
from handlers.database import save_client_message
from utils.logger import logger

# Укажите Page Access Token напрямую
PAGE_ACCESS_TOKEN = "EAANHNDy9q1IBO56pyfTAboXhL8SwcFQpi5NhitfPckvkInLpKU8lbbe0q8R3PSmRp8FIabOKlQe1euPnwJNLGGAKj7sZAdyFBFZAEsrm9ZCBkm6olaALHLh6jhWjfeetAZBI7gQEC7e0oqLznwkZCMY1IQ6pHzSZA3ZABZCGNqnjH18k72LGF6QRMPGUkrp8P2yn"

def handle_message(data):
    """Обрабатывает входящее сообщение от Messenger"""
    logger.info("Начало обработки сообщения...")  # Логирование начала обработки
    # Извлечение информации из входящего сообщения
    messaging_events = data['entry'][0]['messaging']
    for event in messaging_events:
        if 'message' in event:
            sender_id = event['sender']['id']
            message_text = event['message'].get('text')

            if message_text:
                logger.info(f"Сообщение от {sender_id}: {message_text}")

                # Сохранение сообщения клиента в базе данных
                save_client_message(sender_id, message_text)
                logger.info(f"Сообщение от {sender_id} сохранено в базе данных.")

                # Генерация ответа ассистента с помощью ChatGPT
                bot_response = generate_response(message_text)
                logger.info(f"Сгенерированный ответ ассистента: {bot_response}")

                # Отправка ответа клиенту
                response_data = send_message(sender_id, bot_response)
                logger.info(f"Ответ от Facebook API: {response_data}")

                # Проверка наличия триггерной фразы в ответе ассистента
                trigger_phrase = "I will pass the information to the manager and she will come back to you as soon as possible"
                if trigger_phrase in bot_response:
                    # Клиент нецелевой, отправляем уведомление в Telegram-канал
                    logger.info(f"Триггерная фраза найдена, отправка уведомления в Telegram для {sender_id}")
                    send_telegram_notification_to_channel(sender_id, message_text)
            else:
                # Обработка не текстовых сообщений
                logger.warning(f"Не текстовое сообщение от {sender_id}")
                send_message(sender_id, "Извините, я могу обрабатывать только текстовые сообщения.")

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
