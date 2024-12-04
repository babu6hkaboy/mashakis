from apscheduler.schedulers.background import BackgroundScheduler
from handlers.database import delete_inactive_threads
from utils.logger import logger
from pytz import timezone

def start_scheduler():
    """Запуск фонового планировщика для очистки сообщений."""
    scheduler = BackgroundScheduler(timezone=timezone('UTC'))
    scheduler.add_job(delete_inactive_threads, 'interval', minutes=1)
    scheduler.start()
    logger.info("Фоновый планировщик для очистки сообщений запущен.")
    return scheduler