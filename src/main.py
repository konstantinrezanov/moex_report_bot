import datetime

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


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: types.Message):
    """
    Handles the '/start' and '/help' commands and sends a welcome message to the user.

    Args:
        message (types.Message): The received message object.

    Returns:
        None
    """
    if message.chat.id not in data_handle.get_users(db_path):
        bot.send_message(message.chat.id,
                         'Этот бот предоставляет регулярные отчеты о вашем портфеле на Московской Бирже')
        markup: ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True,
                                                                one_time_keyboard=True)
        markup.add("В 19:00", "Другое")
        msg = bot.send_message(message.chat.id,
                               'Торги на MOEX закрываются в 19:00 (по МСК). В какое время вы хотите получать отчет?',
                               reply_markup=markup)
        bot.register_next_step_handler(msg, time_select, **{"from_welcome": True})
    else:
        bot.send_message(message.chat.id,
                         "Вы уже добавляли свои данные. Чтобы изменить список тикеров, используйте команду: /update_tickers")


def time_select(message: types.Message, from_welcome=False):
    """
    Handles the user's selection of time and proceeds to update_ticker function.

    Args:
        message (types.Message): The received message object.

    Returns:
        None
    """
    if message.text == "В 19:00":
        chosen_time = (19, 0)
        data_handle.store_time(db_path, message.chat.id, chosen_time)
        bot.send_message(message.chat.id, "Время выбрано")
        if from_welcome:
            update_ticker(message)

    else:
        msg = bot.send_message(message.chat.id, "Введите желаемое время в формате 00:00")
        bot.register_next_step_handler(msg, custom_time, **{"from_welcome": from_welcome})


@bot.message_handler(commands=['update_time'])
def update_time(message: types.Message):
    markup: ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True,
                                                            one_time_keyboard=True)
    markup.add("В 19:00", "Другое")
    msg = bot.send_message(message.chat.id,
                           'Торги на MOEX закрываются в 19:00 (по МСК). В какое время вы хотите получать отчет?',
                           reply_markup=markup)
    bot.register_next_step_handler(msg, time_select)


def custom_time(message: types.Message, from_welcome=False):
    try:
        user_choice = parse_time(message.text.strip())
        data_handle.store_time(db_path, message.chat.id, user_choice)
        msg = bot.send_message(message.chat.id, "Время выбрано")
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
    """
    Handles the '/update_tickers' command and prompts the user to choose a broker for data update.

    Args:
        message (types.Message): The received message object.

    Returns:
        None
    """
    markup: ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    markup.add("Тинькофф", "БКС", "Другой брокер/загрузить собственный список")
    msg = bot.send_message(message.chat.id, "Выберете брокера из которого хотите загрузить данные:",
                           reply_markup=markup)
    bot.register_next_step_handler(msg, handle_broker_choice)


def handle_broker_choice(message: types.Message):
    """
    Handles the user's selection of a broker and proceeds to appropriate actions based on the selection.

    Args:
        message (types.Message): The received message object.
        time_choice (tuple): A tuple representing the time choice.

    Returns:
        None
    """
    if message.text == "Тинькофф":
        msg = bot.send_message(message.chat.id, "Отправьте Excel-файл с отчетом",
                               reply_markup=types.ReplyKeyboardRemove())
    elif message.text == "БКС":
        msg = bot.send_message(message.chat.id, "Отправьте Excel-файл с отчетом",
                               reply_markup=types.ReplyKeyboardRemove())
    elif message.text == "Другой брокер/загрузить собственный список":
        msg = bot.send_message(message.chat.id, "Загрузить Excel-файл с колонками ticker, type. Подробнее: ",
                               reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, custom_tickers_handler)


def custom_tickers_handler(message: types.Message):
    """
    Handles the custom tickers handler and updates tickers data based on the uploaded file.

    Args:
        message (types.Message): The received message object.
        time_choice (tuple): A tuple representing the time choice.

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
    Handles the '/get_report' command and sends the report to the user.

    Args:
        message (types.Message): The received message object.

    Returns:
        None
    """
    send_report(message.chat.id)


def send_report(user_id: int):
    """
    Retrieves the user's tickers data and sends it as a message to the user.

    Args:
        user_id (int): The ID of the user.

    Returns:
        None
    """
    user_ticker = data_handle.get_user_tickers(db_path, user_id)
    data = moex.moex_counter(user_ticker)

    bot.send_message(user_id, report.format_report(data))


def create_jobs(job_dict: dict):
    """
    Creates scheduled jobs for sending reports based on the job dictionary.

    Args:
        job_dict (dict): A dictionary containing user IDs as keys and time choices as values.

    Returns:
        None
    """
    for user_id, time in job_dict.items():
        scheduler.add_job(send_report, 'cron', hour=time[0], minute=time[1], kwargs={"user_id": user_id})


def main():
    create_jobs(data_handle.get_user_time(db_path))
    scheduler.start()
    bot.infinity_polling()


if __name__ == "__main__":
    main()
