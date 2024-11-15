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

import logging
from openai import OpenAI

# Настраиваем логирование
logger = logging.getLogger("beauty_salon_chatbot")

# Функция для обработки ответа ассистента
def get_response_from_assistant(history, assistant_id, client):
    try:
        # Создание потока сообщений
        logger.info("Создание нового потока сообщений...")
        thread = client.beta.threads.create(messages=history)
        logger.info(f"Созданный поток: {thread}")

        # Запуск диалога с ассистентом
        logger.info("Запуск диалога с ассистентом...")
        run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)
        logger.info(f"Объект Run: {run}")

        # Проверка наличия ответа
        if hasattr(run, 'message') and 'content' in run.message:
            bot_response = run.message['content']
        else:
            logger.error(f"Ошибка: Ответ ассистента пуст или имеет неизвестный формат. Run: {run}")
            bot_response = "Произошла ошибка. Попробуйте снова."

        # Логирование ответа ассистента
        logger.info(f"Ответ ассистента: {bot_response}")

        return bot_response

    except Exception as e:
        # Логирование ошибки
        logger.error(f"Ошибка при общении с ассистентом: {e}")
        return "Произошла ошибка. Попробуйте снова."


