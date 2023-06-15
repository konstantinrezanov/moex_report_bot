import datetime
import warnings
import pandas_datareader as pdr
import pandas as pd
from dateutil.relativedelta import relativedelta
from pandas.tseries.offsets import CustomBusinessDay

moex_holidays = [datetime.date(2023, 6, 12), datetime.date(2022, 6, 12), datetime.date(2022, 6, 13),
                 datetime.date(2022, 11, 4), datetime.date(2023, 11, 4)]
moex_bday = CustomBusinessDay(holidays=moex_holidays)


def get_nearest_work_day(today: datetime.datetime) -> datetime.date:
    if today.date() in moex_holidays or today.weekday() in [5, 6] or today.hour < 24:
        return today - moex_bday
    return today


def price_change(date1: pd.Series, date2: pd.Series) -> pd.Series:
    return ((date1 / date2 - 1) * 100).round(2)


def get_prices(ticker_list: list, date: datetime.date) -> pd.Series:
    with warnings.catch_warnings():
        warnings.simplefilter(action='ignore', category=FutureWarning)
        return pdr.get_data_moex(ticker_list, date, date).set_index('SECID')['CLOSE']


def moex_counter(ticker_list: list) -> pd.DataFrame:
    df = pd.DataFrame({'ticker': [], 'close_price': [], 'DoD': [], 'WoW': [], 'MoM': [], 'YoY': []})
    today = get_nearest_work_day(datetime.datetime.now())
    dod_date = today - moex_bday
    wow_date = get_nearest_work_day(today - relativedelta(weeks=1))
    mom_date = get_nearest_work_day(today - relativedelta(months=1))
    yoy_date = get_nearest_work_day(today - relativedelta(months=12))
    today_prices = get_prices(ticker_list, today)
    dod_prices = get_prices(ticker_list, dod_date)
    wow_prices = get_prices(ticker_list, wow_date)
    mom_prices = get_prices(ticker_list, mom_date)
    yoy_prices = get_prices(ticker_list, yoy_date)
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
