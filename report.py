import pandas as pd


def load_demo_report(demo_path: str) -> pd.DataFrame:
    """
    Loads a demo report from a CSV file.

    Args:
        demo_path (str): The path to the demo report CSV file.

    Returns:
        pd.DataFrame: The loaded demo report as a pandas DataFrame.
    """
    return pd.read_csv(demo_path, sep=";")


def format_ticker(ticker_info: pd.Series) -> str:
    """
    Formats ticker information as a string.

    Args:
        ticker_info (pd.Series): A pandas Series containing ticker information.

    Returns:
        str: The formatted ticker information string.
    """
    return f"{ticker_info['ticker']}: {ticker_info['close']}"


def format_report(exchange_data: pd.DataFrame) -> str:
    """
    Formats the exchange data report as a string.

    Args:
        exchange_data (pd.DataFrame): The exchange data as a pandas DataFrame.

    Returns:
        str: The formatted exchange data report string.
    """
    report_lines = [format_ticker(exchange_data.iloc[i]) for i in exchange_data.index]
    return "\n".join(report_lines)
