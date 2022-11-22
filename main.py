import json
import os
import sys

import telebot
import requests
from dotenv import load_dotenv
from mako.template import Template
from telebot import types

# load variables from .env file
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
API_TOKEN = os.getenv("API_TOKEN")

BASE_CITY = "Taganrog"
BUTTONS=('Сегодня', 'На 5 дней')

bot = telebot.TeleBot(TOKEN)

# check if token provided
if len(TOKEN) == 0:
    print("Please fill up u token into .env file")
    sys.exit(1)


@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.row(types.KeyboardButton(BUTTONS[0]), types.KeyboardButton(BUTTONS[1]))
    bot.send_message(message.from_user.id, "Для того что-бы использовать бота нажимайте интрактивные кнопки в меню", reply_markup=markup)



# static data
#
fcToday = """
Погода в Таганроге на сегодня

{text} ☁️
🌤 Температура: {weather} °C
🌡Ощущается как: {feelslike_c} °C
💧 Влажность воздуха: {humidity}%
📊  Давление: {pressure} hPa
☁️  Облачность: {cloudiness}%
💨 Ветер: {wind} Км/ч

"""

fcFiveDays = """
📅 {date}:
{text}
🌡 Минимальная: {mintemp_c} - Максимальная: {maxtemp_c} °C 
"""


def single_forecast(message):
    bot.send_message(message.from_user.id, str(Weather.get_current_weather(BASE_CITY, True)))

def five_days_forecast(message):
    bot.send_message(message.from_user.id, Weather.get_five_days_forecast(BASE_CITY, True))

# handle all chat messages
@bot.message_handler(content_types=['text'])
def all_messages(message):
  if message.text == BUTTONS[0]:  
      single_forecast(message)
  elif message.text == BUTTONS[1]:
      five_days_forecast(message)

class Weather:

    '''
    https://www.weatherapi.com/api-explorer.aspx#current
    log: zsi33977@cdfaq.com
    pas: 123451qq
    apikey: 20a379ec62ae4772885101451222011
    '''

    @staticmethod
    def get_five_days_forecast(city, convert_to_message=False, days=5):
        """
        :return: Response of request if convert_to_message is False, either way a String with message
        """

        response = requests.get(f"http://api.weatherapi.com/v1/forecast.json?key=20a379ec62ae4772885101451222011&q={city}&days={days}&aqi=no&alerts=no&lang=ru")
        response_dict: dict = json.loads(response.content)
        if convert_to_message:
            message = ""

            for d in response_dict.get("forecast").get("forecastday"):
                message = message + fcFiveDays.format(date=d.get("date"), mintemp_c=d.get("day").get("mintemp_c"), maxtemp_c=d.get("day").get("maxtemp_c"), text=d.get("day").get("condition").get("text")) + "\n"
            return message
        return response.json()

    @staticmethod
    def get_current_weather(city, convert_to_message=False):
        """
        :return: Response of request if convert_to_message is False, either way a String with message
        """

        response = requests.get(f"http://api.weatherapi.com/v1/current.json?key=20a379ec62ae4772885101451222011&q={city}&aqi=no&lang=ru")
        response_dict: dict = json.loads(response.content)

        if convert_to_message:
            return fcToday.format(weather=response_dict.get("current").get("temp_c"), feelslike_c=response_dict.get("current").get("feelslike_c"), humidity=response_dict.get("current").get("humidity"), pressure=response_dict.get("current").get("pressure_mb"),
                                  cloudiness=response_dict.get("current").get("cloud"), wind=response_dict.get("current").get("wind_kph"), text=response_dict.get("current").get("condition").get("text"))
        return response.json()




# program execution entrypoint
def main():
    bot.infinity_polling()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
