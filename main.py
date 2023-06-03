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
    button1 = types.KeyboardButton("Тинькофф")
    button2 = types.KeyboardButton("БКС")
    button3 = types.KeyboardButton("Другой брокер/загрузить собственный список")
    markup.add(button1, button2, button3)
    bot.send_message(message.chat.id, "Выберете брокера из которого хотите загрузить данные:", reply_markup=markup)


def main():
    bot.infinity_polling()


if __name__ == "__main__":
    main()
