import datetime
import pandas_datareader as pdr
import pandas as pd
from dateutil.relativedelta import relativedelta


def to_fixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"


def last_work_day():
    lastBusDay = datetime.date.today()
    if datetime.date.weekday(lastBusDay) == 5:  # if it's Saturday
        lastBusDay = lastBusDay - datetime.timedelta(days=1)  # then make it Friday
    elif datetime.date.weekday(lastBusDay) == 6:  # if it's Sunday
        lastBusDay = lastBusDay - datetime.timedelta(days=2);  # then make it Friday
    return lastBusDay


def price_change(date_price, last_price):
    if last_price >= date_price:
        output = (((last_price / date_price) - (last_price // date_price)) * 100)
        return to_fixed(output, 2)
    elif last_price < date_price:
        output = (last_price / date_price - 1) * 100
        return to_fixed(output, 2)


def moex_counter(ticker_list):
    df = pd.DataFrame({'ticker': [], 'close_price': [], 'DoD': [], 'WoW': [], 'MoM': [], 'YoY': []})
    for i in ticker_list:
        last_price, day_change, week_change, month_change, year_change = all_date_prices(i)
        df.loc[len(df.index)] = [i, last_price, day_change, week_change, month_change, year_change]
    return df


def all_date_prices(ticker):
    today = last_work_day()
    MoM_date = today - relativedelta(months=1)
    YoY_date = today - relativedelta(months=12)
    f = pdr.get_data_moex(ticker, YoY_date)
    g = pdr.get_data_moex(ticker, MoM_date)
    # cho = f['CLOSE']
    a = int(f.count()['WAVAL'])
    YoYa = f.iloc[0]['CLOSE']
    DoDa = f.iloc[a - 2]['CLOSE']
    last_price = f.iloc[a - 1]['CLOSE']
    WoWa = f.iloc[a - 6]['CLOSE']
    MoMa = g.iloc[0]['CLOSE']
    day_change = price_change(DoDa, last_price)
    week_change = price_change(WoWa, last_price)
    month_change = price_change(MoMa, last_price)
    year_change = price_change(YoYa, last_price)
    return last_price, day_change, week_change, month_change, year_change
