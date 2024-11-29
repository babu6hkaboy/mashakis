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
import time

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем API-ключ OpenAI
openai_api_key = os.getenv('OPENAI_API_KEY', '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')
if not openai_api_key:
    raise ValueError("OpenAI API ключ не найден в переменных окружения")

# Инициализируем клиент OpenAI
client = Client(api_key=openai_api_key)

# Максимальное количество сообщений в истории
MAX_HISTORY_LENGTH = 10

# Генерация уникального chat_id
def generate_chat_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# Класс для обработки событий ассистента
class EventHandler(AssistantEventHandler):
    def on_text_created(self, text) -> None:
        print(f"\nassistant > {text}", end="", flush=True)

    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

# Функция для ограничения длины истории сообщений
def trim_history(history, max_length):
    return history[-max_length:]

# Асинхронная функция для общения с ассистентом
async def chat_with_assistant(client, user_id, user_message):
    # Получаем историю сообщений пользователя
    messages_from_db = get_client_messages(user_id)
    history = [{'role': 'user', 'content': msg.message_text} for msg in messages_from_db]

    # Создание нового потока
    thread = client.beta.threads.create()

    # Добавление сообщений в поток
    for message in history:
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role=message['role'],
            content=message['content']
        )

    # Добавление нового сообщения пользователя
    if user_message.strip():
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )

    # Запуск выполнения ассистента
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id="asst_cTZRlEe4EtoSy17GYjpEz1GZ"
    )

    # Ожидание завершения выполнения
    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )
        if run_status.status == "completed":
            break
        elif run_status.status == "failed":
            logger.error("Ошибка выполнения ассистента")
            return "Произошла ошибка. Попробуйте снова."
        time.sleep(2)

    # Получение ответа
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    assistant_response = [
        msg.content for msg in messages if msg.role == "assistant"
    ][-1]

    # Сохраняем сообщение ассистента в базу данных
    save_client_message(user_id, assistant_response)

    return assistant_response

    
#1
