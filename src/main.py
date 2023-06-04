import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup
from apscheduler.schedulers.background import BackgroundScheduler
import data_handle
import ticker_update
import tempfile
import os

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
        bot.register_next_step_handler(msg, time_select)


def time_select(message: types.Message):
    """
    Handles the user's selection of time and proceeds to update_ticker function.

    Args:
        message (types.Message): The received message object.

    Returns:
        None
    """
    if message.text == "В 19:00":
        chosen_time = (19, 0)
    else:
        chosen_time = (0, 0)
    bot.send_message(message.chat.id, "Время выбрано", reply_markup=types.ReplyKeyboardRemove())
    update_ticker(message, chosen_time)


@bot.message_handler(commands=['update_tickers'])
def update_ticker(message: types.Message, time_choice: tuple = None):
    """
    Handles the '/update_tickers' command and prompts the user to choose a broker for data update.

    Args:
        message (types.Message): The received message object.
        time_choice (tuple, optional): A tuple representing the time choice. Defaults to None.

    Returns:
        None
    """
    if time_choice is None:
        time_choice = data_handle.get_user_time(db_path)[message.chat.id]
    markup: ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
    markup.add("Тинькофф", "БКС", "Другой брокер/загрузить собственный список")
    msg = bot.send_message(message.chat.id, "Выберете брокера из которого хотите загрузить данные:",
                           reply_markup=markup)
    bot.register_next_step_handler(msg, handle_broker_choice, **{"time_choice": time_choice})


def handle_broker_choice(message: types.Message, time_choice: tuple):
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
        bot.register_next_step_handler(msg, custom_tickers_handler, **{"time_choice": time_choice})


def custom_tickers_handler(message: types.Message, time_choice: tuple):
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
        ticker_update.excel_update(temp.name, db_path, message.chat.id, time_choice)


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
    data = data_handle.get_user_tickers(db_path, user_id)
    bot.send_message(user_id, str(data))


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
