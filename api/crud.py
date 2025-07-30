from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models
from collections import Counter
import re
from .models import FctMessage


def get_channel_activity(db: Session, channel_name: str):
    return (
        db.query(func.date(models.FctMessage.message_timestamp).label("date"),
                 func.count().label("message_count"))
        .filter(models.FctMessage.channel_id == channel_name)
        .group_by("date")
        .order_by("date")
        .all()
    )


def search_messages(db: Session, query: str):
    return (
        db.query(models.FctMessage)
        .filter(models.FctMessage.message_text.ilike(f"%{query}%"))
        .limit(100)
        .all()
    )


KNOWN_KEYWORDS = {
    "cosmetics", "vucryl", "gloves", "ventilators", "syringe",
    "wheelchair", "alcohol", "metoclorpromid", "forceps", "ibuprofen", "facemask"
}


def clean_and_tokenize(text):
    # Lowercase, remove non-letters, tokenize
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text.split()


def get_top_keywords(db, limit=10):
    messages = (
        db.query(FctMessage.message_text)
        .filter(FctMessage.message_text != None)
        .all()
    )

    counter = Counter()

    for (text,) in messages:
        tokens = clean_and_tokenize(text)
        if KNOWN_KEYWORDS:
            tokens = [t for t in tokens if t in KNOWN_KEYWORDS]
        counter.update(tokens)

    top_keywords = counter.most_common(limit)
    return [{"keyword": k, "count": c} for k, c in top_keywords]
