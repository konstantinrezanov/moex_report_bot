import datetime
import pandas as pd
import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler
import data_handle
import ticker_update
import tempfile
import os
import moex
import report

telegram_api_key = os.getenv('TELEGRAM_API_KEY')
bot = telebot.TeleBot(telegram_api_key, parse_mode=None)

db_path = "./data/tickers.json"

scheduler = BackgroundScheduler()


@bot.message_handler(commands=['start'])
def send_welcome(message: types.Message):
    if message.chat.id not in data_handle.get_users(db_path):
        bot.send_message(message.chat.id,
                         'Этот бот предоставляет регулярные отчеты о вашем портфеле на Московской Бирже')
        markup: ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True,
                                                                one_time_keyboard=True)
        markup.add("В 09:30", "Другое")
        msg = bot.send_message(message.chat.id,
                               'Торги на MOEX открываются в 09:30 (по МСК). В какое время вы хотите получать отчет?',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, time_select, **{"from_welcome": True})
    else:
        bot.send_message(message.chat.id,
                         "Вы уже добавляли свои данные. Чтобы изменить список тикеров, используйте команду: /update_tickers")


def time_select(message: types.Message, from_welcome=False):
    if message.text == "В 09:30":
        chosen_time = (9, 30)
        data_handle.store_time(db_path, message.chat.id, chosen_time)
        create_jobs(data_handle.set_jobs_dict(db_path))
        bot.send_message(message.chat.id, "Время выбрано", reply_markup=types.ReplyKeyboardRemove())
        if from_welcome:
            update_ticker(message)

    else:
        msg = bot.send_message(message.chat.id, "Введите желаемое время в формате 00:00")
        bot.register_next_step_handler(msg, custom_time, **{"from_welcome": from_welcome})


@bot.message_handler(commands=['help'])
def handle_help(message: types.Message):
    bot.send_message(message.chat.id, "Этот бот предоставляет регулярные отчеты о вашем портфеле на Московской Бирже")


@bot.message_handler(commands=['update_time'])
def update_time(message: types.Message):
    markup: ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True,
                                                            one_time_keyboard=True)
    markup.add("В 09:30", "Другое")
    msg = bot.send_message(message.chat.id,
                           'Торги на MOEX открываются в 09:30, во сколько вы хотите получать отчет?',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, time_select)


def custom_time(message: types.Message, from_welcome=False):
    try:
        user_choice = parse_time(message.text.strip())
        data_handle.store_time(db_path, message.chat.id, user_choice)
        create_jobs(data_handle.set_jobs_dict(db_path))
        msg = bot.send_message(message.chat.id, "Время выбрано", reply_markup=types.ReplyKeyboardRemove())
        if from_welcome:
            update_ticker(msg)
    except ValueError:
        msg = bot.send_message(message.chat.id, "Неверный формат времени")
        bot.register_next_step_handler(msg, custom_time, **{"from_welcome": from_welcome})


def parse_time(time_input: str) -> tuple:
    try:
        time = datetime.datetime.strptime(time_input, "%H:%M")
        return time.hour, time.minute
    except:
        raise ValueError


@bot.message_handler(commands=['update_tickers'])
def update_ticker(message: types.Message):
    markup: ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    markup.add("Сообщение", "Excel-таблица")
    msg = bot.send_message(message.chat.id, "Выберете способ загрузки тикеров",
                           reply_markup=markup)
    bot.register_next_step_handler(msg, handle_broker_choice)


def handle_broker_choice(message: types.Message):
    if message.text == "Сообщение":
        msg = bot.send_message(message.chat.id, "Напишите список тикеров через запятую.\nПример: SBER, VTBR",
                               reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, message_ticker_handler)
    elif message.text == "Excel-таблица":
        msg = bot.send_message(message.chat.id, "Загрузить Excel-файл с колонками ticker, type. Подробнее: ",
                               reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, custom_tickers_handler)


def message_ticker_handler(message: types.Message):
    user_tickers = [x.upper() for x in message.text.strip().split(", ")]
    data_handle.store_tickers(db_path, message.chat.id, pd.Series(user_tickers))
    bot.send_message(message.chat.id, "Тикеры добавлены")


def custom_tickers_handler(message: types.Message):
    if message.document.mime_type in ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                      "application/vnd.ms-excel"]:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        temp = tempfile.NamedTemporaryFile()
        with open(temp.name, "wb") as excel:
            excel.write(downloaded_file)
        ticker_update.excel_update(temp.name, db_path, message.chat.id)
        bot.send_message(message.chat.id, "Тикеры добавлены")


@bot.message_handler(commands=["get_report"])
def get_report(message: types.Message):
    send_report(message.chat.id)


def send_report(user_id: int):
    user_ticker = data_handle.get_user_tickers(db_path, user_id)
    data = moex.moex_counter(user_ticker)

    bot.send_message(user_id, report.format_report(data))


def create_jobs(job_dict: dict):
    for user_id, time in job_dict.items():
        scheduler.remove_all_jobs()
        scheduler.add_job(send_report, 'cron', hour=time[0], minute=time[1], kwargs={"user_id": user_id})


@bot.message_handler(commands=['get_tickers'])
def get_tickers(message: types.Message):
    user_tickers = data_handle.get_user_tickers(db_path, message.chat.id)
    bot.send_message(message.chat.id,
                     "Ваши тикеры:\n" + "\n".join([f"{i + 1}. {ticker}" for i, ticker in enumerate(user_tickers)]))


@bot.message_handler(commands=['get_time'])
def get_time(message: types.Message):
    user_time = data_handle.get_user_time(db_path, message.chat.id)
    bot.send_message(message.chat.id, f"Ваше время:\n {user_time[0]}:{user_time[1]}")


def main():
    data_handle.setup_db(db_path)
    create_jobs(data_handle.set_jobs_dict(db_path))
    scheduler.start()
    bot.infinity_polling()


if __name__ == "__main__":
    main()
