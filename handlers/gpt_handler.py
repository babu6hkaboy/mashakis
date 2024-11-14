import openai
from config import OPENAI_API_KEY, OPENAI_ORGANIZATION, OPENAI_ASSISTANT_ID
from utils.logger import logger

# Устанавливаем API-ключ и организацию
openai.organization = OPENAI_ORGANIZATION
openai.api_key = OPENAI_API_KEY

def generate_response(user_message):
    try:
        # Создаем запрос к ассистенту, используя assistant_id
        response = openai.ChatCompletion.create(
            assistant_id=OPENAI_ASSISTANT_ID,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        logger.error(f"Error generating response from assistant: {e}")
        return "Извините, возникла техническая неполадка. Мы свяжемся с вами в ближайшее время."
