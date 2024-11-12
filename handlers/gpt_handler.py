import openai
from config import OPENAI_API_KEY, OPENAI_MODEL
from utils.data_loader import load_context
from utils.logger import logger

openai.api_key = OPENAI_API_KEY

def generate_response(user_id, user_message):
    context = load_context(user_id)
    messages = [
        {"role": "system", "content": context},
        {"role": "user", "content": user_message}
    ]
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=150,
            temperature=0.7,
        )
        bot_message = response.choices[0].message.content.strip()
        return bot_message
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        # Уведомляем владельца о проблеме
        from handlers.telegram_notifier import send_telegram_notification
        send_telegram_notification(user_id, user_message)
        return "Извините, возникла техническая неполадка. Мы свяжемся с вами в ближайшее время."
