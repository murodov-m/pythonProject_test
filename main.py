#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.
"""
6. Задание:

Создать команду /me Имя, в котором в качестве ответа выводится информация принадлежности
данного имени к какой то нации (попробуйте назвать, что Ваш учитель нацист:), я больше заданий дам)
https://api.nationalize.io/?name=gayrat
"""

import telebot
import requests
import pprint
from decouple import config
import pymongo

# BOT CONFIGS
API_TOKEN = config('TOKEN')
bot = telebot.TeleBot(API_TOKEN)

# DB CONFIGS
client = pymongo.MongoClient(config('MONGO'))
db = client.test
users = db.users


def natist_g(name):
    get_natist = requests.get(f'https://api.nationalize.io/?name={name}')
    result = get_natist.json()
    x = ''
    for i in result['country']:
        country_pr = (i['country_id'], i['probability'])
        x = x + str(country_pr)
    return x


print(natist_g('Shirin'))


def bitcoin_rate():
    get_btc = requests.get('https://api.coinbase.com/v2/prices/USD/spot')
    data = get_btc.json()['data']
    for i in data:
        if i.get('base') == 'BTC':
            print(i)
            return i


def music(parametr):
    get_artist = requests.get(f'https://itunes.apple.com/search?term={parametr}&media=music&limit=10')
    data = get_artist.json()['results']
    songs = ''
    for i in data:
        songs += i['trackName'] + '\n'
    return songs

    # pprint.pprint(data)


def universities():
    get_univ = requests.get('http://universities.hipolabs.com/search?country=Uzbekistan')
    univ_str = ''
    data = get_univ.json()
    print(data)
    for num, i in enumerate(data):
        if num < 6:
            univer_site = ''
            for j in i['web_pages']:
                univer_site += j + " "
            univ_str += (f"Univer name: {i['name']}\n web_pages: "
                         f"{univer_site}" + '\n\n')
    return univ_str


# universities()
# Handle '/start' and '/help'

def user():
    get_user = requests.get('https://randomuser.me/api/')
    data = get_user.json()['results']
    full_user_data = ''
    for i in data:
        full_name = i['name']
        full_name_str = f'Name: {full_name["first"]} '
        location = i['location']
        location_str = f'Country:  {location["country"]}'
        username = i['login']['username']
        password = i['login']['password']
        login = f'Username: {username}, Password: {password}'
        full_user_data += f'{full_name_str}\n{location_str} \n{login}'
        print(full_user_data)
    return full_user_data


@bot.message_handler(commands=['user'])
def send_random_user(message):
    x = user()
    bot.send_message(message.chat.id, x)


@bot.message_handler(commands=['start'])
def send_random_user(message):
    user_id = users.find_one({"id": message.chat.id})
    if user_id:
        pass
    else:
        print(user_id)
        users.insert_one({'id': message.chat.id,
                          'name': message.from_user.first_name})
    bot.send_message(message.chat.id, "Hello")


@bot.message_handler(commands=['age'])
def send_welcome(message: telebot.types.Message):
    # keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    # keyboard.add('/btc')
    # keyboard.add('/music')
    p = bot.send_message(message.chat.id, "Вам нужно ввести минимальный возраст")
    bot.register_next_step_handler(p, set_min_reg)


@bot.message_handler(commands=['me'])
def send_random_user(message):
    # natist_name = message.from_user.first_name
    natist_name = message.text.split()[1]
    x = natist_g(natist_name)
    bot.send_message(message.chat.id, x)


def set_min_reg(message: telebot.types.Message):
    if not message.text.isdigit():
        retype = bot.send_message(message.chat.id,
                                  "Минимальный возраст должен состоять только из цифр")
        bot.register_next_step_handler(retype, set_min_reg)
    else:
        ## pass save method for this DB
        success = bot.send_message(message.chat.id, "Теперь введите максимальный возраст")
        bot.register_next_step_handler(success, set_max_age)


def set_max_age(message):
    if not message.text.isdigit():
        retype = bot.send_message(message.chat.id,
                                  "Максимальный возраст должен состоять только из цифр")
        bot.register_next_step_handler(retype, set_max_age)
    else:
        ## pass save method for this DB
        bot.send_message(message.chat.id, "Успешно сохранен")


@bot.message_handler(commands=['btc'])
def send_btc_rate(message):
    btc = bitcoin_rate()  # dict
    bot.send_message(message.chat.id, f"Bitcoint currency: {btc['amount']}")


@bot.message_handler(commands=['music'])
def send_songs(message):
    x = message.text.split()
    music_get = music(x)
    bot.send_message(message.chat.id, music_get)


@bot.message_handler(commands=['univer'])
def send_songs(message):
    univ_str = universities()
    bot.send_message(message.chat.id, univ_str, disable_web_page_preview=True)


def weather():
    get_weather = requests.get('https://www.7timer.info/bin/astro.php?lon=69.2&lat=41.3&ac=0&unit=metric&output=json')
    data = get_weather.json()
    return data['dataseries'][0]['temp2m']


@bot.message_handler(commands=['pogoda'])
def send_weather_temp(message):
    # pprint.pprint(message.json)
    # print(message.text.split())
    x = weather()  # dict
    # bitcoin_rate()
    bot.send_message(message.chat.id, f"Weather temp: {x}  {weather()}")
    print(x)


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    print(message.text)
    bot.reply_to(message, message.text)


# bot.enable_save_next_step_handlers(delay=2)
# bot.load_next_step_handlers()

bot.send_message(739327515, "Bot started")

bot.infinity_polling()
