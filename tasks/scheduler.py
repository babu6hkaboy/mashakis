from apscheduler.schedulers.background import BackgroundScheduler
from handlers.database import delete_inactive_threads
from utils.logger import logger
from pytz import timezone

def start_scheduler():
    """Запуск фонового планировщика для очистки сообщений."""
    logger.info("Инициализация планировщика.")
    scheduler = BackgroundScheduler(timezone=timezone('UTC'))
    logger.info("Создан экземпляр планировщика.")

    try:
        scheduler.add_job(delete_inactive_threads, 'interval', minutes=1)
        logger.info("Задача очистки неактивных тредов добавлена в планировщик.")
    except Exception as e:
        logger.error(f"Ошибка при добавлении задачи в планировщик: {e}")

    scheduler.start()
    logger.info("Фоновый планировщик запущен.")
    return scheduler
