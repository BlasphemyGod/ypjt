# coding: utf8

import logging  # Логгинг
import telebot  # API Telegram-бота
from telebot import types
import sqlite3  # Базы данных
import schedule  # Планировщик периодических заданий
import json  # Работа с JSON-файлами
import time  # Время
from multiprocessing import Process  # Мультипроцессы
from random import choice  # Случайности не случайны
from datetime import datetime  # Определение времени
from pytz import timezone, utc  # Часовые пояса
from timezonefinder import TimezoneFinder  # Поиск часового пояса
import apiai  # Искусственный интеллект
from messages import *  # Слишком длинные сообщения, стикеры, челенджи
from config import *  # Токенчики мои ненаглядные

"""
                                         Подгтовка к запуску
"""
# настройка логов
logging.getLogger('schedule').propagate = False  # ненавижу schedule(он шлёт логги INFO)
logging.basicConfig(filename='couch.log')  # запись логов
logging.basicConfig(level=logging.DEBUG)

# создание экземпляра класса TimezoneFinder(это очевидно, но тут почти все комментарии такие)
tf = TimezoneFinder()

# открытие json
with open('training.json') as f:
    json_data = json.load(f)

# проверка json
if not json_data:
    logging.fatal('Json is empty')
    raise Exception  # без json он не будет работать, значит сразу кладём

# Токен стесняется, не смотрите
bot = telebot.TeleBot(BOT_TOKEN)

# цена за абонемент(это в копейках если что)
PRICE = types.LabeledPrice(label='Абонемент', amount=12000)

# разнообразные списки и словари
list_of_stickers = [sticker_brain, sticker_car, sticker_fingers, sticker_poster, sticker_stupid, sticker_surprised,
                    sticker_angry, sticker_hey_you, sticker_really, sticker_sad]

list_of_time_zones = ["-11", "-10", "-9", "-8", "-7", "-6", "-5", "-4", "-3", "-2", "-1", "0", "+1", "+2", "+3", "+4",
                      "+5", "+6", "+7", "+8", "+9", "+10", "+11", "+12"]
list_of_phrases = ["Красавчик!", "Молодчина!", "Так держать!", "Огонь!", "Чётко!"]

dict_of_talks = {'greeting': 'разобрались как мне тебя называть',
                 'exercises': 'определились с твоими упражнениями', 'date_time': 'утвердили твоё расписание',
                 'training': 'закончили тренировку'}

dict_of_exercises = {"Отжимания": [0, 24], "Приседания": [0, 24], "Подтягивания": [0, 24], "Планка": [0, 24],
                     "Поднимание ног": [0, 24]}

days = {"понедельник": "Monday", "вторник": "Tuesday", "среда": "Wednesday", "четверг": "Thursday",
        "пятница": "Friday",
        "суббота": "Saturday", "воскресенье": "Sunday"}

list_of_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

format_date = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}

# огромное колличество клавиатур для удобства
keyboard_exercise = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_exercise.add('Отжимания')
keyboard_exercise.add('Приседания')
keyboard_exercise.add('Подтягивания')
keyboard_exercise.add('Планка')
keyboard_exercise.add('Поднимание ног')

keyboard_ask_timezone = telebot.types.ReplyKeyboardMarkup()
keyboard_ask_timezone.add(telebot.types.KeyboardButton('Отправить геолокацию', request_location=True))
keyboard_ask_timezone.add(telebot.types.KeyboardButton('Выбрать самому'))

keyboard_time_zone = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_time_zone.row("+1", "+2", "+3", "+4", "+5", "+6")
keyboard_time_zone.row("+7", "+8", "+9", "+10", "+11", "+12")
keyboard_time_zone.row('0', "-1", "-2", "-3", "-4", "-5")
keyboard_time_zone.row("-6", "-7", "-8", "-9", "-10", "-11")

keyboard_change = telebot.types.ReplyKeyboardMarkup()
keyboard_change.add("Добавить")
keyboard_change.add("Изменить")

keyboard_noyes = telebot.types.ReplyKeyboardMarkup()
keyboard_noyes.add("Да", "Нет")

keyboard_num = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_num.add("8", "16", "18", "24", "32", "40", "48", "56", "64", "72", "80", "88", "96", "104", "112")

keyboard_num_strap = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_num_strap.add("15", "30", "45", "60", "75", "90", "105", "120", "135", "150", "165", "180", "195", "210",
                       "225")

keyboard_pull = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_pull.add("1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15")

keyboard_time = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_time.row('4:00', '4:30', '5:00', '5:30', '6:00', '6:30')
keyboard_time.row('7:00', '7:30', '8:00', '8:30', '9:00', '9:30')
keyboard_time.row('10:00', '10:30', '11:00', '11:30', '12:00', '12:30')
keyboard_time.row('13:00', '13:30', '14:00', '14:30', '15:00', '15:30')
keyboard_time.row('16:00', '16:30', '17:00', '17:30', '18:00', '18:30')
keyboard_time.row('19:00', '19:30', '20:00', '20:30', '21:00', '21:30')
keyboard_time.row('22:00', '22:30', '23:00', '23:30', '00:00', '00:30')
keyboard_time.row('1:00', '1:30', '2:00', '2:30', '3:00', '3:30')

keyboard_days = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_days.add("Понедельник", "Вторник")
keyboard_days.add("Среда", "Четверг")
keyboard_days.add("Пятница", "Суббота")
keyboard_days.add("Воскресенье")
keyboard_days.add("На этом хватит")

keyboard_first_days = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_first_days.add("Понедельник", "Вторник")
keyboard_first_days.add("Среда", "Четверг")
keyboard_first_days.add("Пятница", "Суббота")
keyboard_first_days.add("Воскресенье")

keyboard_training = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_training.add('Выполнил')
keyboard_training.add('Увеличить кол-во упражнений')
keyboard_training.add('Слишком тяжело')
keyboard_training.add('Очень легко')
keyboard_training.add('Закончить тренировку')

keyboard_main = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_main.add("Хочу заниматься")
keyboard_main.add("Купить абонемент")
keyboard_main.add("Показать расписание")
keyboard_main.add("Сменить упражнения")
keyboard_main.add("Сменить расписание")
keyboard_main.add("Называй меня по другому")
keyboard_main.add("Изменить часовой пояс")

keyboard_main_premium = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_main_premium.add("Хочу челендж")
keyboard_main_premium.add("Хочу заниматься")
keyboard_main_premium.add("Показать расписание")
keyboard_main_premium.add("Сменить упражнения")
keyboard_main_premium.add("Сменить расписание")
keyboard_main_premium.add("Называй меня по другому")
keyboard_main_premium.add("Изменить часовой пояс")

keyboard_answer = types.InlineKeyboardMarkup()
key_yes = types.InlineKeyboardButton(text='Готов заниматься', callback_data='yes')
keyboard_answer.add(key_yes)
key_no = types.InlineKeyboardButton(text='Нет возможности', callback_data='no')
keyboard_answer.add(key_no)

keyboard_challenge = types.InlineKeyboardMarkup()
key_done = types.InlineKeyboardButton(text='Выполнил!', callback_data='done')
keyboard_challenge.add(key_done)
key_did_not = types.InlineKeyboardButton(text='Не получилось', callback_data='did_not')
keyboard_challenge.add(key_did_not)
"""
                                        Классы
"""


# ошибка если юзер отвечает на вопросы некоректно
class YesNoError(Exception):
    pass


# ошибка при неправильном вводе дня недели(там есть варианты, но стоит перестраховаться)
class WeekdayError(Exception):
    pass


# ошибка неверного формата времени
class TimeFormatError(Exception):
    pass


# ошибка некоректно введённого времени(например 25:61)
class TimeError(Exception):
    pass


# ошибка выбора отрицательного кол-ва упражниний
class ExerciseFormatError(Exception):
    pass


# ошибка выбора нулевого кол-ва упражниний
class ZeroError(Exception):
    pass


# ошибка возникающая при попытке уменьшения кол-ва упражниний если оно может стать отрицательным или равным 0
class TooLittle(Exception):
    pass


# ошибка возникающая при попытке ввода времени если минуты не кратны 5 (например 14:41)
class DivFiveError(Exception):
    pass


# ошибка при попытке ввода пустого имени
class BlankName(Exception):
    pass


# ошибка регистрации
class RegError(Exception):
    pass


# класс для хранения информации о юзере
class User:
    def __init__(self, user_name, training_type, date_and_time, time_zone, sub):
        self.user_name = user_name  # имя пользователя
        if training_type:  # тип тренировки
            self.training_type = eval(training_type)
        else:
            self.training_type = dict()
        if date_and_time:  # расписание
            self.date_and_time = eval(date_and_time)
        else:
            self.date_and_time = dict()
        self.change_data = dict()  # смена расписания
        self.change_training = dict()  # смена тренировки
        self.timezone = time_zone  # часоввой пояс
        self.pref_timezone = time_zone  # предыдущий часовой пояс(для переписывания расписания)
        self.day = ""  # день тренировки
        self.sub = sub  # наличие подписки
        self.conversation = ""  # тема диалога
        self.conversation_power = 0  # прогресс диалога
        self.first = False  # зашёл ли юзер в первый раз
        self.num = []  # названия упражниний пользователя
        self.training = []  # прогресс тренировки
        self.challenge = True  # можно ли взять челендж


"""
                                        Вычислительные функции
"""


# функция которая возращает клавиатуру с учётом статуса пользователя
def keyboard(user):
    if user.sub:
        return keyboard_main_premium
    return keyboard_main


# функция геокодера (получает координаты и возращает часовой пояс)
def get_offset(*, lat, lng):
    try:
        today = datetime.now()
        tz_target = timezone(tf.certain_timezone_at(lng=lng, lat=lat))
        today_target = tz_target.localize(today)
        today_utc = utc.localize(today)
        return (today_utc - today_target).total_seconds() / 60
    except Exception as geo_error:
        logging.error("geo error {}".format(geo_error.__class__.__name__))
        return 3  # если что то пойдёт не так, то он вернёт часовой пояс +3 авось попадёт


# функция возращающая время в понятном программе формате(с эти временем столько проблем)
def time_format(hour_minute):
    hour_minute = hour_minute.split(":")
    hour, minute = [int(i) for i in hour_minute]
    if 0 <= hour < 24 and 0 <= minute <= 59:
        if minute % 5 != 0:
            raise DivFiveError  # описания ошибок находятся выше
        if hour < 10:
            hour = "0" + str(hour)
        if minute < 10:
            minute = "0" + str(minute)
        hour_minute = [str(hour), str(minute)]
        return hour_minute
    else:
        raise TimeError  # описания ошибок находятся выше


# функция проверяющая выбранные упражниния и запиывающая изменения в БД
def training_update(tel_id):
    training = dictionary_of_users[tel_id].change_training
    try:
        if training.keys():  # если список упражниний не пуст
            dictionary_of_users[tel_id].training_type = training
            dictionary_of_users[tel_id].change_training = dict()
            con = sqlite3.connect("data.db")  # запись в бд
            cur = con.cursor()
            cur.execute(
                """UPDATE table_name SET training_type = "{}" WHERE user_id = {}""".format(training, tel_id))
            con.commit()
            con.close()
            return True
        else:
            return False
    except Exception as training_update_error:
        logging.error('training_update_error {}'.format(training_update_error.__class__.__name__))
        return False


# отлов исключений связанных со смещением дня недели из-за часового пояса
def day_exception(hour, day):
    if int(hour) < 0:
        if day != 'Monday':
            day = list_of_days[day.index(day) - 1]
        else:
            day = 'Sunday'
        hour = str(24 + int(hour))
    elif int(hour) > 23:
        if day != 'Sunday':
            day = list_of_days[day.index(day) + 1]
        else:
            day = 'Monday'
        hour = str(int(hour) - 24)
    if int(hour) < 10:
        hour = "0" + str(int(hour))
    return hour, day


# обновление часового пояса в БД и json
def timezone_update(tel_id):
    user = dictionary_of_users[tel_id]
    global json_data
    user_data = user.date_and_time
    logging.debug('timezone refreshing')  # уведомление о начале смены часового пояса
    if user.pref_timezone != user.timezone:  # если часовой изменился
        try:  # эта огромная штука обновляет данные(кажется что можно сделать короче, но это не так)
            for many_data in user_data.keys():
                day = days[many_data]
                for data in user_data[many_data]:
                    hour, minute = str(int(data[0]) - user.pref_timezone), data[1]
                    hour, day = day_exception(hour, day)
                    if hour in json_data[day]["Time"]["Hours"]:
                        if minute in json_data[day]["Time"]["Hours"][hour]["minutes"]:
                            if tel_id in json_data[day]["Time"]["Hours"][hour]["minutes"][minute]:
                                json_data[day]["Time"]["Hours"][hour]["minutes"][minute].remove(tel_id)
                                if not json_data[day]["Time"]["Hours"][hour]["minutes"][minute]:
                                    del json_data[day]["Time"]["Hours"][hour]["minutes"][minute]
            logging.debug('Deleting timezone json completed')  # уведомление об успешном удалении старых данных

            for many_data in user_data.keys():
                day = days[many_data]
                for data in user_data[many_data]:
                    hour, minute = str(int(data[0]) - user.timezone), data[1]
                    hour, day = day_exception(hour, day)
                    if hour in json_data[day]["Time"]["Hours"]:
                        if minute in json_data[day]["Time"]["Hours"][hour]["minutes"]:
                            json_data[day]["Time"]["Hours"][hour]["minutes"][minute].append(tel_id)
                        else:
                            json_data[day]["Time"]["Hours"][hour]["minutes"][minute] = [tel_id]
                    else:
                        json_data[day]["Time"]["Hours"][hour] = {'minutes': {minute: [tel_id]}}
            logging.debug('Refreshing timezone json completed')  # уведомление об успешном оновлении данных
            file = open("training.json", 'w')  # открытие json для записи
            a = json.dumps(json_data, ensure_ascii=False, sort_keys=True, indent=4)
            file.write(a)
            file.close()
            dictionary_of_users[tel_id].pref_timezone = user.timezone
            logging.debug('Refresh timezone completed')  # уведомление об успешное обновление json и бд
        except Exception as time_zone_error:
            logging.error('timezone_update {}'.format(time_zone_error.__class__.__name__))


# обновление расписания занятий в БД и json
def timetable_update(tel_id):
    global json_data
    users_data = dictionary_of_users[tel_id].change_data
    prev_data = dictionary_of_users[tel_id].date_and_time
    logging.debug('timetable refreshing')  # уведомление о начале смены расписания
    try:
        for many_data in prev_data.keys():
            day = days[many_data]
            for data in prev_data[many_data]:
                hour, minute = str(int(data[0]) - dictionary_of_users[tel_id].timezone), data[1]
                hour, day = day_exception(hour, day)
                if hour in json_data[day]["Time"]["Hours"]:
                    if minute in json_data[day]["Time"]["Hours"][hour]["minutes"]:
                        if tel_id in json_data[day]["Time"]["Hours"][hour]["minutes"][minute]:
                            json_data[day]["Time"]["Hours"][hour]["minutes"][minute].remove(tel_id)
                            if not json_data[day]["Time"]["Hours"][hour]["minutes"][minute]:
                                del json_data[day]["Time"]["Hours"][hour]["minutes"][minute]
        logging.debug('Delete completed')  # уведомление об успешном удалении старых данных

        for many_data in users_data.keys():
            day = days[many_data]
            for data in users_data[many_data]:
                hour, minute = str(int(data[0]) - dictionary_of_users[tel_id].timezone), data[1]
                hour, day = day_exception(hour, day)

                if hour in json_data[day]["Time"]["Hours"]:
                    if minute in json_data[day]["Time"]["Hours"][hour]["minutes"]:
                        json_data[day]["Time"]["Hours"][hour]["minutes"][minute].append(tel_id)
                    else:
                        json_data[day]["Time"]["Hours"][hour]["minutes"][minute] = [tel_id]
                else:
                    json_data[day]["Time"]["Hours"][hour] = {'minutes': {minute: [tel_id]}}

        logging.debug("Refresh timetable json completed")  # уведомление об успешном оновлении данных
        file = open("training.json", 'w')  # открытие json для записи
        a = json.dumps(json_data, ensure_ascii=False, sort_keys=True, indent=4)
        file.write(a)
        file.close()
        dictionary_of_users[tel_id].date_and_time = users_data
        con = sqlite3.connect("data.db")  # запись в бд
        cur = con.cursor()
        cur.execute(
            """UPDATE table_name SET date_and_time = "{}" WHERE user_id = {}""".format(
                str(users_data), tel_id))
        con.commit()
        con.close()
        logging.debug("Refresh timetable completed")  # уведомление об успешное обновление json и бд
    except Exception as timetable_update_error:
        logging.error('timetable_update {}'.format(timetable_update_error))


# обновление словаря юзеров
def dictionary_update():
    global dictionary_of_users
    con = sqlite3.connect("data.db")  # запись в бд
    cur = con.cursor()
    result = cur.execute("SELECT * FROM table_name").fetchall()
    con.close()
    for info in result:
        if info[0] not in dictionary_of_users.keys():  # создание словаря экземпляров класса User(ключ - id в телеграме)
            dictionary_of_users[info[0]] = User(*info[1:])


# создание и заполнение словаря пользователей
dictionary_of_users = {}
dictionary_update()

"""
                                        Диалоговые функции
"""


# диалог по упражнениям
def exercise_talking(message, user):
    try:
        if user.conversation_power == 0:
            if message.text.lower() == "да":  # если пользователь зочет отжиматься, то бот спрашивает сколько раз..
                user.conversation_power = 1
                bot.send_message(message.chat.id, 'Сколько раз ты отжимаешься?', reply_markup=keyboard_num)
            elif message.text.lower() == "нет":  # если не хочет, то следующий вопрос
                user.conversation_power = 2
                bot.send_message(message.chat.id, 'Ты хочешь приседать?', reply_markup=keyboard_noyes)
            else:
                raise YesNoError  # описания ошибок находятся выше

        elif user.conversation_power == 1:
            if int(message.text) == 0:
                raise ZeroError  # описания ошибок находятся выше
            if int(message.text) < 0:
                raise ExerciseFormatError  # описания ошибок находятся выше
            user.change_training["Отжимания"] = int(message.text)
            user.conversation_power = 2
            bot.send_message(message.chat.id, 'Ты хочешь приседать?', reply_markup=keyboard_noyes)

        elif user.conversation_power == 2:
            if message.text.lower() == "да":
                user.conversation_power = 3
                bot.send_message(message.chat.id, 'Сколько раз ты приседаешь?', reply_markup=keyboard_num)
            elif message.text.lower() == "нет":
                user.conversation_power = 4
                bot.send_message(message.chat.id, 'Ты хочешь подтягиваться?', reply_markup=keyboard_noyes)
            else:
                raise YesNoError  # описания ошибок находятся выше

        elif user.conversation_power == 3:
            if int(message.text) == 0:
                raise ZeroError  # описания ошибок находятся выше
            if int(message.text) < 0:
                raise ExerciseFormatError  # описания ошибок находятся выше
            user.change_training["Приседания"] = int(message.text)
            user.conversation_power = 4
            bot.send_message(message.chat.id, 'Ты хочешь подтягиваться?', reply_markup=keyboard_noyes)

        elif user.conversation_power == 4:
            if message.text.lower() == "да":
                user.conversation_power = 5
                bot.send_message(message.chat.id, 'Сколько раз ты подтягиваешься?', reply_markup=keyboard_pull)
            elif message.text.lower() == "нет":
                user.conversation_power = 6
                bot.send_message(message.chat.id, 'Ты хочешь делать планку?', reply_markup=keyboard_noyes)
            else:
                raise YesNoError  # описания ошибок находятся выше

        elif user.conversation_power == 5:
            if int(message.text) == 0:
                raise ZeroError  # описания ошибок находятся выше
            if int(message.text) < 0:
                raise ExerciseFormatError  # описания ошибок находятся выше
            user.change_training["Подтягивания"] = int(message.text)
            user.conversation_power = 6
            bot.send_message(message.chat.id, 'Ты хочешь делать планку?', reply_markup=keyboard_noyes)

        elif user.conversation_power == 6:
            if message.text.lower() == "да":
                user.conversation_power = 7
                bot.send_message(message.chat.id, 'Сколько секунд ты держишь планку?', reply_markup=keyboard_num_strap)
            elif message.text.lower() == "нет":
                user.conversation_power = 8
                bot.send_message(message.chat.id, 'Ты хочешь поднимать ноги?', reply_markup=keyboard_noyes)
            else:
                raise YesNoError  # описания ошибок находятся выше

        elif user.conversation_power == 7:
            if int(message.text) == 0:
                raise ZeroError  # описания ошибок находятся выше
            if int(message.text) < 0:
                raise ExerciseFormatError  # описания ошибок находятся выше
            user.change_training["Планка"] = int(message.text)
            user.conversation_power = 8
            bot.send_message(message.chat.id, 'Ты хочешь поднимать ноги?', reply_markup=keyboard_noyes)

        elif user.conversation_power == 8:
            if message.text.lower() == "да":
                user.conversation_power = 9
                bot.send_message(message.chat.id, 'Сколько раз ты поднимаешь ноги?', reply_markup=keyboard_num)
            elif message.text.lower() == "нет":
                if training_update(message.from_user.id):
                    if user.first:
                        user.conversation_power = 0
                        user.conversation = "date_time"  # диалог о расписании
                        user.change_data = dict()
                        bot.send_message(message.chat.id, 'В какой день тебе удобно заниматься?',
                                         reply_markup=keyboard_first_days)
                    else:
                        bot.send_sticker(message.chat.id, sticker_brain)
                        bot.send_message(message.chat.id, 'Я запомнил', reply_markup=keyboard(user))
                        user.conversation_power = 0
                        user.conversation = ""  # выход из диалога
                else:
                    bot.send_sticker(message.chat.id, sticker_angry)
                    bot.send_message(message.chat.id, 'Выбери хотя бы одно упражнение')
                    bot.send_message(message.chat.id, 'Ты хочешь отжиматься?', reply_markup=keyboard_noyes)
                    user.conversation = 'exercises'
                    user.conversation_power = 0

            else:
                raise YesNoError  # описания ошибок находятся выше

        elif user.conversation_power == 9:
            if int(message.text) == 0:
                raise ZeroError  # описания ошибок находятся выше
            if int(message.text) < 0:
                raise ExerciseFormatError  # описания ошибок находятся выше
            user.change_training["Поднимание ног"] = int(message.text)
            user.conversation_power = 0

            if training_update(message.from_user.id):
                if user.first:
                    user.conversation_power = 0
                    user.conversation = "date_time"  # диалог о расписании
                    user.change_data = dict()  # пустой словарь для записи новых данных
                    bot.send_message(message.chat.id, 'Когда хочешь заниматься?',
                                     reply_markup=keyboard_first_days)
                else:
                    bot.send_sticker(message.chat.id, sticker_brain)
                    bot.send_message(message.chat.id, 'Я запомнил', reply_markup=keyboard(user))
                    user.conversation_power = 0
                    user.conversation = ""  # выход из диалога
            else:
                bot.send_sticker(message.chat.id, sticker_stupid)
                bot.send_message(message.chat.id, 'Серьёзно? Выбери хотя бы одно упражнение')
                bot.send_message(message.chat.id, 'Ты хочешь отжиматься?', reply_markup=keyboard_num)
                user.conversation = 'exercises'
                user.conversation_power = 0
    except ValueError:
        bot.send_sticker(message.chat.id, sticker_angry)
        bot.send_message(message.chat.id, 'Отвечай внятно')


# диалог тренировки
def exercise(tel_id):
    user = dictionary_of_users[tel_id]
    if user.num:  # если остались несделанные упражниния
        if 'Отжимания' in user.num:
            bot.send_message(tel_id, 'Отожмись {} раз'.format(user.training_type['Отжимания']),
                             reply_markup=keyboard_training)
            user.training = 'Отжимания'
        elif 'Приседания' in user.num:
            bot.send_message(tel_id, 'Присядь {} раз'.format(user.training_type['Приседания']),
                             reply_markup=keyboard_training)
            user.training = 'Приседания'
        elif 'Подтягивания' in user.num:
            bot.send_message(tel_id, 'Подтянись {} раз'.format(user.training_type['Подтягивания']),
                             reply_markup=keyboard_training)
            user.training = 'Подтягивания'
        elif 'Планка' in user.num:
            bot.send_message(tel_id, 'Держи планку {} секунд'.format(user.training_type['Планка']),
                             reply_markup=keyboard_training)
            user.training = 'Планка'
        elif 'Поднимание ног' in user.num:
            bot.send_message(tel_id, 'Подними ноги {} раз'.format(user.training_type['Поднимание ног']),
                             reply_markup=keyboard_training)
            user.training = 'Поднимание ног'

        user.num.remove(user.training)  # сделанное упражниние удаляется и списка
    else:
        con = sqlite3.connect("data.db")  # обновление кол-ва упражниний юзера после тренировки
        cur = con.cursor()
        cur.execute(
            """UPDATE table_name SET training_type = "{}" WHERE user_id = {}""".format(user.training_type, tel_id))
        con.commit()
        con.close()
        logging.debug('{} completed training'.format(user.user_name))
        bot.send_message(tel_id, 'Отличная была тренировка', reply_markup=keyboard(user))
        user.conversation = ''  # выход из диалога


"""
                                        Функции рассылки
"""


# рассылка напоминаний о тренировках
def mailing(users):
    for tel_id in users:
        bot.send_sticker(tel_id, sticker_hey_you)
        bot.send_message(tel_id, 'Пора заниматься', reply_markup=keyboard_answer)


# проверка времени для рассылки
def act():
    try:
        if datetime.now().minute % 5 == 0:
            hour = str(datetime.now().hour % 24)
            minute = str(datetime.now().minute)
            day = format_date[datetime.now().weekday()]
            if int(hour) < 10:
                hour = "0" + str(int(hour))
            if int(minute) < 10:
                minute = "0" + str(int(minute))
            with open('training.json') as file:  # обновление json
                data = json.load(file)
            if hour in data[day]["Time"]["Hours"]:
                if minute in data[day]["Time"]["Hours"][hour]["minutes"]:
                    mailing(data[day]["Time"]["Hours"][hour]["minutes"][minute])
    except Exception as act_error:
        logging.error('sending error {}'.format(act_error.__class__.__name__))


# процесс проверки времени
def check_time():
    while True:
        schedule.run_pending()
        # пауза между проверками, чтобы не загружать процессор
        time.sleep(60)


# создание процесса
p1 = Process(target=check_time, args=())

# ежеминутный запуск функции act
schedule.every().minute.do(act)

"""
                                        Хэндлеры
"""


# самое первое и самое волнительное сообщение
@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        tel_id = message.from_user.id
        if tel_id not in dictionary_of_users.keys():
            con = sqlite3.connect("data.db")  # запись юзера в бд
            cur = con.cursor()
            cur.execute(
                """INSERT INTO table_name (user_id, sub) VALUES ({}, 0)""".format(tel_id))
            con.commit()
            con.close()
            bot.send_message(message.chat.id, 'Как тебя звать?')
            dictionary_update()
            dictionary_of_users[tel_id].first = True  # юзер впервые запустил бота(его ждёт обучение)
            dictionary_of_users[tel_id].conversation = "greeting"  # диалог приветствия
            dictionary_of_users[tel_id].conversation_power = 1  # степень диалога
            logging.info('New user')
        else:  # если пользователь уже зарегистрирован
            if dictionary_of_users[tel_id].user_name:
                bot.send_message(message.chat.id, 'Мы встречались, {}'.format(dictionary_of_users[tel_id].user_name),
                                 reply_markup=keyboard(dictionary_of_users[tel_id]))
    except Exception as start_error:
        logging.error('/start {}'.format(start_error.__class__.__name__))


# все основные сообщения идут сюда
@bot.message_handler(content_types=['text', 'location'])
def send_text(message):
    tel_id = message.from_user.id  # id пользователя
    try:
        if tel_id not in dictionary_of_users.keys():
            raise RegError  # описания ошибок находятся выше
        user = dictionary_of_users[tel_id]
        if user.conversation == "greeting":  # диалог приветствия
            if user.conversation_power == 1:
                if not message.text:
                    raise BlankName  # описания ошибок находятся выше
                if user.first:  # если юзер зашёл в первый раз
                    bot.send_message(tel_id,
                                     'Я буду звать тебя {}'.format(message.text))
                    user.user_name = message.text
                    user.conversation = 'time_zone'  # включается диалог о часовом поясе
                    user.conversation_power = 0
                    bot.send_message(tel_id, 'Какой у тебя часовой пояс?', reply_markup=keyboard_ask_timezone)
                else:
                    bot.send_message(tel_id,
                                     'Я буду звать тебя {}'.format(message.text), reply_markup=keyboard(user))
                    user.user_name = message.text
                    user.conversation_power = 0
                    user.conversation = ""  # выход из диалога
                con = sqlite3.connect("data.db")  # запись в бд
                cur = con.cursor()
                cur.execute(
                    """UPDATE table_name SET user_name = "{}" WHERE user_id = {}""".format(message.text, tel_id))
                con.commit()
                con.close()
        elif user.conversation == "time_zone":  # диалог о часовом поясе
            try:
                if user.conversation_power == 0:
                    if message.location:  # если юзер послал своё местоположение
                        loc = {'lat': message.location.latitude, 'lng': message.location.longitude}
                        hour_offset = int(get_offset(**loc) // 60)
                        if hour_offset <= 0:
                            bot.send_message(tel_id, 'Ты живёшь в часовом поясе UTC {}?'.format(hour_offset),
                                             reply_markup=keyboard_noyes)
                        else:
                            bot.send_message(tel_id, 'Ты живёшь в часовом поясе UTC +{}?'.format(hour_offset),
                                             reply_markup=keyboard_noyes)
                        user.conversation_power = 1
                        user.timezone = hour_offset
                    elif message.text.lower() == 'выбрать самому':
                        bot.send_message(tel_id, 'Ну тогда выбирай', reply_markup=keyboard_time_zone)
                        user.conversation_power = 2
                elif user.conversation_power == 1:
                    if message.text.lower() == 'нет':
                        bot.send_message(tel_id, 'Ну тогда выбирай', reply_markup=keyboard_time_zone)
                        logging.warning('Wrong timezone')  # уведомление о неправильном пределении часового пояса
                        user.conversation_power = 2
                    elif message.text.lower() == 'да':
                        if user.first:
                            user.pref_timezone = user.timezone
                            user.conversation = 'exercises'  # диалог о тренировке
                            user.conversation_power = 0
                            bot.send_message(tel_id, 'Отлично, а сейчас тебя ждёт допрос')
                            bot.send_message(tel_id, 'Ты хочешь отжиматься?', reply_markup=keyboard_noyes)
                        else:
                            timezone_update(tel_id)
                            bot.send_message(tel_id, 'Я запомнил', reply_markup=keyboard(user))
                            user.conversation = ''  # выход из диалога
                            user.conversation_power = 0
                        con = sqlite3.connect("data.db")  # запись в бд
                        cur = con.cursor()
                        cur.execute(
                            """UPDATE table_name SET time_zone = {} WHERE user_id = {}""".format(user.timezone, tel_id))
                        con.commit()
                        con.close()

                elif user.conversation_power == 2:
                    if message.text in list_of_time_zones:
                        user.timezone = int(message.text)
                        if user.first:
                            user.pref_timezone = user.timezone
                            user.conversation = 'exercises'  # диалог об упражнениях
                            user.conversation_power = 0
                            bot.send_message(tel_id, 'Отлично, а сейчас тебя ждёт допрос')
                            bot.send_message(tel_id, 'Ты хочешь отжиматься?', reply_markup=keyboard_noyes)
                        else:
                            timezone_update(tel_id)
                            bot.send_message(tel_id, 'Я запомнил', reply_markup=keyboard(user))
                            user.conversation = ''  # выход из диалога
                            user.conversation_power = 0
                        con = sqlite3.connect("data.db")  # запись в бд
                        cur = con.cursor()
                        cur.execute(
                            """UPDATE table_name SET time_zone = {} WHERE user_id = {}""".format(user.timezone, tel_id))
                        con.commit()
                        con.close()

                    else:
                        bot.send_message(tel_id, 'Пиши корректно')
            except ValueError:
                bot.send_message(tel_id, 'Выбери из вариантов')

        elif user.conversation == "exercises":  # диалог об упражнениях
            try:
                exercise_talking(message, user)
            except ZeroError:  # если юзер ответил 0
                bot.send_sticker(tel_id, sticker_stupid)
                bot.send_message(tel_id, 'Слабак?')
            except ExerciseFormatError:  # если юзер ответил отприцательным числом (а ещё это пасхалка)
                bot.send_sticker(tel_id, sticker_car)
                bot.send_message(tel_id, 'Ты думаешь Рэймонд это не предвидел?')
            except ValueError:  # если юзер ответил не числом
                bot.send_sticker(tel_id, sticker_fingers)
                bot.send_message(tel_id, 'Напиши просто число')
            except YesNoError:  # если юзер ответил на вопрос некоректно
                bot.send_message(tel_id, 'Отвечай да или нет')
            except Exception as exercise_error:
                logging.error('Unknown error in exercises choosing {}'.format(exercise_error.__class__.__name__))
                bot.send_message(tel_id, 'Отвечай внятно')

        elif user.conversation == 'date_time':  # диалог о расписании
            try:
                if user.conversation_power == 0:
                    if message.text.lower() in days.keys():
                        if message.text.lower() in user.change_data.keys():  # если этот день для тренировок уже выбран
                            bot.send_message(tel_id,
                                             'Вы хотите добавить тренировкку в {} или изменить'.format(
                                                 message.text.lower()), reply_markup=keyboard_change)
                            user.conversation_power = 2
                        else:
                            bot.send_message(tel_id,
                                             'В какое время ты можешь заниматься в {}'.format(message.text.lower()),
                                             reply_markup=keyboard_time)
                            user.conversation_power = 1
                        user.day = message.text.lower()
                    elif message.text.lower() == 'на этом хватит':
                        if user.change_data:
                            user.conversation = ""  # выход из диалога
                            timetable_update(tel_id)
                            user.first = False  # конец обучения
                            user.conversation_power = 0
                            bot.send_sticker(tel_id, sticker_brain)
                            bot.send_message(tel_id, "Я запомнил", reply_markup=keyboard(user))
                        else:
                            bot.send_sticker(tel_id, sticker_angry)
                            bot.send_message(tel_id, "Ты вообще собираешься заниматься?",
                                             reply_markup=keyboard_days)
                    else:
                        raise WeekdayError  # описания ошибок находятся выше
                elif user.conversation_power == 2:
                    if message.text.lower() == 'добавить':  # этой функции не было пока не появился абонемент
                        if user.sub:
                            if len(user.change_data[user.day]) < 3:
                                bot.send_message(tel_id,
                                                 'В какое время ты можешь заниматься в {}'.format(
                                                     message.text.lower()), reply_markup=keyboard_time)
                                user.conversation_power = 3
                            else:
                                bot.send_message(tel_id, 'У вас не может быть больше 3 тренировок в день',
                                                 reply_markup=keyboard_days)  # надеюсь спасёт от дудоса
                                user.conversation_power = 0
                        else:
                            bot.send_message(tel_id,
                                             'Для этого действия вы должны приобрести абонемент',
                                             reply_markup=keyboard_days)  # придётся покупать абонемент
                            user.conversation_power = 0
                    elif message.text.lower() == 'изменить':
                        bot.send_message(tel_id,
                                         'Когда можешь заниматься в {}, скажи во сколько если не можешь выбрать'.format(
                                             message.text.lower()), reply_markup=keyboard_time)
                        user.conversation_power = 1
                elif user.conversation_power == 3:
                    if not time_format(message.text) in user.change_data[user.day]:  # если время не занято
                        user.change_data[user.day].append(time_format(message.text))
                        bot.send_message(tel_id, 'Когда ты ещё хочешь заниматься?', reply_markup=keyboard_days)
                        user.conversation_power = 0
                    else:
                        bot.send_message(tel_id, 'Ты уже записан на это время', reply_markup=keyboard_days)
                        user.conversation_power = 0
                elif user.conversation_power == 1:
                    user.change_data[user.day] = [time_format(message.text)]
                    bot.send_message(tel_id, 'Когда ты ещё хочешь заниматься?', reply_markup=keyboard_days)
                    user.conversation_power = 0
            except DivFiveError:  # описания ошибок находятся выше
                bot.send_message(tel_id, 'Число минут должно быть кратно 5')
                # это ограничение снижает пассивную нагрузку примерно в 5 раз
            except WeekdayError:  # описания ошибок находятся выше
                bot.send_message(tel_id, 'Просто напиши день недели')
            except TimeFormatError:  # описания ошибок находятся выше
                bot.send_message(tel_id, 'Пиши в формате HH:MM, например 18:00')
            except TimeError:  # описания ошибок находятся выше
                bot.send_sticker(tel_id, sticker_angry)
                bot.send_message(tel_id, 'Ты шутки шутить вздумал?')
            except ValueError:  # если ответ в неверном формате
                bot.send_sticker(tel_id, sticker_angry)
                bot.send_message(tel_id, 'Скажи нормально')
            except Exception as time_error:
                logging.error('Unknown date and time error {}'.format(time_error.__class__.__name__))
        elif user.conversation == 'training':  # диалог тренировки
            if message.text.lower() == 'выполнил':
                bot.send_message(tel_id, choice(list_of_phrases))  # выбор фразочки для мотивации
                exercise(tel_id)
            elif message.text.lower() == 'увеличить кол-во упражнений':
                if user.training == "Отжимания":
                    user.training_type[user.training] += 2
                elif user.training == "Приседания":
                    user.training_type[user.training] += 2
                elif user.training == "Подтягивания":
                    user.training_type[user.training] += 1
                elif user.training == "Планка":
                    user.training_type[user.training] += 10
                elif user.training == "Поднимание ног":
                    user.training_type[user.training] += 4
                bot.send_message(tel_id, 'Я буду давать тебе большую нагрузку')
                exercise(tel_id)
            elif message.text.lower() == 'слишком тяжело':
                try:
                    if user.training == "Отжимания":
                        if user.training_type[user.training] > 2:
                            user.training_type[user.training] -= 2
                        else:
                            raise TooLittle  # описания ошибок находятся выше
                    elif user.training == "Приседания":
                        if user.training_type[user.training] > 2:
                            user.training_type[user.training] -= 2
                        else:
                            raise TooLittle
                    elif user.training == "Подтягивания":
                        if user.training_type[user.training] > 1:
                            user.training_type[user.training] -= 1
                        else:
                            raise TooLittle
                    elif user.training == "Планка":
                        if user.training_type[user.training] > 10:
                            user.training_type[user.training] -= 10
                        else:
                            raise TooLittle
                    elif user.training == "Поднимание ног":
                        if user.training_type[user.training] > 2:
                            user.training_type[user.training] -= 2
                        else:
                            raise TooLittle
                    bot.send_message(tel_id, 'Я запомнил, что тебе нужно давать меньшую нагрузку')
                    exercise(tel_id)
                except TooLittle:  # описания ошибок находятся выше
                    bot.send_sticker(tel_id, sticker_stupid)
                    bot.send_message(tel_id, 'Меньше уже некуда, {}'.format(user.user_name))
                    exercise(tel_id)

            elif message.text.lower() == 'очень легко':
                bot.send_sticker(tel_id, sticker_surprised)
                if user.training == "Отжимания":
                    user.training_type[user.training] += 4
                elif user.training == "Приседания":
                    user.training_type[user.training] += 4
                elif user.training == "Подтягивания":
                    user.training_type[user.training] += 2
                elif user.training == "Планка":
                    user.training_type[user.training] += 20
                elif user.training == "Поднимание ног":
                    user.training_type[user.training] += 8
                bot.send_message(tel_id, 'Я буду давать тебе большую нагрузку')
                exercise(tel_id)
            elif message.text.lower() == 'закончить тренировку':
                bot.send_sticker(tel_id, sticker_sad)
                bot.send_message(tel_id, 'Грустно конечно, но что поделать')
                user.num = []  # обновление списка при преждевременном завершении тренировки
                exercise(tel_id)
            else:
                bot.send_message(tel_id, 'Я тебя не понял, повтори')
        else:  # беседы вне диалога
            if message.text.lower() == 'называй меня по другому':
                bot.send_message(tel_id, 'Как тебя называть?', reply_markup=types.ReplyKeyboardRemove())
                dictionary_of_users[tel_id].conversation = "greeting"  # запуск диалога приветсквия
                dictionary_of_users[tel_id].conversation_power = 1
            elif message.text.lower() == 'сменить упражнения':
                user.change_training = dict()  # пустой словарь для новых данных
                bot.send_message(tel_id, 'Ты хочешь отжиматься?', reply_markup=keyboard_noyes)
                user.conversation = 'exercises'  # запуск диалога об упражнениях
                user.conversation_power = 0
            elif message.text.lower() == 'сменить расписание':
                user.conversation_power = 0
                user.change_data = dict()  # пустой словарь для новых данных
                user.conversation = "date_time"  # запуск диалога о расписании
                bot.send_message(tel_id, 'В какой день можешь заниматься?', reply_markup=keyboard_first_days)
            elif message.text.lower() == 'показать расписание':
                bot.send_message(tel_id, "{}".format('\n'.join(
                    ["{}\t{}".format(j.capitalize(), '\t'.join([':'.join(m) for m in sorted(user.date_and_time[j])]))
                     for j in user.date_and_time.keys()])), reply_markup=keyboard(user))  # люблю списочные выражения
            elif message.text.lower() == 'хочу заниматься':
                dictionary_of_users[tel_id].conversation = 'training'  # запуск диалога тренировки
                dictionary_of_users[tel_id].num = [i for i in dictionary_of_users[
                    tel_id].training_type.keys()]  # упражниния юзера
                dictionary_of_users[tel_id].conversation_power = 0
                exercise(tel_id)
            elif message.text.lower() == 'изменить часовой пояс':
                user.conversation = 'time_zone'  # запуск диалога о часовом поясе
                user.conversation_power = 0
                bot.send_message(tel_id, 'Какой у тебя часовой пояс?', reply_markup=keyboard_ask_timezone)
            elif message.text.lower() == 'хочу челендж':
                if user.sub:
                    if user.challenge:
                        challenge = choice(list(dict_of_challenges.keys()))
                        bot.send_message(tel_id,
                                         'Твой челендж:\n{}\n{}'.format(challenge, dict_of_challenges[challenge]),
                                         reply_markup=keyboard_challenge)
                        user.challenge = False
                    else:
                        bot.send_message(tel_id, "Ты ещё не закончил предыдущий челендж")
                else:
                    bot.send_message(tel_id, "Для этого ты должен купить абонемент")
            elif message.text.lower() == 'купить абонемент':
                if not user.sub:
                    if PAYMENTS_PROVIDER_TOKEN.split(':')[1] == 'TEST':  # отправка предупреждения о тестовой оплате
                        bot.send_message(message.chat.id, pre_buy_demo_alert)
                    bot.send_invoice(message.chat.id,  # отправка информации об оплате
                                     title='Абонемент',
                                     description=tm_description,  # описание абонемента
                                     provider_token=PAYMENTS_PROVIDER_TOKEN,  # токен оплаты
                                     currency='rub',  # валюта
                                     is_flexible=False,
                                     prices=[PRICE],  # цена
                                     start_parameter='subscription-example',
                                     invoice_payload='some-invoice-payload-for-our-internal-use'
                                     )
                else:
                    bot.send_message(tel_id, 'У вас уже есть подписка')
            else:  # тот самый ИИ про который было много сказано
                request = apiai.ApiAI(AI_TOKEN).text_request()
                request.lang = 'ru'
                request.session_id = 'WorkoutBot'
                request.query = message.text
                response_json = json.loads(request.getresponse().read().decode('utf-8'))
                response = response_json['result']['fulfillment']['speech']
                if response:
                    bot.send_message(tel_id, response)
                else:
                    bot.send_message(tel_id, 'Я тебя не понимаю')
    except RegError:  # описания ошибок находятся выше
        bot.send_message(tel_id, 'Я тебя не знаю, нажми /start')
    except BlankName:  # описания ошибок находятся выше
        bot.send_message(tel_id, 'Ты шутки шутишь? Как тебя звать?')
        bot.send_sticker(tel_id, sticker_car)
    except Exception as main_error:
        logging.error('Unknown error in main {}'.format(main_error.__class__.__name__))


# проверка готовности юзера к тренировке и выполнения челенджей
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    tel_id = call.message.chat.id
    try:
        if dictionary_of_users[tel_id].conversation == '':  # тренировку можно начать только если нет диалога с тренером
            if call.data == "yes":  # начало тренировки
                dictionary_of_users[tel_id].conversation = 'training'
                dictionary_of_users[tel_id].num = [i for i in dictionary_of_users[tel_id].training_type.keys()]
                dictionary_of_users[tel_id].conversation_power = 0
                exercise(tel_id)
            elif call.data == "no":  # отказ от тренировки
                bot.send_sticker(tel_id, sticker_really)
            elif call.data == 'done':  # выполнение челенджа
                bot.send_sticker(tel_id, sticker_hey_you)
                bot.send_message(tel_id, 'Ты молодец, так держать!')
                dictionary_of_users[tel_id].challenge = True
            elif call.data == 'did_not':  # отказ от челенджа
                bot.send_sticker(tel_id, sticker_stupid)
                bot.send_message(tel_id, 'Может в следующий раз получится')
                dictionary_of_users[tel_id].challenge = True
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.send_message(tel_id,
                             'Подожди, мы не {}'.format(dict_of_talks[dictionary_of_users[tel_id].conversation]))
    except KeyError:
        bot.send_message(tel_id, 'Я тебя не знаю, нажми /start')
    except Exception as callback_error:
        logging.error('callback error {}'.format(callback_error.__class__.__name__))


# отлов стикеров(на случай если захотим добавить стикеров)
@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message.sticker.file_id)
    bot.send_sticker(message.chat.id, choice(list_of_stickers))  # отправка случайного стикера из нашего пака


# проверка оплаты
@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# Обновление статуса пользрвателя и уведомление о приобритении абонемента
@bot.message_handler(content_types='successful_payment')
def process_successful_payment(message):
    dictionary_of_users[message.chat.id].sub = 1
    con = sqlite3.connect("data.db")  # запись в бд
    cur = con.cursor()
    cur.execute(
        """UPDATE table_name SET sub = 1 WHERE user_id = {}""".format(message.chat.id))
    con.commit()
    con.close()
    if dictionary_of_users[message.chat.id].conversation == '':  # что бы не переключить клавиатуру если идёт диалог
        bot.send_message(message.chat.id, 'Спасибо за приобритение абонемента', reply_markup=keyboard_main_premium)
    else:
        bot.send_message(message.chat.id, 'Спасибо за приобритение абонемента')


"""
                                        Запуск бота
"""

# ну это main, тут всё ясно
if __name__ == '__main__':
    p1.start()  # запускаем проверку в отдельном потоке
    while True:  # цикл что бы при падении серверов телеграма бот жил и ждал включения серверов
        try:
            bot.polling(none_stop=True)  # запуск в бота
        except Exception as error:
            logging.error("{} LAST CHANCE".format(error.__class__.__name__))
        time.sleep(300)  # а это что бы он не нагружал систему запросами в случае падения серверов телеграма
