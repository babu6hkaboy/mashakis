import os
import logging
import time
from datetime import datetime
import openai
from dotenv import load_dotenv
from handlers.database import get_thread_id, save_thread_id

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("beauty_salon_chatbot")

# Укажите постоянный ID ассистента
ASSISTANT_ID = "asst_cTZRlEe4EtoSy17GYjpEz1GZ"

# Укажите ваш API-ключ OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OpenAI API ключ не найден в переменных окружения")

# Создание клиента
client = openai.OpenAI(api_key=openai.api_key)


def create_thread():
    """Создает новый поток и возвращает его ID."""
    thread = client.beta.threads.create()
    logger.info(f"Создан новый тред: {thread.id}")
    return thread.id


def send_message_to_thread(thread_id, content):
    """Отправка сообщения пользователя в поток."""
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content,
    )
    logger.info(f"Отправлено сообщение пользователя в thread_id={thread_id}: {content}")
    return message


def get_assistant_response(thread_id):
    """Получение ответа ассистента с использованием ASSISTANT_ID."""
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID,
    )
    logger.info(f"Запущен Run: {run.id}")

    while True:
        run_status = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id,
        )
        logger.info(f"Статус выполнения Run: {run_status.status}")

        if run_status.status == "completed":
            break
        elif run_status.status == "failed":
            logger.error("Ошибка выполнения Run.")
            return None
        else:
            time.sleep(2)

    # Получение сообщений из треда
    messages = list(client.beta.threads.messages.list(thread_id=thread_id))
    assistant_message = next(
        (msg for msg in messages if msg.role == "assistant"),
        None,
    )
    if assistant_message:
        logger.info(f"Ответ ассистента: {assistant_message.content[0].text.value}")
        return assistant_message.content[0].text.value
    else:
        logger.error("Ответ ассистента не найден.")
        return None


async def chat_with_assistant(sender_id, user_message):
    """Организация взаимодействия с ассистентом через выбранный тред."""
    try:
        logger.info(
            f"Начало обработки сообщения от пользователя {sender_id}: {user_message}"
        )

        # Проверка существующего thread_id
        thread_id = get_thread_id(sender_id)
        if not thread_id:
            # Создаем новый тред
            thread_id = create_thread()
            save_thread_id(sender_id, thread_id)
            logger.info(f"Создан новый тред: {thread_id}")
        else:
            logger.info(f"Используется существующий тред: {thread_id}")

        # Отправка сообщения пользователя
        send_message_to_thread(thread_id, user_message)

        # Получение ответа ассистента
        assistant_response = get_assistant_response(thread_id)
        if not assistant_response:
            return "Произошла ошибка. Попробуйте снова."

        return assistant_response

    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        return "Произошла непредвиденная ошибка."
