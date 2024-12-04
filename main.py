from flask import Flask, request
from dotenv import load_dotenv
import os
from handlers.message_handler import handle_message
from utils.logger import logger
from tasks.scheduler import start_scheduler  # Импорт функции запуска планировщика
from threading import Thread

load_dotenv()

app = Flask(__name__)
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', '1e9f4858-5058-434b-a778-3ec8d9701ab8')

@app.route('/')
def home():
    return "Welcome to Flask!", 200

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if verify_token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return 'Verification token mismatch', 403
    elif request.method == 'POST':
        data = request.get_json()
        logger.info(f"Полученные данные от Messenger: {data}")
        handle_message(data)
        return 'EVENT_RECEIVED', 200

def run_app():
    """Функция для запуска Flask-приложения."""
    app.run(debug=True, use_reloader=False)  # Отключаем autoreload, чтобы избежать дублирования потоков

if __name__ == '__main__':
    # Запуск планировщика в отдельном потоке
    scheduler_thread = Thread(target=start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    logger.info("Планировщик запущен в отдельном потоке.")

    # Запуск Flask-приложения
    run_app()
