import pandas as pd
from tinydb import TinyDB, Query
import os


def setup_db(db_path: str):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)


def store_tickers(db: str, chat_id: int, tickers: pd.DataFrame, time_choice: tuple):
    db = TinyDB(db)
    db.insert({'chat_id': chat_id, "tickers": tickers.to_dict(), "time": time_choice})


def get_user_tickers(db_path: str, chat_id: int) -> pd.DataFrame:
    db = TinyDB(db_path)
    chat = Query()
    return pd.DataFrame(db.get(chat.chat_id == chat_id)['tickers'])


def get_user_time(db_path: str) -> dict:
    db = TinyDB(db_path)
    jobs = {}
    for user in db.all():
        jobs[user["chat_id"]] = tuple(user["time"])

    return jobs


def get_users(db_path: str) -> list:
    db = TinyDB(db_path)
    return [x['chat_id'] for x in db.all()]
