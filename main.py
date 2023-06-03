import telebot
from telebot import types

bot = telebot.TeleBot('6013348559:AAF1zPtGlKAeEWSAvzI3KicRG6CjpAN1Hxo', parse_mode=None)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: types.Message):
    bot.send_message(message.chat.id, 'Этот бот предоставляет регулярные отчеты о вашем портфеле на Московской Бирже')


def main():
    bot.infinity_polling()


if __name__ == "__main__":
    main()
