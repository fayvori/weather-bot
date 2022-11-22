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
bot = telebot.TeleBot(TOKEN)

# check if token provided
if len(TOKEN) == 0:
    print("Please fill up u token into .env file")
    sys.exit(1)


@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton('Current weather in Taganrog', callback_data="today"))
    markup.add(types.InlineKeyboardButton('Weather of 5 days in Taganrog', callback_data="5days"))
    bot.send_message(message.from_user.id, "Press buttons for interactions with bot", reply_markup=markup)



# static data
#
fcToday = """
Weather in Taganrog

{text} ☁️
☀ temperature: {weather} °C
🌡 feels like: {feelslike_c} °C
💧 humidity: {humidity} %
📊 pressure: {pressure} hPa
☁️ cloudiness: {cloudiness} %
💨 wind: {wind} Km\h

"""

fcFiveDays = """
📅 {date}:
{text}
🌡 Min: {mintemp_c} - Max: {maxtemp_c} °C 
"""


# format and send single forecast + menu
def single_forecast(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    todayBtn = types.InlineKeyboardButton('❮ 5 дней ❯', callback_data="today")
    markup.add(todayBtn)
    bot.send_message(message.from_user.id, fcToday, reply_markup=markup)


# handle all chat messages
@bot.message_handler(content_types=['text'])
def all_messages(message):
    # user city like: Таганрог, Москва etc. 
    single_forecast(message)


# handle callback
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # if call.data == "today":
    #     bot.send_message(call.message.chat.id, Template(fcFiveDays).render())
    if call.data == "today":
        bot.send_message(call.message.chat.id, str(Weather.get_current_weather("Taganrog", True)))
    if call.data == "5days":
        bot.send_message(call.message.chat.id, Weather.get_five_days_forcast("Taganrog", True))


class Weather:

    '''
    https://www.weatherapi.com/api-explorer.aspx#current
    log: zsi33977@cdfaq.com
    pas: 123451qq
    apikey: 20a379ec62ae4772885101451222011
    '''

    @staticmethod
    def get_five_days_forcast(city, convert_to_message=False, days=5):
        """
        :return: Response of request if convert_to_message is False, either way a String with message
        """

        response = requests.get(f"http://api.weatherapi.com/v1/forecast.json?key=20a379ec62ae4772885101451222011&q={city}&days={days}&aqi=no&alerts=no&lang=ru")
        response_dict: dict = json.loads(response.content)
        print(response_dict)
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
        print(response_dict)


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
