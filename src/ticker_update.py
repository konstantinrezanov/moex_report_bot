import pandas as pd
import data_handle


# def tinkoff_update():
# def bcs_update():
def excel_update(file_path: str, db_path: str, chat_id: int, time_choice: tuple):
    """
    Updates tickers data from an Excel file and stores it in the database.

    Args:
        file_path (str): The path to the Excel file.
        db_path (str): The path to the database file.
        chat_id (int): The ID of the chat/user.
        time_choice (tuple): A tuple representing the time choice.

    Returns:
        None
    """
    tickers = pd.read_excel(file_path)
    data_handle.store_tickers(db_path, chat_id, tickers, time_choice)
