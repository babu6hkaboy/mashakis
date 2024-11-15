import os
from dotenv import load_dotenv

load_dotenv()

# Токены и ключи
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
OPENAI_API_KEY = os.getenv('GPT_API_KEY_3')
OPENAI_ASSISTANT_ID = "asst_XxjfUuLuPLYkD8mt6uUdpqQt"
OPENAI_PROJECT_ID = "proj_a2b7dZjMYCxcQmn6j7exH4iq"
OPENAI_ORGANIZATION = "org-h9qd17qCN4hnixxx3p2KoPfX"

# Настройки базы данных MySQL
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME')

DATABASE_URI = f'mysql+pymysql://gen_user:%2Es%5C%7BNYp_G%7D9TUN@185.119.59.113:3306/default_db'


# Настройки OpenAI API
OPENAI_MODEL = 'gpt-3.5-turbo'

#0