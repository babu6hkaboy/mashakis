from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import logging
from handlers.openai_assistant import get_assistant_response  # Импорт функции взаимодействия с OpenAI
from utils.logger import logger

# Загрузка переменных окружения из .env файла
load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', '1e9f4858-5058-434b-a778-3ec8d9701ab8')

@app.route('/')
def home():
    return "Welcome to Flask!", 200

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Валидация токена для Facebook
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

        # Извлечение ID отправителя и текста сообщения
        sender_id = data['entry'][0]['messaging'][0]['sender']['id']
        user_message = data['entry'][0]['messaging'][0]['message']['text']
        
        # Вызов функции для получения ответа ассистента
        chat_history = [{"role": "user", "content": user_message}]  # Если нужно, добавьте историю сообщений
        assistant_reply = get_assistant_response(user_message, chat_history)
        logger.info(f"Ответ ассистента: {assistant_reply}")

        # Формирование ответа для отправки обратно в Messenger
        response_data = {
            "recipient": {"id": sender_id},
            "message": {"text": assistant_reply}
        }

        # Возвращаем подтверждение
        return jsonify(response_data), 200

if __name__ == '__main__':
    app.run(debug=True)
