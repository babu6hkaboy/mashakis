import os
from dotenv import load_dotenv

load_dotenv()

# Токены и ключи
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Настройки базы данных MySQL
# ... ваши настройки базы данных ...

# Настройки OpenAI API
OPENAI_MODEL = 'gpt-3.5-turbo'
