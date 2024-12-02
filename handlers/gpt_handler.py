import os
import logging
import time
import openai
from dotenv import load_dotenv
from handlers.database import get_thread_id, save_thread_id

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем API-ключ OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    raise ValueError("OpenAI API ключ не найден в переменных окружения")

client = openai.OpenAI(api_key=openai.api_key)

# Асинхронная функция для общения с ассистентом
async def chat_with_assistant(client, sender_id, user_message):
    try:
        # Проверка существующего thread_id
        thread_id = get_thread_id(sender_id)
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id
            save_thread_id(sender_id, thread_id)
            logger.info(f"Создан новый тред: thread_id={thread_id}")

        # Добавление сообщения пользователя в существующий тред
        if user_message.strip():
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_message
            )
            logger.info(f"Добавлено сообщение пользователя в thread_id={thread_id}: {user_message}")

        # Запуск выполнения ассистента
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id="asst_cTZRlEe4EtoSy17GYjpEz1GZ"
        )
        logger.info(f"Запуск выполнения ассистента: thread_id={thread_id}, run_id={run.id}")

        # Проверка выполнения ассистента
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            logger.info(f"Текущий статус выполнения ассистента: {run_status.status}")

            if run_status.status == "completed":
                logger.info(f"Выполнение завершено: thread_id={thread_id}")
                break
            elif run_status.status == "failed":
                logger.error(f"Ошибка выполнения ассистента: thread_id={thread_id}")
                return "Произошла ошибка. Попробуйте снова."
            time.sleep(2)

        # Получение последнего сообщения от ассистента
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_response = [
            msg.content[0].text.value for msg in messages if msg.role == "assistant"
        ][-1]
        logger.info(f"Ответ ассистента: {assistant_response}")

        return assistant_response

    except Exception as e:
        logger.error(f"Ошибка в chat_with_assistant: {e}")
        return "Произошла ошибка. Попробуйте снова."
