import os
import logging
import time
import openai
from dotenv import load_dotenv
from handlers.database import save_client_message, get_client_messages

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
        # Получение истории сообщений из базы данных
        logger.info(f"Получение истории сообщений для user_id={sender_id}")
        messages_from_db = get_client_messages(sender_id)

        # Формирование полной истории для потока
        history = [
            {'role': 'user', 'content': msg.message_text.strip()}
            for msg in messages_from_db
            if msg.message_text and msg.message_text.strip()
        ]
        logger.info(f"История сообщений (полная): {history}")

        # Создание нового потока
        thread = openai.OpenAI(api_key=openai.api_key).beta.threads.create()
        logger.info(f"Создан новый поток: thread_id={thread.id}")

        # Добавление сообщений из истории в поток
        for message in history:
            openai.OpenAI(api_key=openai.api_key).beta.threads.messages.create(
                thread_id=thread.id,
                role=message['role'],
                content=message['content']
            )
        logger.info(f"Сообщения из истории добавлены в поток thread_id={thread.id}")

        # Добавление текущего сообщения пользователя в поток
        if user_message.strip():
            openai.OpenAI(api_key=openai.api_key).beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_message
            )
            logger.info(f"Добавлено сообщение пользователя: {user_message}")

        # Сохранение сообщения пользователя в базу данных
        save_client_message(sender_id, user_message)
        logger.info(f"Сообщение пользователя сохранено в базу данных: {user_message}")

        # Запуск выполнения ассистента
        run = openai.OpenAI(api_key=openai.api_key).beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id="asst_cTZRlEe4EtoSy17GYjpEz1GZ"
        )
        logger.info(f"Запуск выполнения ассистента: run_id={run.id}")

        # Проверка выполнения ассистента
        while True:
            run_status = openai.OpenAI(api_key=openai.api_key).beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            logger.info(f"Текущий статус выполнения ассистента: {run_status.status}")

            if run_status.status == "completed":
                logger.info("Выполнение ассистента завершено успешно.")
                break
            elif run_status.status == "failed":
                logger.error("Ошибка выполнения ассистента.")
                return "Произошла ошибка. Попробуйте снова."
            time.sleep(2)  # Ожидание перед повторной проверкой

        # Получение сообщений из потока
        messages = openai.OpenAI(api_key=openai.api_key).beta.threads.messages.list(thread_id=thread.id)
        assistant_response = [
            msg.content[0].text.value for msg in messages if msg.role == "assistant"
        ][-1]
        logger.info(f"Ответ ассистента: {assistant_response}")

        # Сохранение ответа ассистента в базу данных
        save_client_message(sender_id, assistant_response)
        logger.info(f"Ответ ассистента сохранен в базу данных: {assistant_response}")

        return assistant_response

    except Exception as e:
        logger.error(f"Ошибка в chat_with_assistant: {e}")
        return "Произошла ошибка. Попробуйте снова."
