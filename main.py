from deeppavlov import build_model
from deeppavlov.core.common.file import read_json
from flask import jsonify
from enum import Enum
import requests
import telebot
import json


class Modes(Enum):
    INITIAL = 1
    QUESTINGANSWERING = 2


user_states = {}

token = open("token.txt").readline().strip()
bot = telebot.TeleBot(token)



def anime_img():
    url = 'https://api.waifu.im/search'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['images'][0]['url']
    else:
        return "Неудалось получить картинку. Попробуйте позже"


def cat_img():
    domain_name = "https://cataas.com/"
    url = domain_name + "cat/says/HEY?json=true"
    response = requests.get(url)
    if response.status_code == 200:
        return domain_name + "cat/" + response.json()['_id'] + "/says/HEY"
    else:
        return "Неудалось получить изображение кота. Попробуй позже"


def naruto(question):
    url = "http://127.0.0.1:5002/"
    data = {"data": question}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()['data']
    else:
        return "Ошибка при попытке узнать о вселенной Ведьмака"

def intent_get(text):
    url = "http://127.0.0.1:5000/"
    data = {"data": text}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()['data']
    else:
        return "Ошибка при попытке узнать намерение"


@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.chat.id
    user_states[user_id] = Modes.INITIAL
    bot.reply_to(message, "Привет! Ты можешь спросить у меня о Наруто, попросить факт о кошках или картинку с котом. Просто попробуй попросить о чём-то.")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    user_id = message.chat.id
    mode = user_states.get(user_id, Modes.INITIAL)
    intent = intent_get(message.text)
    if intent == "anime_img" and mode == Modes.INITIAL:
        print("Ищу картинку")
        bot.reply_to(message, anime_img())
    elif intent == "cat_img" and mode == Modes.INITIAL:
        print("Отправляю случайное изображение")
        bot.reply_to(message, cat_img())
    elif mode == Modes.QUESTINGANSWERING and intent != "init":
        print("Отвечаю на вопрос")
        bot.reply_to(message, naruto(message.text))
    elif intent == "witcher" and mode == Modes.INITIAL:
        print("Перехожу в режим ответа на вопросы")
        user_states[user_id] = Modes.QUESTINGANSWERING
        bot.reply_to(message, "Сейчас ты можешь начать задавать мне вопросы про вселенную Ведьмака. Когда тебе надоест и ты захочешь воспользоваться другими функциями, просто скажи Хватит")
    elif intent == "init" and mode == Modes.QUESTINGANSWERING:
        print("Выхожу из режима ответа на вопросы")
        user_states[user_id] = Modes.INITIAL
        bot.reply_to(
            message, "Сейчас мы можем снова вернуться к картинкам. Если ты вышел из режима по ошибке, дай мне знать, что ты хочешь к нему вернуться")


bot.infinity_polling()
