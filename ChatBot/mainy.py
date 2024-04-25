import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from telebot import types
import requests
import logging
import sys
import datetime
from Token import TOKEN1, TOKEN2

BOT_TOKEN = TOKEN1
DOTA_TOKEN = TOKEN2
bot = telebot.TeleBot(BOT_TOKEN)

data = {'languageId': 19}
GET_HERO_ENDPOINT = "https://api.stratz.com/api/v1/Hero"
GET_SKILL_ENDPOINT = "https://api.stratz.com/api/v1/Ability"
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
response_heroes = requests.get(GET_HERO_ENDPOINT, data=data, headers={"Authorization": f"Bearer {DOTA_TOKEN}"}).json()
del response_heroes['0']
del response_heroes['127']
names = {response_heroes[hero]['displayName']: hero for hero in response_heroes}
response_skills = requests.get(GET_SKILL_ENDPOINT, data=data, headers={"Authorization": f"Bearer {DOTA_TOKEN}"}).json()

logger = telebot.logger
formatter = logging.Formatter('[%(asctime)s] %(thread)d {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
                                  '%m-%d %H:%M:%S')
ch = logging.StreamHandler(sys.stdout)
logger.addHandler(ch)
logger.setLevel(logging.INFO)  # or use logging.INFO
ch.setFormatter(formatter)

def get_name_heroes():
    for hero in sorted(names):
        keyboard.add(KeyboardButton(hero))

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    get_name_heroes()
    bot.send_message(message.chat.id, 'Я бот по dota 2. Я выдаю информацию по героям и их способностям dota 2. Просьба не спамить этому боту, так как api для этого бота даёт только 250 вызовов в минуту.', reply_markup=keyboard)

def hello(message):
    for i in ["Hello", "Hi", "hello", "hi", "Привет", "привет", "Здравствуй", "здравствуй"]:
        if i in message.text:
            return hello_message(message, i)

def echo(message):
    for i in ["Bye", "Good Bye", "bye", "Good bye", "good bye", "Bye Bye", "bye bye", "Пока", "пока", "до свидания",
              "До свидания"]:
        if i in message.text:
            return echo_message(message, i)

@bot.message_handler(func= hello)
def hello_message(message, st):
    bot.send_message(message.chat.id, st + "!")

@bot.message_handler(func=echo)
def echo_message(message, st):
    bot.send_message(message.chat.id, st + "!")

@bot.message_handler(func=lambda x: x.text in names)
def hero_info(message):
    name = response_heroes[names[message.text]]['displayName']
    text: str = response_heroes[names[message.text]]['language']['hype']
    bot.send_message(message.chat.id, f'{name}\n{text}', parse_mode='HTML')
    logging.info(f'{message.chat.id} requested info about {name}')
    for skill in response_heroes[names[message.text]]['abilities']:
        try:
            skill_text = response_skills[str(skill['abilityId'])]['language']
            skill_text_description = ' '.join(response_skills[str(skill['abilityId'])]['language']['description'])
            skill_text_name = response_skills[str(skill['abilityId'])]['language']['displayName']
            skill_text_attributes = ' '.join(response_skills[str(skill['abilityId'])]['language']['attributes'])
            all_hero_skills = f'{skill_text_name}\n{skill_text_description}\n{skill_text_attributes}'
        except KeyError:
            continue
        try:
            bot.send_message(message.chat.id, all_hero_skills, parse_mode='HTML')
        except Exception:
            bot.send_message(message.chat.id, all_hero_skills)

@bot.message_handler(commands= ["time"])
def time(message):
    current = str(datetime.datetime.now()).split(" ")
    bot.send_message(message.chat.id, str(f'{":".join([i if len(i) <= 2 else i[:2] for i in current[1].split(":")])}'
                                          f'\n{current[0]}'))

@bot.message_handler(commands= ["more"])
def info(message):
    kb = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton(text="Ссылки", callback_data="btn1")
    btn2 = types.InlineKeyboardButton(text="Медиа", callback_data="btn2")
    kb.add(btn1, btn2)
    bot.send_message(message.chat.id, "Дополнительные функции", reply_markup=kb)

@bot.callback_query_handler(func=lambda callback: callback.data)
def check_callback(callback):
    if callback.data == "btn1":
        links(callback.message)
    elif callback.data == "btn2":
        media(callback.message)

def links(message):
    kb = types.InlineKeyboardMarkup(row_width=3)
    btn3 = types.InlineKeyboardButton(text="Официальный сайт Dota 2", url="https://www.dota2.com/home")
    btn4 = types.InlineKeyboardButton(text="API_STRATZ", url="https://stratz.com/api")
    kb.add(btn3, btn4)
    bot.send_message(message.chat.id, "Полезные ссылки", reply_markup=kb)

def media(message):
    file1 = open("img.png", "rb")
    file2 = open("img_1.png", "rb")
    bot.send_photo(message.chat.id, file1)
    bot.send_photo(message.chat.id, file2)
# Обработчики

bot.infinity_polling()