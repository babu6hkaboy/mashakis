from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from config import DATABASE_URI
from datetime import datetime
from utils.logger import logger
import os

engine = create_engine(
    DATABASE_URI,
    pool_size=10,
    max_overflow=20,
    pool_recycle=280,
    pool_pre_ping=True
)
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()

class ClientMessage(Base):
    __tablename__ = 'client_messages'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255))
    message_text = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

def save_client_message(user_id, message_text):
    session = Session()
    try:
        message = ClientMessage(user_id=user_id, message_text=message_text)
        session.add(message)
        session.commit()
    except Exception as e:
        logger.error(f"Error saving message: {e}")
        session.rollback()
    finally:
        session.close()

def get_client_messages(user_id):
    session = Session()
    try:
        messages = session.query(ClientMessage).filter_by(user_id=user_id).order_by(ClientMessage.timestamp).all()
        return messages
    except Exception as e:
        logger.error(f"Error fetching messages: {e}")
        return []
    finally:
        session.close()

# Создание таблиц в базе данных (если они еще не созданы)
Base.metadata.create_all(engine)
