import requests
from handlers.gpt_handler import chat_with_assistant, client
from handlers.telegram_notifier import send_telegram_notification_to_channel
from utils.logger import logger
import asyncio

# Укажите Page Access Token напрямую
PAGE_ACCESS_TOKEN = "token"

# Множество обработанных идентификаторов сообщений
processed_messages = set()

def handle_message(data):
    try:
        for entry in data.get('entry', []):
            for messaging in entry.get('messaging', []):
                sender_id = messaging['sender']['id']
                message_id = messaging['message']['mid']
                user_message = messaging['message'].get('text', '').strip()

                # Проверка: сообщение уже обработано
                if message_id in processed_messages:
                    logger.info(f"Сообщение {message_id} уже обработано. Пропускаем.")
                    continue

                # Добавляем сообщение в обработанные
                processed_messages.add(message_id)

                # Проверка наличия текста
                if not user_message:
                    logger.error(f"Пустое сообщение от пользователя {sender_id}. Пропускаем.")
                    continue

                # Логирование перед вызовом
                logger.info(f"Передача аргументов в chat_with_assistant: user_id={sender_id}, user_message={user_message}")

                # Передаём client в функцию
                assistant_reply = asyncio.run(chat_with_assistant(sender_id, user_message))

                # Логирование ответа ассистента
                logger.info(f"Ответ ассистента: {assistant_reply}")

                # Обработка ответа ассистента: извлечение текста из объектов
                if isinstance(assistant_reply, list):
                    assistant_reply_text = " ".join(
                        block.text.value for block in assistant_reply if hasattr(block, 'text') and hasattr(block.text, 'value')
                    )
                else:
                    assistant_reply_text = str(assistant_reply)

                # Проверяем необходимость отправки уведомления в Telegram
                if should_notify(assistant_reply_text):
                    logger.info("Обнаружены триггерные слова в ответе ассистента. Отправляем уведомление в Telegram.")
                    try:
                        send_telegram_notification_to_channel(sender_id, user_message)
                        logger.info("Уведомление в Telegram успешно отправлено.")
                    except Exception as e:
                        logger.error(f"Ошибка при отправке уведомления в Telegram: {e}")
                else:
                    logger.info("Триггерные слова в ответе ассистента не найдены. Уведомление в Telegram не отправлено.")

                # Отправка ответа клиенту
                try:
                    send_message(sender_id, assistant_reply_text)
                    logger.info(f"Ответ успешно отправлен клиенту {sender_id}.")
                except Exception as e:
                    logger.error(f"Ошибка при отправке ответа клиенту {sender_id}: {e}")
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")


def send_message(recipient_id, message_text):
    """Отправляет сообщение клиенту через Messenger API"""
    logger.info(f"Подготовка к отправке сообщения клиенту {recipient_id}")
    if not isinstance(message_text, str):
        logger.warning(f"Сообщение не является строкой, преобразуем: {type(message_text)}")
        message_text = str(message_text)

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
        'https://graph.facebook.com/v16.0/me/messages',
        params=params,
        headers=headers,
        json=data
    )
    logger.info(f"Отправка сообщения с данными: {data}")
    if response.status_code != 200:
        logger.error(f"Не удалось отправить сообщение: {response.status_code} - {response.text}")
    else:
        logger.info(f"Сообщение отправлено клиенту {recipient_id} успешно")
    return response.json() if response.status_code == 200 else {"error": response.text}


def should_notify(response_text):
    """Проверка, стоит ли отправлять уведомление в Telegram."""
    if not isinstance(response_text, str):
        logger.error(f"Некорректный формат текста ответа: {type(response_text)}. Ожидалась строка.")
        return False

    # Набор ключевых слов для проверки
    trigger_words = {"please", "give", "manager", "information", "minutes"}
    response_words = set(response_text.lower().split())
    match_count = len(response_words & trigger_words)

    logger.info(f"Совпадение ключевых слов: {match_count} (необходимо: 3)")
    return match_count >= 3
