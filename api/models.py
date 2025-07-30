from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date
from .database import Base

class FctMessage(Base):
    __tablename__ = "fct_messages"
    __table_args__ = {"schema": "dbt_telegram_mart"}

    message_id = Column(Integer, primary_key=True)
    message_timestamp = Column(DateTime)
    scrape_date = Column(Date)
    channel_id = Column(String)
    sender_id = Column(String)
    message_text = Column(Text)
    view_count = Column(Integer)
    has_image = Column(Boolean)
    message_length = Column(Integer)
    loaded_at = Column(DateTime)

class DimChannel(Base):
    __tablename__ = "dim_channels"
    __table_args__ = {"schema": "dbt_telegram_mart"}

    channel_id = Column(String, primary_key=True)

class DimDate(Base):
    __tablename__ = "dim_dates"
    __table_args__ = {"schema": "dbt_telegram_mart"}

    date = Column(Date, primary_key=True)
    year = Column(Integer)
    month = Column(Integer)
    day = Column(Integer)
    day_of_week = Column(String)
    month_name = Column(String)
    is_weekday = Column(Boolean)
