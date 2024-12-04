from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from datetime import datetime, timedelta
from config import DATABASE_URI
from utils.logger import logger

# Настройка подключения к базе данных
engine = create_engine(
    DATABASE_URI,
    pool_size=10,
    max_overflow=20,
    pool_recycle=280,
    pool_pre_ping=True
)
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

# Модель ClientThread
class ClientThread(Base):
    __tablename__ = 'client_threads'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), unique=True, nullable=False)
    thread_id = Column(String(255), unique=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    # Связь с сообщениями
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")

# Модель Message
class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False)
    thread_id = Column(String(255), ForeignKey('client_threads.thread_id', ondelete="CASCADE"), nullable=False)
    role = Column(Enum('user', 'assistant', name='role_enum'), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    # Связь с тредом
    thread = relationship("ClientThread", back_populates="messages")

# Функция получения thread_id по user_id
def get_thread_id(user_id):
    session = Session()
    try:
        thread = session.query(ClientThread).filter_by(user_id=user_id).first()
        return thread.thread_id if thread else None
    except Exception as e:
        logger.error(f"Ошибка при получении thread_id: {e}")
        return None
    finally:
        session.close()

# Функция сохранения thread_id
def save_thread_id(user_id, thread_id):
    session = Session()
    try:
        existing_thread = session.query(ClientThread).filter_by(user_id=user_id).first()
        if existing_thread:
            existing_thread.thread_id = thread_id
            existing_thread.timestamp = datetime.utcnow()
        else:
            new_thread = ClientThread(user_id=user_id, thread_id=thread_id)
            session.add(new_thread)
        session.commit()
    except Exception as e:
        logger.error(f"Ошибка при сохранении thread_id: {e}")
        session.rollback()
    finally:
        session.close()

# Функция сохранения сообщения
def save_message(thread_id, user_id, role, content):
    session = Session()
    try:
        message = Message(thread_id=thread_id, user_id=user_id, role=role, content=content)
        session.add(message)
        # Обновляем timestamp треда
        thread = session.query(ClientThread).filter_by(thread_id=thread_id).first()
        if thread:
            thread.timestamp = datetime.utcnow()
        session.commit()
    except Exception as e:
        logger.error(f"Ошибка при сохранении сообщения: {e}")
        session.rollback()
    finally:
        session.close()

# Функция получения истории сообщений по thread_id
def get_thread_history(thread_id):
    session = Session()
    try:
        messages = session.query(Message).filter_by(thread_id=thread_id).order_by(Message.timestamp).all()
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    except Exception as e:
        logger.error(f"Ошибка при получении истории треда: {e}")
        return []
    finally:
        session.close()

def delete_inactive_threads():
    session = Session()
    try:
        cutoff_time = datetime.utcnow() - timedelta(minutes=1)  # Для теста используем 1 минуту
        logger.info(f"Начало удаления неактивных тредов. Время отсечения: {cutoff_time}")

        inactive_threads = session.query(ClientThread).filter(ClientThread.timestamp < cutoff_time).all()
        logger.info(f"Найдено {len(inactive_threads)} неактивных тредов для удаления.")

        for thread in inactive_threads:
            session.query(Message).filter_by(thread_id=thread.thread_id).delete()
            session.delete(thread)
            logger.info(f"Удалён тред {thread.thread_id} и связанные сообщения")
        
        session.commit()
    except Exception as e:
        logger.error(f"Ошибка при удалении неактивных тредов: {e}")
        session.rollback()
    finally:
        session.close()
        logger.info("Проверка на неактивные треды завершена.")


# Создание таблиц в базе данных
Base.metadata.create_all(engine)
