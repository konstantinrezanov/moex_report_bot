import pandas as pd


def load_demo_report(demo_path: str) -> pd.DataFrame:
    return pd.read_csv(demo_path, sep=";", index_col='ticker')


def format_ticker(ticker_info: pd.Series) -> str:
    return f"{ticker_info.name}: {ticker_info['close']}"


def format_report(exchange_data: pd.DataFrame) -> str:
    report_lines = [format_ticker(exchange_data.loc[ticker]) for ticker in exchange_data.index]
    return "\n".join(report_lines)


data = load_demo_report('demo.csv')
print(format_report(data))