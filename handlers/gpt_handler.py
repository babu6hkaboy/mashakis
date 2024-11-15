import os
import re
import io
import logging
import random
import string
from contextlib import redirect_stdout
from openai import Client, AssistantEventHandler
from dotenv import load_dotenv
from handlers.database import save_client_message, get_client_messages

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем API-ключ OpenAI
openai_api_key = os.getenv('GPT_API_KEY_3')
if not openai_api_key:
    raise ValueError("OpenAI API ключ не найден в переменных окружения")

# Инициализируем клиент OpenAI
client = Client(api_key=openai_api_key)

# Максимальное количество сообщений в истории
MAX_HISTORY_LENGTH = 10

# Класс для обработки событий ассистента
class EventHandler(AssistantEventHandler):
    def on_text_created(self, text) -> None:
        print(f"\nassistant > {text}", end="", flush=True)

    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

# Функция для ограничения длины истории сообщений
def trim_history(history, max_length):
    return history[-max_length:]

def chat_with_assistant_sync(user_id, user_message):
    """Синхронное общение с ассистентом"""
    # Получение истории сообщений
    messages_from_db = get_client_messages(user_id)
    history = [{'role': 'user', 'content': msg.message_text} for msg in messages_from_db]

    # Добавляем новое сообщение в историю
    history.append({'role': 'user', 'content': user_message})
    history = trim_history(history, MAX_HISTORY_LENGTH)

    # Сохраняем сообщение пользователя в базу данных
    save_client_message(user_id, user_message)

    try:
        # Создаём поток (thread) и запускаем диалог
        thread = client.beta.threads.create(messages=history)
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id="asst_XxjfUuLuPLYkD8mt6uUdpqQt",  # Ваш ID ассистента
        )

        # Логируем объект Run для анализа
        logger.info(f"Run object: {run}")

        # Извлечение ответа из объекта Run
        if hasattr(run, 'message') and run.message:
            bot_response = run.message['content']
        else:
            logger.error(f"Ошибка: Не удалось извлечь ответ из объекта Run: {run}")
            bot_response = "Произошла ошибка. Попробуйте снова."

        # Сохраняем ответ ассистента в базу данных
        save_client_message(user_id, bot_response)
        return bot_response

    except Exception as e:
        logger.error(f"Ошибка при общении с ассистентом: {e}")
        return "Произошла ошибка. Попробуйте снова."

