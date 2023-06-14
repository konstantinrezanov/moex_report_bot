import pandas as pd
from tinydb import TinyDB, Query
import os


def setup_db(db_path: str):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)


def store_tickers(db_path: str, chat_id: int, tickers: pd.Series):
    db_path = TinyDB(db_path)
    User = Query()
    db_path.upsert({'chat_id': chat_id, "tickers": list(tickers.values)}, User.chat_id == chat_id)


def store_time(db_path: str, chat_id: int, time_choice: tuple):
    db_path = TinyDB(db_path)
    User = Query()
    db_path.upsert({'chat_id': chat_id, "time": time_choice}, User.chat_id == chat_id)


def get_user_tickers(db_path: str, chat_id: int) -> list:
    db = TinyDB(db_path)
    chat = Query()
    return db.get(chat.chat_id == chat_id)['tickers']


def get_user_time(db_path: str) -> dict:
    db = TinyDB(db_path)
    jobs = {}
    for user in db.all():
        jobs[user["chat_id"]] = tuple(user["time"])

    return jobs


def get_users(db_path: str) -> list:
    db = TinyDB(db_path)
    return [x['chat_id'] for x in db.all()]