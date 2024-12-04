import os
import logging
import time
from datetime import datetime
import openai
from dotenv import load_dotenv
from handlers.database import get_thread_id, save_thread_id, save_message, get_thread_history

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
    """Обработка сообщения с учётом сохранения и передачи истории."""
    try:
        logger.info(f"Начало обработки сообщения от пользователя {sender_id}: {user_message}")

        # Получение thread_id из базы данных
        thread_id = get_thread_id(sender_id)
        if not thread_id:
            thread_id = create_thread()
            save_thread_id(sender_id, thread_id)
            logger.info(f"Создан новый тред: {thread_id}")

        # Сохраняем сообщение пользователя
        save_message(thread_id, sender_id, "user", user_message)

        # Извлекаем историю сообщений
        thread_history = get_thread_history(thread_id)

        # Отправка истории и получение ответа
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID,
            messages=thread_history,
        )
        logger.info(f"Запущен Run: {run.id}")

        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            logger.info(f"Статус выполнения Run: {run_status.status}")

            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                logger.error("Ошибка выполнения Run.")
                return "Произошла ошибка. Попробуйте снова."
            else:
                time.sleep(2)

        # Извлекаем последний ответ ассистента
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_message = next((msg for msg in messages if msg.role == "assistant"), None)
        if assistant_message:
            assistant_reply = assistant_message.content[0].text.value
            save_message(thread_id, sender_id, "assistant", assistant_reply)  # Сохраняем ответ ассистента
            return assistant_reply
        else:
            logger.error("Ответ ассистента не найден.")
            return "Произошла ошибка. Попробуйте снова."

    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        return "Произошла непредвиденная ошибка."
