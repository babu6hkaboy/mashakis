from flask import Flask, request
from dotenv import load_dotenv
import os
from handlers.message_handler import handle_message
from utils.logger import logger
import asyncio

load_dotenv()

app = Flask(__name__)
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', '1e9f4858-5058-434b-a778-3ec8d9701ab8')

@app.route('/')
def home():
    return "Welcome to Flask!", 200

@app.route('/webhook', methods=['POST'])
def webhook(client):
    data = request.get_json()
    logger.info(f"Полученные данные от Messenger: {data}")
    handle_message(data, client)  # Здесь без asyncio.run
    return 'EVENT_RECEIVED', 200


if __name__ == '__main__':
    app.run(debug=True)
 