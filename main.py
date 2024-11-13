from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
from handlers.message_handler import handle_message  # Импорт функции handle_message
from utils.logger import logger

# Загрузите переменные окружения из .env, если используется
load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', '1e9f4858-5058-434b-a778-3ec8d9701ab8')  # Убедитесь, что VERIFY_TOKEN правильный

@app.route('/')
def home():
    return "Welcome to Flask!", 200

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Проверка токена от Facebook
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if verify_token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return 'Verification token mismatch', 403
    elif request.method == 'POST':
        # Получение данных от Messenger
        data = request.get_json()
        logger.info(f"Полученные данные от Messenger: {data}")

        # Вызов функции handle_message для обработки сообщения
        handle_message(data)

        return 'EVENT_RECEIVED', 200

if __name__ == '__main__':
    app.run(debug=True)