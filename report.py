import pandas as pd


def load_demo_report(demo_path: str) -> pd.DataFrame:
    return pd.read_csv(demo_path, sep=";")


def format_ticker(ticker_info: pd.Series) -> str:
    return f"{ticker_info['ticker']}: {ticker_info['close']}"


def format_report(exchange_data: pd.DataFrame) -> str:
    report_lines = [format_ticker(exchange_data.iloc[i]) for i in exchange_data.index]
    return "\n".join(report_lines)
