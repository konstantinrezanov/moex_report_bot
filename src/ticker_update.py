import pandas as pd
import data_handle


def excel_update(file_path: str, db_path: str, chat_id: int):
    """
    Updates the database with tickers from an Excel file.

    Args:
        file_path (str): The path to the Excel file.
        db_path (str): The path to the database file.
        chat_id (int): The chat ID associated with the tickers.

    Returns:
        None
    """
    tickers = pd.read_excel(file_path)['ticker']
    data_handle.store_tickers(db_path, chat_id, tickers)
