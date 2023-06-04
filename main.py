import telebot
from telebot import types
from telebot.types import ReplyKeyboardMarkup

bot = telebot.TeleBot('6013348559:AAF1zPtGlKAeEWSAvzI3KicRG6CjpAN1Hxo', parse_mode=None)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: types.Message):
    bot.send_message(message.chat.id, 'Этот бот предоставляет регулярные отчеты о вашем портфеле на Московской Бирже')


@bot.message_handler(commands=['update_tickers'])
def update_ticker(message: types.Message):
    markup: ReplyKeyboardMarkup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add("Тинькофф", "БКС", "Другой брокер/загрузить собственный список")
    msg = bot.send_message(message.chat.id, "Выберете брокера из которого хотите загрузить данные:",
                           reply_markup=markup)
    bot.register_next_step_handler(msg, handle_broker_choice)


def handle_broker_choice(message: types.Message):
    if message.text == "Тинькофф":
        bot.send_message(message.chat.id, "Отправьте Excel-файл с отчетом")
    elif message.text == "БКС":
        bot.send_message(message.chat.id, "Отправьте Excel-файл с отчетом")
    elif message.text == "Другой брокер/загрузить собственный список":
        bot.send_message(message.chat.id, "Загрузить Excel-файл с колонками ticker, type. Подробнее: ")
    else:
        bot.send_message(message.chat.id, "Выбран неверный вариант")


def main():
    bot.infinity_polling()


if __name__ == "__main__":
    main()
