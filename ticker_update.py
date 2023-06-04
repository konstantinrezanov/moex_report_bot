import pandas as pd
import data_handle


# def tinkoff_update():
# def bcs_update():
def excel_update(file_path: str, db_path: str, chat_id: int, time_choice: tuple):
    tickers = pd.read_excel(file_path)
    data_handle.store_tickers(db_path, chat_id, tickers, time_choice)
