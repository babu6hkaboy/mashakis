import openai
from config import OPENAI_API_KEY, OPENAI_ASSISTANT_ID
from handlers.telegram_notifier import send_telegram_notification_to_channel
from utils.logger import logger

openai.api_key = OPENAI_API_KEY

def generate_response(user_message):
    try:
        response = openai.Assistant.create(
            assistant=OPENAI_ASSISTANT_ID,
            messages=[{"role": "user", "content": user_message}],
            max_tokens=150,
            temperature=0.7,
        )
        bot_message = response.choices[0].message.content.strip()
        return bot_message
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        # Отправляем уведомление в Telegram-канал в случае ошибки
        send_telegram_notification_to_channel("Error", user_message)
        return "Извините, возникла техническая неполадка. Мы свяжемся с вами в ближайшее время."
