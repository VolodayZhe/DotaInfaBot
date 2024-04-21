import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests
import logging
import sys

TOKEN = '6272483845:AAE5bXtmGxKx5ohB6f91ZBBAxQvhOZotXVs'
DOTA_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJTdWJqZWN0IjoiN2UwYWQ4ZTEtYmMwNi00NTFkLWIzZDktYTRhMjBkMTBjODc0IiwiU3RlYW1JZCI6IjM5Nzg5Mzc1OCIsIm5iZiI6MTcxMzAxNzc5OSwiZXhwIjoxNzQ0NTUzNzk5LCJpYXQiOjE3MTMwMTc3OTksImlzcyI6Imh0dHBzOi8vYXBpLnN0cmF0ei5jb20ifQ.f45z404ZbBsKkmEhKO-z5v6b_SnO_shMDMI0bXJA5Ws'
bot = telebot.TeleBot(TOKEN)

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
    bot.send_message(message.chat.id, 'Я бот по dota 2. Просьба не спамить этому боту, так как api для этого бота даёт только 250 вызовов в минуту. Если бот не работает, то значит или идёт обновление, или его не успели занести на сервер и при этом код не запущен на пк создателя. Напишите Жоре на счёт этого.', reply_markup=keyboard)

@bot.message_handler(func=lambda x: 'Hello' in x.text)
def hello_message(message):
    bot.send_message(message.chat.id, 'Hi!')

@bot.message_handler(func=lambda s: 'Bye' in s.text)
def echo_message(message):
    bot.send_message(message.chat.id, "Bye!")

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


# Обработчики


bot.infinity_polling()
