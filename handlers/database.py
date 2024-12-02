from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
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

# Создание таблиц в базе данных (если они еще не созданы)
Base.metadata.create_all(engine)
