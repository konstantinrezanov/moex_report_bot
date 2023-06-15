import pandas as pd
from tinydb import TinyDB, Query
import os


def setup_db(db_path: str):
    """
    Creates the directory for the database file if it doesn't exist.

    Args:
        db_path (str): The path to the database file.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)


def store_tickers(db_path: str, chat_id: int, tickers: pd.Series):
    """
    Stores the tickers associated with a chat ID in the database.

    Args:
        db_path (str): The path to the database file.
        chat_id (int): The ID of the chat.
        tickers (pd.Series): A Pandas Series object containing the tickers.

    """
    db_path = TinyDB(db_path)  # Initialize the TinyDB object with the given database path
    User = Query()  # Create a Query object for performing queries on the database
    db_path.upsert({'chat_id': chat_id, "tickers": list(tickers.values)}, User.chat_id == chat_id)
    # Update or insert a new document in the database with chat_id and tickers


def store_time(db_path: str, chat_id: int, time_choice: tuple):
    """
    Stores the time choice associated with a chat ID in the database.

    Args:
        db_path (str): The path to the database file.
        chat_id (int): The ID of the chat.
        time_choice (tuple): A tuple representing the time choice.

    """
    db_path = TinyDB(db_path)  # Initialize the TinyDB object with the given database path
    User = Query()  # Create a Query object for performing queries on the database
    db_path.upsert({'chat_id': chat_id, "time": time_choice}, User.chat_id == chat_id)
    # Update or insert a new document in the database with chat_id and time_choice


def get_user_tickers(db_path: str, chat_id: int) -> list:
    """
    Retrieves the tickers associated with a chat ID from the database.

    Args:
        db_path (str): The path to the database file.
        chat_id (int): The ID of the chat.

    Returns:
        list: A list of tickers associated with the chat ID.
    """
    db = TinyDB(db_path)  # Initialize the TinyDB object with the given database path
    chat = Query()  # Create a Query object for performing queries on the database
    return db.get(chat.chat_id == chat_id)['tickers']
    # Retrieve the tickers field from the document with the matching chat_id


def set_jobs_dict(db_path: str) -> dict:
    """
    Creates a dictionary of chat IDs and their corresponding time choices from the database.

    Args:
        db_path (str): The path to the database file.

    Returns:
        dict: A dictionary mapping chat IDs to time choices.
    """
    db = TinyDB(db_path)  # Initialize the TinyDB object with the given database path
    jobs = {}  # Dictionary to store the chat IDs and time choices
    for user in db.all():
        try:
            jobs[user["chat_id"]] = tuple(user["time"])
            # Add chat ID and time choice as a key-value pair to the jobs dictionary
        except KeyError:
            continue  # Skip users without a time choice field

    return jobs


def get_user_time(db_path: str, chat_id: int) -> tuple:
    """
    Retrieves the time choice associated with a chat ID from the database.

    Args:
        db_path (str): The path to the database file.
        chat_id (int): The ID of the chat.

    Returns:
        tuple: The time choice associated with the chat ID.
    """
    db = TinyDB(db_path)  # Initialize the TinyDB object with the given database path
    chat = Query()  # Create a Query object for performing queries on the database
    return db.get(chat.chat_id == chat_id)['time']
    # Retrieve the time field from the document with the matching chat_id


def get_users(db_path: str) -> list:
    """
    Retrieves a list of chat IDs from the database.

    Args:
        db_path (str): The path to the database file.

    Returns:
        list: A list of chat IDs.
    """
    db = TinyDB(db_path)  # Initialize the TinyDB object with the given database path
    return [x['chat_id'] for x in db.all()]
    # Extract the chat_id field from all documents in the database and return as a list
