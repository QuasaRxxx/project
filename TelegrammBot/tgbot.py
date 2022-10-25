from datetime import datetime
import telebot
from pycbrf import ExchangeRates

bot = telebot.TeleBot('5793280474:AAGmIdy6ZNE-Ly8pp9k6sXeN8h-JCVvMnw4')


@bot.message_handler(commands=['start', 'help'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = telebot.types.KeyboardButton('USD')
    itembtn2 = telebot.types.KeyboardButton('EUR')
    markup.add(itembtn1, itembtn2)
    bot.send_message(chat_id=message.chat.id, text="<b>Hello! Chose the cyrrency to see Exchange Rates!</b>",
                     reply_markup=markup, parse_mode="html")


@bot.message_handler(content_types=['text'])
def message(message):
    message_norm = message.text.strip().lower()

    if message_norm in ['usd', 'eur']:
        rates = ExchangeRates(datetime.now())
        bot.send_message(chat_id=message.chat.id,
                         text=f"<b>{message_norm.upper()} rate is {float(rates[message_norm.upper()].rate)}</b>",
                         parse_mode="html")


bot.polling(none_stop=True)
