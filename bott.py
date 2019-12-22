import telebot
import sqlite3
import random
import datetime
import re

conn = sqlite3.connect("cinemabot.db", check_same_thread=False)
cursor = conn.cursor()

bot = telebot.TeleBot('')

keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard1.row('хочу смотреть киношку', 'хочу выбрать кинотеатр')
keyboard_halls = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard_halls.row('в меню', 'рандом', 'по брендам')
keyboard_brands = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard_brands.row('в меню', 'КАРО', 'Синема Парк', 'Люксор')
keyboard_sessions = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard_sessions.add('в меню', 'дай сеансы на сегодня', "дай сеансы на завтра", "дай сеансы на другую дату")
keyboard_films = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard_films.add('в меню', 'рандомное', 'по жанрам')
keyboard_films2 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard_films2.add('в меню', 'рандомное', 'по жанрам', 'а где это смотреть-то?')
keyboard_genres = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard_genres.add('в меню', 'а вот это где смотреть?')
brands = [elem[0] for elem in cursor.execute("select name from brand").fetchall()]
genres = []
for elem in cursor.execute("select * from cinemas"):
    lst = elem[3].lower().split()
    for i in lst:
        if i[-1] == ',':
            genres.append(i[:-1])
        else:
            genres.append(i)
genres = set(genres)
genres2 = [elem[3].lower().split() for elem in cursor.execute("select * from cinemas")]
films = {}
for elem in cursor.execute("select * from cinemas"):
    if elem[1][-1] == ' ':
        films[elem[1][:-1]] = elem[0]
    else:
        films[elem[1]] = elem[0]
last_hall_id = [0]
last_cinema_id = [-1]

def brand_fetcher(choice):
    brands_ids = {elem[1] : elem[0] for elem in cursor.execute("select * from brand").fetchall()}
    return brands_ids[choice]
def hall_fetcher(name):
    hall_id = cursor.execute("select id from cinema_halls where name =?", (name,)).fetchall()
    return hall_id
def hall_fetcher_reverse(name):
    hall_name = cursor.execute("select name from cinema_halls where id =?", (name,)).fetchall()
    return hall_name

def hall_info_output(elem, output):
    hall_info = {'Кинотеатр': elem[2], 'Адрес': elem[3], 'Метро': elem[4]}
    for k, v in hall_info.items():
        output = output + k + ': ' + str(v) + '\n'
    output = output + '\n' + '\n'
    return output

def sessions_info_output(elem, output):
    session_info = {'Фильм' : elem[3], 'Время' : elem[5], 'Цена' : elem[6]}
    for k, v in session_info.items():
        output = output + k + ': ' + str(v) + '\n'
    output = output + '\n'
    return output

def sessions_info_output2(elem, output):
    session_info = {'Фильм' : elem[3], 'Кинотеатр': hall_fetcher_reverse(elem[2])[0][0], 'Дата':elem[4],'Время' : elem[5], 'Цена' : elem[6]}
    for k, v in session_info.items():
        output = output + k + ': ' + str(v) + '\n'
    output = output + '\n'
    return output

def date_finder(string):
    pattern = re.compile(r'[0-9]+-[0-9]+-[0-9]+')
    res = re.match(pattern, string)
    if res:
        return res.group()
    else:
        return None

def films_output(elem, output):
    film_info = {'Название': elem[1], 'Длительность' : elem[2], 'Жанры': elem[3]}
    for k, v in film_info.items():
        output = output + k + ': ' + str(v) + '\n'
    output = output + '\n'
    return output

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'че нада?', reply_markup=keyboard1)

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'привет' or message.text.lower() == 'ghbdtn':
        bot.send_message(message.chat.id, 'здарова', reply_markup=keyboard1)
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'скатертью дорожка')
    elif message.text.lower() == 'хочу смотреть киношку':
        bot.send_message(message.chat.id, 'жмякни кнопку или напиши точное название, попробую найти сеансик для тебя', reply_markup = keyboard_films)
    elif message.text.lower() == 'хочу выбрать кинотеатр':
        bot.send_message(message.chat.id, 'а гвоздей жареных не хочешь?', reply_markup=keyboard_halls)
    elif message.text.lower() == 'по брендам':
        bot.send_message(message.chat.id, 'на', reply_markup=keyboard_brands)
    elif message.text in brands:
        brand = brand_fetcher(message.text)
        result = ''
        for elem in cursor.execute("select * from cinema_halls").fetchall():
            if elem[1] == brand:
                result = hall_info_output(elem, result)
        if result:
            bot.send_message(message.chat.id, result)
        bot.send_message(message.chat.id, 'напиши название кинотеатра, чтобы узнать, че можно глянуть')
    elif hall_fetcher(message.text):
        last_hall_id.pop()
        last_hall_id.append(hall_fetcher(message.text)[0][0])
        bot.send_message(message.chat.id, 'понял&принял', reply_markup=keyboard_sessions)
    elif message.text.lower() == 'рандом':
        hall_id = (random.randint(0, max([el[0] for el in cursor.execute("select id from cinema_halls").fetchall()])),)
        last_hall_id.pop()
        last_hall_id.append(hall_id[0])
        elem = cursor.execute('select * from cinema_halls where id =?', hall_id).fetchall()[0]
        result = ''
        result = hall_info_output(elem, result)
        if result:
            bot.send_message(message.chat.id, result, reply_markup=keyboard_sessions)
    elif message.text.lower() == 'в меню':
        bot.send_message(message.chat.id, 'куда ж ты фраер сдал назад?', reply_markup=keyboard1)
    elif message.text.lower() == 'дай сеансы на сегодня':
        date = datetime.date.today().strftime('%Y-%m-%d')
        result = ''
        for elem in cursor.execute("select * from sessions where hall_id =? and date =?", (last_hall_id[0], date)).fetchall():
            result = sessions_info_output(elem, result)
        if result:
            if len(result) > 4096:
                for x in range(0, len(result), 4096):
                    bot.send_message(message.chat.id, result[x:x + 4096])
            else:
                bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, 'тут нечего смотреть')
    elif message.text.lower() == 'дай сеансы на завтра':
        if last_hall_id[0] == 42 or last_hall_id[0] == 43:
            bot.send_message(message.chat.id, 'сеансы тута недоступны, кина не будет')
        date = (datetime.date.today()+ datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        result = ''
        for elem in cursor.execute("select * from sessions where hall_id =? and date =?", (last_hall_id[0], date)).fetchall():
            result = sessions_info_output(elem, result)
        if result:
            if len(result) > 4096:
                for x in range(0, len(result), 4096):
                    bot.send_message(message.chat.id, result[x:x + 4096])
            else:
                bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, 'тут нечего смотреть')
    elif message.text.lower() == "дай сеансы на другую дату":
        bot.send_message(message.chat.id, 'напиши дату в формате yyyy-mm-dd, если хочешь, чтоб я работал')
    elif date_finder(message.text):
        if last_hall_id[0] == 42 or last_hall_id[0] == 43:
            bot.send_message(message.chat.id, 'сеансы тута недоступны, кина не будет')
        date = message.text
        result = ''
        for elem in cursor.execute("select * from sessions where hall_id =? and date =?", (last_hall_id[0], date)).fetchall():
            result = sessions_info_output(elem, result)
        if result:
            if len(result) > 4096:
                for x in range(0, len(result), 4096):
                    bot.send_message(message.chat.id, result[x:x + 4096])
            else:
                bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, 'тут нечего смотреть')
    elif message.text.lower() == "рандомное":
        cinema_id = (random.randint(0, max([el[0] for el in cursor.execute("select id from cinemas").fetchall()])),)
        last_cinema_id.pop()
        last_cinema_id.append(cinema_id[0])
        elem = cursor.execute('select * from cinemas where id =?', cinema_id).fetchall()[0]
        result = ''
        result = films_output(elem, result)
        if result:
            bot.send_message(message.chat.id, result, reply_markup=keyboard_films2)
    elif message.text.lower() == "а где это смотреть-то?":
        result = ''
        for elem in cursor.execute("select * from sessions where cinema_id =?", (last_cinema_id[0],)):
            result = sessions_info_output2(elem, result)
        if result:
            if len(result) > 4096:
                for x in range(0, len(result), 4096):
                    bot.send_message(message.chat.id, result[x:x + 4096])
            else:
                bot.send_message(message.chat.id, result)
        else:
            bot.send_message(message.chat.id, 'нигде')
    elif message.text.lower() == "по жанрам":
        bot.send_message(message.chat.id, 'напиши жанр')
    elif message.text.lower() in genres:
        result = ''
        for genre in genres2:
            film_genre = ''
            if message.text.lower() in genre:
                film_genre = ' '.join(genre)
            if film_genre:
                for elem in cursor.execute('select * from cinemas where genres =?', (film_genre,)):
                    result = films_output(elem, result)
        if result:
            if len(result) > 4096:
                for x in range(0, len(result), 4096):
                    bot.send_message(message.chat.id, result[x:x + 4096])
            else:
                bot.send_message(message.chat.id, result, reply_markup=keyboard_genres)
        else:
            bot.send_message(message.chat.id, 'кажется, не знаю такого жанра')
    elif message.text.lower() == 'а вот это где смотреть?':
        bot.send_message(message.chat.id, 'а что именно?')
    elif message.text in films.keys():
        cinema_id = films[message.text]
        result = ''
        for elem in cursor.execute("select * from sessions where cinema_id =?", (cinema_id,)):
            result = sessions_info_output2(elem, result)
        if result:
            if len(result) > 4096:
                for x in range(0, len(result), 4096):
                    bot.send_message(message.chat.id, result[x:x + 4096])
            else:
                bot.send_message(message.chat.id, result, reply_markup=keyboard_films)
        else:
            bot.send_message(message.chat.id, 'нигде')
    else:
        bot.send_message(message.chat.id, 'я тебя не понимат')


bot.polling(none_stop=True, interval=0)
