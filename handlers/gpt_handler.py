import os
import re
import io
import logging
import random
import string
from contextlib import redirect_stdout
from openai import Client, AssistantEventHandler
from dotenv import load_dotenv
from database import save_client_message, get_client_messages

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
async def chat_with_assistant(user_id, user_message):
    # Получаем историю сообщений пользователя из базы данных
    messages_from_db = get_client_messages(user_id)
    history = [{'role': 'user', 'content': msg.message_text} for msg in messages_from_db]

    # Добавляем сообщение пользователя в историю
    history.append({'role': 'user', 'content': user_message})
    history = trim_history(history, MAX_HISTORY_LENGTH)

    # Сохраняем сообщение пользователя в базу данных
    save_client_message(user_id, user_message)

    # Инструкции для ассистента
    instructions = """
    You are a helpful assistant for a beauty salon. Provide concise and accurate responses based on the user's messages and context.
    """

    try:
        # Создаём поток и запускаем ассистента
        f = io.StringIO()
        with redirect_stdout(f):
            thread = client.beta.threads.create(messages=history)
            with client.beta.threads.runs.stream(
                thread_id=thread.id,
                assistant_id='asst_XxjfUuLuPLYkD8mt6uUdpqQt',
                instructions=instructions,
                event_handler=EventHandler()
            ) as stream:
                stream.until_done()

        # Чистим вывод от метаданных
        full_output = f.getvalue()
        cleaned_output = re.sub(r"assistant > Text\(.*?\)", "", full_output).strip()

        # Сохраняем ответ ассистента в базу данных
        save_client_message(user_id, cleaned_output)

        return cleaned_output

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return "Произошла ошибка. Попробуйте снова."
