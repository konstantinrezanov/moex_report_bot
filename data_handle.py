import pandas as pd
from tinydb import TinyDB, Query
import os


def setup_db(db_path: str):
    """
    Creates the directory for the database file if it doesn't exist.

    Args:
        db_path (str): The path to the database file.

    Returns:
        None
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)


def store_tickers(db: str, chat_id: int, tickers: pd.DataFrame, time_choice: tuple):
    """
    Stores tickers data in the database.

    Args:
        db (str): The path to the database file.
        chat_id (int): The ID of the chat/user.
        tickers (pd.DataFrame): DataFrame containing tickers data.
        time_choice (tuple): A tuple representing the time choice.

    Returns:
        None
    """
    db = TinyDB(db)
    db.insert({'chat_id': chat_id, "tickers": tickers.to_dict(), "time": time_choice})


def get_user_tickers(db_path: str, chat_id: int) -> pd.DataFrame:
    """
    Retrieves tickers data for a specific user from the database.

    Args:
        db_path (str): The path to the database file.
        chat_id (int): The ID of the chat/user.

    Returns:
        pd.DataFrame: DataFrame containing tickers data.
    """
    db = TinyDB(db_path)
    chat = Query()
    return pd.DataFrame(db.get(chat.chat_id == chat_id)['tickers'])


def get_user_time(db_path: str) -> dict:
    """
    Retrieves time choices for all users from the database.

    Args:
        db_path (str): The path to the database file.

    Returns:
        dict: A dictionary containing user IDs as keys and time choices as values.
    """
    db = TinyDB(db_path)
    jobs = {}
    for user in db.all():
        jobs[user["chat_id"]] = tuple(user["time"])

    return jobs


def get_users(db_path: str) -> list:
    """
    Retrieves a list of all user IDs from the database.

    Args:
        db_path (str): The path to the database file.

    Returns:
        list: A list of user IDs.
    """
    db = TinyDB(db_path)
    return [x['chat_id'] for x in db.all()]
