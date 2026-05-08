from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Ubah baris ini di database.py
DATABASE_URL = "sqlite:///./data/tweets.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TweetLog(Base):
    __tablename__ = "tweet_logs"
    id = Column(Integer, primary_key=True, index=True)
    tweet_text = Column(String, index=True)
    predicted_label = Column(String)
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)