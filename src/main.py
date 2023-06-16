import datetime
import pandas as pd
import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
import requests_cache
import data_handle
import ticker_update
import tempfile
import os
import moex
import report

telegram_api_key = os.getenv('TELEGRAM_API_KEY')
bot = telebot.TeleBot(telegram_api_key, parse_mode=None)

db_path = "./data/tickers.json"

jobstores = {
    "default": SQLAlchemyJobStore(url='sqlite:///jobs.sqlite'),
    "cache": MemoryJobStore()
}

scheduler = BackgroundScheduler(jobstores=jobstores)

session = requests_cache.CachedSession(cache_name="moex", backend="sqlite")


@bot.message_handler(commands=['start'])
def send_welcome(message: types.Message):
    """
    Handles the 'start' command and initializes the bot.

    Args:
        message (types.Message): The received message object.

    Returns:
        None
    """
    if message.chat.id not in data_handle.get_users(db_path):
        bot.send_message(message.chat.id,
                         """Добро пожаловать в Телеграм-бот для отслеживания акций на Московской бирже!

Этот бот разработан, чтобы помочь вам отслеживать изменение стоимости акций выбранных компаний на Московской бирже. Он предоставляет следующие функции:

1. Добавление тикеров: Вы можете добавить тикеры акций, которые вас интересуют, чтобы получать информацию о их изменении стоимости.

2. Получение отчетов: Вы можете запросить отчеты о изменении стоимости акций в выбранное вами время. Бот отправит вам информацию о коде акции, цене на начальную и конечную даты выбранного интервала и процентном изменении стоимости акции за указанный период.

3. Обновление тикеров: Если вам нужно изменить список тикеров акций, вы можете обновить его в любое время.

4. Выбор времени отчета: Вы можете выбрать время, в которое вы хотите получать регулярные отчеты об изменении стоимости акций.

Чтобы начать использовать бота, просто отправьте ему команду `/start` и следуйте инструкциям. Приятного использования!""")
        markup: ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True,
                                                                one_time_keyboard=True)
        markup.add("В 09:30", "Другое")
        msg = bot.send_message(message.chat.id,
                               'Торги на MOEX открываются в 09:30 (по МСК). В какое время вы хотите получать отчет?',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, time_select, **{"from_welcome": True})
    else:
        bot.send_message(message.chat.id,
                         "Вы уже добавляли свои данные. Чтобы изменить список тикеров, используйте команду: /update_tickers".strip())


def time_select(message: types.Message, from_welcome=False):
    """
    Handles the time selection for report delivery.

    Args:
        message (types.Message): The received message object.
        from_welcome (bool): Indicates if the function is called from the welcome message.

    Returns:
        None
    """
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
    """
    Handles the 'help' command and sends the help message.

    Args:
        message (types.Message): The received message object.

    Returns:
        None
    """
    bot.send_message(message.chat.id, """Привет! Я Телеграм-бот для отслеживания акций на Московской бирже. Вот список доступных команд:

- /start: Запуск бота и приветственное сообщение.
- /help: Получить помощь и описание доступных команд.
- /get_report: Получить отчет о изменении стоимости акций в выбранное время.
- /update_tickers: Обновить список тикеров акций.
- /update_time: Выбрать время для получения регулярных отчетов.
- /get_tickers: Получить текущий список тикеров акций.

Чтобы начать использовать бота, отправьте команду /start и следуйте инструкциям. Если у вас возникли вопросы или вам нужна дополнительная помощь, отправьте команду /help. Приятного использования!""".strip())


@bot.message_handler(commands=['update_time'])
def update_time(message: types.Message):
    """
    Handles the 'update_time' command and prompts the user to update the report delivery time.

    Args:
        message (types.Message): The received message object.

    Returns:
        None
    """
    markup: ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True,
                                                            one_time_keyboard=True)
    markup.add("В 09:30", "Другое")
    msg = bot.send_message(message.chat.id,
                           'Торги на MOEX открываются в 09:30, во сколько вы хотите получать отчет?',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, time_select)


def custom_time(message: types.Message, from_welcome=False):
    """
    Handles the custom time input for report delivery.

    Args:
        message (types.Message): The received message object.
        from_welcome (bool): Indicates if the function is called from the welcome message.

    Returns:
        None
    """
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
    """
    Parses the user-inputted time and returns a tuple of (hour, minute).

    Args:
        time_input (str): The user-inputted time in the format HH:MM.

    Returns:
        tuple: A tuple of (hour, minute).

    Raises:
        ValueError: If the time format is incorrect.
    """
    try:
        time = datetime.datetime.strptime(time_input, "%H:%M")
        return time.hour, time.minute
    except:
        raise ValueError


@bot.message_handler(commands=['update_tickers'])
def update_ticker(message: types.Message):
    """
    Handles the 'update_tickers' command and prompts the user to choose the method of updating tickers.

    Args:
        message (types.Message): The received message object.

    Returns:
        None
    """
    markup: ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    markup.add("Сообщение", "Excel-таблица")
    msg = bot.send_message(message.chat.id, "Выберете способ загрузки тикеров",
                           reply_markup=markup)
    bot.register_next_step_handler(msg, handle_broker_choice)


def handle_broker_choice(message: types.Message):
    """
    Handles the user's choice of ticker update method.

    Args:
        message (types.Message): The received message object.

    Returns:
        None
    """
    if message.text == "Сообщение":
        msg = bot.send_message(message.chat.id, "Напишите список тикеров через запятую.\nПример: SBER, VTBR",
                               reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, message_ticker_handler)
    elif message.text == "Excel-таблица":
        msg = bot.send_message(message.chat.id, "Загрузить Excel-файл с колонками ticker, type. Подробнее: ",
                               reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, custom_tickers_handler)


def message_ticker_handler(message: types.Message):
    """
    Handles the user-inputted tickers in the message format.

    Args:
        message (types.Message): The received message object.

    Returns:
        None
    """
    user_tickers = [x.upper() for x in message.text.strip().split(", ")]
    data_handle.store_tickers(db_path, message.chat.id, pd.Series(user_tickers))
    bot.send_message(message.chat.id, "Тикеры добавлены")


def custom_tickers_handler(message: types.Message):
    """
    Handles the user-inputted tickers in the custom Excel file format.

    Args:
        message (types.Message): The received message object.

    Returns:
        None
    """
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
    """
    Handles the 'get_report' command and sends the portfolio report to the user.

    Args:
        message (types.Message): The received message object.

    Returns:
        None
    """
    send_report(message.chat.id)


def send_report(user_id: int):
    """
    Sends the portfolio report to the specified user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        None
    """
    user_ticker = data_handle.get_user_tickers(db_path, user_id)
    msg = bot.send_message(user_id, "Пожалуйста, подождите...", disable_notification=True)
    data = moex.moex_counter(user_ticker)
    bot.delete_message(user_id, msg.id)
    bot.send_message(user_id, report.format_report(data))


def create_jobs(job_dict: dict):
    """
    Creates the scheduler jobs for sending regular portfolio reports.

    Args:
        job_dict (dict): A dictionary containing user IDs as keys and report delivery times as values.

    Returns:
        None
    """
    for user_id, time in job_dict.items():
        scheduler.remove_all_jobs()
        scheduler.add_job(send_report, 'cron', hour=time[0], minute=time[1], kwargs={"user_id": user_id},
                          jobstore="default")


@bot.message_handler(commands=['get_tickers'])
def get_tickers(message: types.Message):
    """
    Handles the 'get_tickers' command and sends the user's tickers.

    Args:
        message (types.Message): The received message object.

    Returns:
        None
    """
    user_tickers = data_handle.get_user_tickers(db_path, message.chat.id)
    bot.send_message(message.chat.id,
                     "Ваши тикеры:\n" + "\n".join([f"{i + 1}. {ticker}" for i, ticker in enumerate(user_tickers)]))


@bot.message_handler(commands=['get_time'])
def get_time(message: types.Message):
    """
    Handles the 'get_time' command and sends the user's report delivery time.

    Args:
        message (types.Message): The received message object.

    Returns:
        None
    """
    user_time = data_handle.get_user_time(db_path, message.chat.id)
    bot.send_message(message.chat.id, f"Время доставки отчета: {user_time[0]:02d}:{user_time[1]:02d}")

def clear_cache():
    session.cache.clear()


def main():
    data_handle.setup_db(db_path)
    scheduler.start()
    scheduler.add_job(clear_cache, "cron", hour=0, minute=0, jobstore="cache")
    bot.infinity_polling()


if __name__ == "__main__":
    main()