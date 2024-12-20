from apscheduler.schedulers.background import BackgroundScheduler
from handlers.database import delete_inactive_threads
from utils.logger import logger
from pytz import timezone

def start_scheduler():
    """Запуск планировщика."""
    logger.info("Инициализация планировщика.")
    scheduler = BackgroundScheduler(timezone=timezone('UTC'))
    scheduler.add_job(delete_inactive_threads, 'interval', hours=24)  # Интервал 6 часов
    scheduler.start()
    logger.info("Планировщик успешно запущен.")
    return scheduler
