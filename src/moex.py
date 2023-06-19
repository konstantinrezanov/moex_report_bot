import datetime
import warnings
import pandas_datareader as pdr
import pandas as pd
import requests_cache
from dateutil.relativedelta import relativedelta
from pandas.tseries.offsets import CustomBusinessDay

moex_holidays = [datetime.date(2023, 6, 12), datetime.date(2022, 6, 12), datetime.date(2022, 6, 13),
                 datetime.date(2022, 11, 4), datetime.date(2023, 11, 4)]  # MOEX holidays for the this and previous year
moex_bday = CustomBusinessDay(holidays=moex_holidays)  # Creates custom BusinessDay object with custom holidays


def get_nearest_work_day(today: datetime.datetime) -> datetime.date:
    """
    Returns the nearest working day given a datetime.

    Args:
        today (datetime.datetime): The current datetime.

    Returns:
        datetime.date: The nearest working day.

    """
    if today.date() in moex_holidays or today.weekday() in [5, 6] or today.hour < 24:
        return today - moex_bday  # If today is holiday returns nearst workday, hour< 24 because MOEX returns data at the end of the day
    return today


def price_change(date1: pd.Series, date2: pd.Series) -> pd.Series:
    """
    Calculates the price change percentage between two sets of prices.

    Args:
        date1 (pd.Series): The first set of prices.
        date2 (pd.Series): The second set of prices.

    Returns:
        pd.Series: The price change percentage.

    """
    return ((date1 / date2 - 1) * 100).round(2) # Divdes to pd.Series and converts to percentage to get price changes


def get_prices(ticker_list: list, date: datetime.date, session: requests_cache.CachedSession) -> pd.Series:
    """
    Retrieves the closing prices of a list of tickers on a specific date.

    Args:
        ticker_list (list): The list of tickers.
        date (datetime.date): The date for which prices are requested.
        session (requests_cache.CachedSession): The requests cache session.

    Returns:
        pd.Series: The closing prices of the tickers.

    """
    with warnings.catch_warnings():
        warnings.simplefilter(action='ignore', category=FutureWarning)
        if requests_cache is None:
            return pdr.get_data_moex(ticker_list, date, date).set_index('SECID')['CLOSE']
        else:
            return pdr.get_data_moex(ticker_list, date, date, session=session).set_index('SECID')['CLOSE']


def moex_counter(ticker_list: list, session: requests_cache.CachedSession = None) -> pd.DataFrame:
    """
    Retrieves price changes for a list of tickers.

    Args:
        ticker_list (list): The list of tickers.
        session (requests_cache.CachedSession, optional): The requests cache session.

    Returns:
        pd.DataFrame: A DataFrame containing ticker, close price, DoD change, WoW change, MoM change, and YoY change.

    """
    today = get_nearest_work_day(datetime.datetime.now())
    dod_date = today - moex_bday
    wow_date = get_nearest_work_day(today - relativedelta(weeks=1))
    mom_date = get_nearest_work_day(today - relativedelta(months=1))
    yoy_date = get_nearest_work_day(today - relativedelta(months=12))
    today_prices = get_prices(ticker_list, today, session)
    dod_prices = get_prices(ticker_list, dod_date, session)
    wow_prices = get_prices(ticker_list, wow_date, session)
    mom_prices = get_prices(ticker_list, mom_date, session)
    yoy_prices = get_prices(ticker_list, yoy_date, session)
    dod_change = price_change(today_prices, dod_prices)
    wow_change = price_change(today_prices, wow_prices)
    mom_change = price_change(today_prices, mom_prices)
    yoy_change = price_change(today_prices, yoy_prices)
    df = pd.concat({
        'close_price': today_prices,
        'DoD': dod_change,
        'WoW': wow_change,
        'MoM': mom_change,
        'YoY': yoy_change
    }, axis=1)
    return df
