import datetime
import pandas_datareader as pdr
import pandas as pd
from dateutil.relativedelta import relativedelta
from pandas.tseries.offsets import CustomBusinessDay

moex_holidays = [datetime.date(2023, 6, 12)]
moex_bday = CustomBusinessDay(holidays=moex_holidays)


def get_nearest_work_day(today: datetime.datetime):
    if today.weekday() in [5, 6] or today.hour < 24:
        return today - moex_bday(1)
    return today


def price_change(date_price, last_price):
    return f"{(last_price / date_price - 1) * 100:.2f}"


def moex_counter(ticker_list):
    df = pd.DataFrame({'ticker': [], 'close_price': [], 'DoD': [], 'WoW': [], 'MoM': [], 'YoY': []})
    for i in ticker_list:
        last_price, day_change, week_change, month_change, year_change = all_date_prices(i)
        df.loc[len(df.index)] = [i, last_price, day_change, week_change, month_change, year_change]
    return df


def all_date_prices(ticker):
    today = get_nearest_work_day(datetime.datetime.now())
    dod_date = today - moex_bday(1)
    wow_date = get_nearest_work_day(today - relativedelta(weeks=1))
    mom_date = get_nearest_work_day(today - relativedelta(months=1))
    yoy_date = get_nearest_work_day(today - relativedelta(months=12))
    today_price = pdr.get_data_moex(ticker, today, today)['CLOSE'].iloc[0]
    dod_price = pdr.get_data_moex(ticker, dod_date, dod_date)['CLOSE'].iloc[0]
    wow_price = pdr.get_data_moex(ticker, wow_date, wow_date)['CLOSE'].iloc[0]
    mom_price = pdr.get_data_moex(ticker, mom_date, mom_date)['CLOSE'].iloc[0]
    yoy_price = pdr.get_data_moex(ticker, yoy_date, yoy_date)['CLOSE'].iloc[0]
    day_change = price_change(dod_price, today_price)
    week_change = price_change(wow_price, today_price)
    month_change = price_change(mom_price, today_price)
    year_change = price_change(yoy_price, today_price)
    return today_price, day_change, week_change, month_change, year_change
