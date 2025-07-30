from pydantic import BaseModel
from datetime import datetime, date
from typing import List

class MessageOut(BaseModel):
    message_id: int
    message_timestamp: datetime
    channel_id: str
    message_text: str
    view_count: int

    class Config:
        orm_mode = True

class ChannelActivity(BaseModel):
    date: date
    message_count: int

class ChannelOut(BaseModel):
    channel_id: str

class SearchResult(BaseModel):
    message_id: int
    message_timestamp: datetime
    channel_id: str
    message_text: str

class KeywordCount(BaseModel):
    keyword: str
    count: int
