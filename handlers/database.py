from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from config import DATABASE_URI
from datetime import datetime
from utils.logger import logger

engine = create_engine(
    DATABASE_URI,
    pool_size=10,
    max_overflow=20,
    pool_recycle=280,
    pool_pre_ping=True
)
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

class ClientThread(Base):
    __tablename__ = 'client_threads'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), unique=True)
    thread_id = Column(String(255), unique=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    # Связь с сообщениями
    messages = relationship("Message", back_populates="thread", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False)
    thread_id = Column(String(255), ForeignKey('client_threads.thread_id', ondelete="CASCADE"), nullable=False)
    role = Column(Enum('user', 'assistant', name='role_enum'), nullable=False)  # Роль отправителя
    content = Column(String, nullable=False)  # Текст сообщения
    timestamp = Column(DateTime, default=datetime.utcnow)  # Время отправки сообщения
    # Связь с тредом
    thread = relationship("ClientThread", back_populates="messages")

def get_thread_id(user_id):
    session = Session()
    try:
        thread = session.query(ClientThread).filter_by(user_id=user_id).first()
        return thread.thread_id if thread else None
    except Exception as e:
        logger.error(f"Error fetching thread_id: {e}")
        return None
    finally:
        session.close()

def save_thread_id(user_id, thread_id):
    session = Session()
    try:
        existing_thread = session.query(ClientThread).filter_by(user_id=user_id).first()
        if existing_thread:
            existing_thread.thread_id = thread_id
        else:
            new_thread = ClientThread(user_id=user_id, thread_id=thread_id)
            session.add(new_thread)
        session.commit()
    except Exception as e:
        logger.error(f"Error saving thread_id: {e}")
        session.rollback()
    finally:
        session.close()

def save_message(thread_id, user_id, role, content):
    """Сохраняет сообщение в базу данных."""
    session = Session()
    try:
        message = Message(thread_id=thread_id, user_id=user_id, role=role, content=content)
        session.add(message)
        session.commit()
    except Exception as e:
        logger.error(f"Error saving message: {e}")
        session.rollback()
    finally:
        session.close()

def get_thread_history(thread_id):
    """Возвращает всю историю сообщений для заданного thread_id."""
    session = Session()
    try:
        messages = session.query(Message).filter_by(thread_id=thread_id).order_by(Message.timestamp).all()
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    except Exception as e:
        logger.error(f"Error fetching thread history: {e}")
        return []
    finally:
        session.close()

# Создание таблиц в базе данных (если они еще не созданы)
Base.metadata.create_all(engine)
