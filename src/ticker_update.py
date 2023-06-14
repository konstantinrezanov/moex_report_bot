import pandas as pd
import data_handle

def excel_update(file_path: str, db_path: str, chat_id: int):
    tickers = pd.read_excel(file_path)['ticker']
    data_handle.store_tickers(db_path, chat_id, tickers)
