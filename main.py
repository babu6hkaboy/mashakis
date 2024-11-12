from flask import Flask, request
from config import VERIFY_TOKEN
from handlers.message_handler import handle_message
from utils.logger import logger

app = Flask(__name__)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Верификация вебхука
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if verify_token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return 'Verification token mismatch', 403
    elif request.method == 'POST':
        # Обработка входящего сообщения
        data = request.get_json()
        logger.info(f"Received message: {data}")
        handle_message(data)
        return 'EVENT_RECEIVED', 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
