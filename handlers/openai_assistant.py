import openai
from utils.logger import logger
import os

# Загрузка API-ключа
openai.api_key = os.getenv('OPENAI_API_KEY')
ASSISTANT_ID = os.getenv('OPENAI_ASSISTANT_ID')  # Убедитесь, что ассистент ID указан в .env

def get_assistant_response(user_message, chat_history):
    try:
        # Создаем запрос к OpenAI с использованием ChatCompletion
        response = openai.ChatCompletion.create(
            model=ASSISTANT_ID,
            messages=chat_history + [{"role": "user", "content": user_message}],
            max_tokens=150,
            temperature=0.7,
        )
        
        # Получение ответа ассистента
        assistant_reply = response['choices'][0]['message']['content'].strip()
        return assistant_reply

    except Exception as e:
        logger.error(f"Ошибка при получении ответа от ассистента: {e}")
        return "Извините, возникла ошибка. Пожалуйста, попробуйте позже."
