from flask import Flask, request
from dotenv import load_dotenv
import os
from handlers.message_handler import handle_message
from utils.logger import logger
import asyncio

load_dotenv()

app = Flask(__name__)
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', '1e9f4858-5058-434b-a778-3ec8d9701ab8')

# Инициализация OpenAI клиента
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Убедитесь, что переменная окружения установлена

if not OPENAI_API_KEY:
    raise RuntimeError("Переменная окружения 'OPENAI_API_KEY' не установлена!")

@app.route('/')
def home():
    return "Welcome to Flask!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        handle_message(data)  # Передаем данные из запроса
        return "OK", 200
    except Exception as e:
        app.logger.error(f"Ошибка: {e}")
        return "Ошибка на сервере", 500


if __name__ == '__main__':
    app.run(debug=True)
 