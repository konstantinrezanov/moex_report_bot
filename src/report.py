import pandas as pd


def format_ticker(ticker_info: pd.Series) -> str:
    """
    Formats ticker information into a string.

    Args:
        ticker_info (pd.Series): The ticker information as a Series.

    Returns:
        str: The formatted ticker information.
    """
    return f"{ticker_info.name}   {ticker_info['close_price']}   {ticker_info['DoD']}%   {ticker_info['WoW']}%   {ticker_info['MoM']}%   {ticker_info['YoY']}%"


def format_report(exchange_data: pd.DataFrame) -> str:
    """
    Formats the exchange data report into a string.

    Args:
        exchange_data (pd.DataFrame): The exchange data report as a DataFrame.

    Returns:
        str: The formatted exchange data report.
    """
    report_lines = [format_ticker(exchange_data.loc[i]) for i in exchange_data.index]
    return "Тикер  Цена     DoD     WoW     MoM     YoY\n" + "\n".join(report_lines)
