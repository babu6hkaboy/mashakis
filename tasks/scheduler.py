from apscheduler.schedulers.background import BackgroundScheduler
from handlers.database import delete_inactive_threads
from utils.logger import logger
from pytz import timezone

def log_scheduler_heartbeat():
    """Логирует активность планировщика."""
    logger.info("BackgroundScheduler активно и работает.")

def start_scheduler():
    """Запуск фонового планировщика для очистки сообщений."""
    scheduler = BackgroundScheduler(timezone=timezone('UTC'))
    
    # Задача для удаления неактивных тредов
    scheduler.add_job(delete_inactive_threads, 'interval', minutes=1)
    
    # Задача для проверки активности планировщика
    scheduler.add_job(log_scheduler_heartbeat, 'interval', seconds=30)
    
    scheduler.start()
    logger.info("Фоновый планировщик для очистки сообщений запущен.")
    return scheduler
