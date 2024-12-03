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

async def chat_with_assistant(client, sender_id, user_message):
    try:
        logger.info(f"Начало обработки сообщения от пользователя {sender_id}: {user_message}")

        # Проверка существующего thread_id
        thread_id = get_thread_id(sender_id)
        if not thread_id:
            thread = client.beta.threads.create()
            thread_id = thread.id
            save_thread_id(sender_id, thread_id)
            logger.info(f"Создан новый тред: thread_id={thread_id}")

        # Логируем сообщение, отправляемое в OpenAI
        logger.info(f"Отправляем сообщение в OpenAI от пользователя {sender_id}: {user_message}")
        
        # Добавление нового сообщения пользователя в тред
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
        logger.info(f"Запущено выполнение: run_id={run.id}")

        # Ожидаем завершения выполнения
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            logger.info(f"Статус выполнения: {run_status.status}")

            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                logger.error("Ошибка выполнения.")
                return "Произошла ошибка. Попробуйте снова."
            else:
                time.sleep(2)

        # Получение новых сообщений из треда
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        assistant_responses = [
            msg.content[0].text.value for msg in messages if msg.role == "assistant"
        ]

        if not assistant_responses:
            logger.error("Ответ ассистента не найден.")
            return "Произошла ошибка. Попробуйте снова."

        assistant_response = assistant_responses[-1]

        # Логируем ответ, полученный от OpenAI
        logger.info(f"Полученный ответ от OpenAI для пользователя {sender_id}: {assistant_response}")

        return assistant_response

    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        return "Произошла непредвиденная ошибка."

