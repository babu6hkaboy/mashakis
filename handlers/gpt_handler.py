import openai
from config import OPENAI_API_KEY, OPENAI_MODEL
from handlers.telegram_notifier import send_telegram_notification_to_channel
from utils.data_loader import load_context
from utils.logger import logger

openai.api_key = OPENAI_API_KEY

def generate_response(user_id, user_message):
    context = load_context(user_id)
    assistant_instructions = (
        "If you are unable to assist the client with their request, "
        "please respond with the following phrase exactly: "
        "'I will pass the information to the manager and she will come back to you as soon as possible'"
    )
    messages = [
        {"role": "system", "content": assistant_instructions + "\n" + context},
        {"role": "user", "content": user_message}
    ]
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.2,
        )
        bot_message = response.choices[0].message.content.strip()
        return bot_message
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        send_telegram_notification_to_channel(user_id, user_message)
        return "Извините, возникла техническая неполадка. Мы свяжемся с вами в ближайшее время."
