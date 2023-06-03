import telebot

bot=telebot.TeleBot('6013348559:AAF1zPtGlKAeEWSAvzI3KicRG6CjpAN1Hxo', parse_mode=None)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hi")

bot.infinity_polling()