from requests import get
from bs4 import BeautifulSoup
from threading import Timer
from telebot import types, TeleBot
from os import path, mkdir, listdir
from time import ctime

def log(message): #Создание логов от собщении
    if not path.isdir('./logs'):
        mkdir('./logs')
    logfile = open(f'./logs/{ctime()}.txt', 'w')
    logfile.write(f'ID: {message.id}\nMessage Id: {message.message_id}\nChat ID: {message.chat.id}\n-------------\nUserName: {message.from_user.username}\nFirst Name: {message.from_user.first_name}\nLast Name: {message.from_user.last_name}\nLanguage: {message.from_user.language_code}\n-------------\nUser ID: {message.from_user.id}\nType: {message.chat.type}\nText: {message.text}\n-------------\nTime: {ctime()}')

def init(): #Инициализация перменных
  ad = 'https://ctftime.org/event/list/?year=2021&online=-1&format=0&restrictions=0&upcoming=true'
  ad2 = 'https://ctftime.org'
  r = get(ad,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36'})
  soup = BeautifulSoup(r.text, 'lxml')
  ctfs_html = soup.select('tr:not(:first-of-type)')
  return ad, ad2, ctfs_html

def place_insert(place): #Функция для подстановки места в словарь стф
  if place != '' and place[len(place)-1] != '\n' and place[0] != '\n':
    return place
  elif place != '' and place[0] == '\n' and place[len(place)-1] == '\n' and place[len(place)-2] == '\n' and place[1] == '\n':
    return place[6:len(place)-2]
  elif place != '' and place[0] == '\n' and place[len(place)-1] == '\n':
    return place[1:len(place)-1]
  elif place == '':
    return place

def set_interval(func, sec): #Функция для запуска функции через какое-то кол-во секунд
    def func_wrapper():
        set_interval(func, sec) 
        func()
    t = Timer(sec, func_wrapper)
    t.start()
    return t

def keyboard_creator(list_of_names): #Функция для создания кнопок
    returned_k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in list_of_names:
        if isinstance(i, list):
            string = ""
            for o in range(len(i) - 1):
                string += f"'{i[o]}', "
            string += f"'{i[-1]}'"
            exec(f"""returned_k.row({string})""")
            continue
        exec(f"""returned_k.row('{i}')""")
    return returned_k

def buttons_creator(dict_of_names, how_many_rows=7): #Функция для создания кнопок в сообщении
    returned_k = types.InlineKeyboardMarkup(row_width=how_many_rows)
    for i in dict_of_names.keys():
        if type(dict_of_names[i]) is dict:
            count = 0
            for o in dict_of_names[i].keys():
                count += 1
                exec(
                    f"""button{count} = types.InlineKeyboardButton(text='{o}', callback_data='{dict_of_names[i][o]}')""")
            s = []
            for p in range(1, count + 1):
                s.append(f"button{p}")
            exec(f"""returned_k.add({', '.join(s)})""")
        else:
            exec(f"""button = types.InlineKeyboardButton(text='{i}', callback_data='{dict_of_names[i]}')""")
            exec(f"""returned_k.add(button)""")
    return returned_k

def ctf_text(ctf, first_text=''): #Отправка текста с стфкой
  if ctf["place"] != '' and ctf["place"] != 'On-line':
    return f'{first_text}Имя: {ctf["name"]}\nТип: {ctf["type"]}\nНачало: {ctf["begin_date"]} в {ctf["begin_time"]}\nКонец: {ctf["end_date"]} в {ctf["end_time"]}\nБудет проходить в {ctf["place"]}\nСсылка на страничку на ctf time: {ctf["link"]}'
  elif ctf['place'] == '':
    return f'{first_text}Имя: {ctf["name"]}\nТип: {ctf["type"]}\nНачало: {ctf["begin_date"]} в {ctf["begin_time"]}\nКонец: {ctf["end_date"]} в {ctf["end_time"]}\nМестоположение данной стф пока никому не известно...\nСсылка на страничку на ctf time: {ctf["link"]}'
  elif ctf['place'] == 'On-line':
    return f'{first_text}Имя: {ctf["name"]}\nТип: {ctf["type"]}\nНачало: {ctf["begin_date"]} в {ctf["begin_time"]}\nКонец: {ctf["end_date"]} в {ctf["end_time"]}\nБудет проходить в онлайн режиме\nСсылка на страничку на ctf time: {ctf["link"]}'

def all_ctf(): #Функция для получения всех стфок
    ad, ad2, ctfs_html = init()
    ctfs = []
    for i in range(len(ctfs_html)):
      ctf_el = ctfs_html[i]
      ctf_html = BeautifulSoup(str(ctf_el), 'lxml').findAll('td')
      ctf = {
        'name': BeautifulSoup(str(ctf_html[0]),'lxml').text, 

        'link': ad2 + str(BeautifulSoup(str(ctf_html[0]),'lxml').a.get('href')), 

        'begin_date': str(BeautifulSoup(str(ctf_html[1]), 'lxml').text).split(' — ')[0].split(', ')[0], 

        'begin_time': str(BeautifulSoup(str(ctf_html[1]), 'lxml').text).split(' — ')[0].split(', ')[1], 

        'end_date': str(BeautifulSoup(str(ctf_html[1]), 'lxml').text).split(' — ')[1].split(', ')[0], 

        'end_time': str(BeautifulSoup(str(ctf_html[1]), 'lxml').text).split(' — ')[1].split(', ')[1],

        'type': BeautifulSoup(str(ctf_html[2]), 'lxml').text,

        'place': place_insert(BeautifulSoup(str(ctf_html[3]), 'lxml').text)
      }
      ctfs.append(ctf)
    return ctfs

def current_ctf(): #Функция для получения текущей стфки
  global ChatIDs
  print(ChatIDs)
  if ChatIDs != None:
    for id in ChatIDs:
      current_ctf = all_ctf()[0]
      find_text = 0
      f = open(f'./old_ctfs/{id}', 'r')
      old_ctf = f.read().split('\n')
      f.close()
      for ctf in old_ctf:
        if ctf == str(current_ctf):
          find_text = 1
      if find_text == 0:
        old_ctf = str(current_ctf) + '\n' + '\n'.join([str(old) for old in old_ctf])
        w = open(f'./old_ctfs/{id}', 'w')
        w.write(str(old_ctf))
      print(find_text, id)
      if find_text == 0:
        bot.send_message(id, ctf_text(current_ctf, 'Найдена новая стф!\n\n'))


ChatIDs = None
token = open('./tokenfile.txt', 'r').read()
token = token[0:len(token)-1]
bot = TeleBot(token)
chatId = '654810143'


@bot.message_handler(commands=['showctf'])
def message(message):
  global chatId
  global ChatIDs
  chatId = message.chat.id
  ctfs = all_ctf()
  ctf = ctfs[0]
  keyboards = {'1': {}}
  for i in range(len(ctfs)):
    keyboards['1'][f'{i+1}'] = f'{i}'
  bot.send_message(chatId, text=ctf_text(ctf), reply_markup=buttons_creator(keyboards, 8))
  try:
    r = open(f'./old_ctfs/{chatId}', 'r')
    ChatIDs = listdir('./old_ctfs/')
  except FileNotFoundError:
    w = open(f'./old_ctfs/{chatId}', 'w')
    ChatIDs = listdir('./old_ctfs/')
  log(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    ctfs = all_ctf()
    ctf = ctfs[int(call.data)]
    keyboards = {'1': {}}
    for i in range(len(ctfs)):
      keyboards['1'][f'{i+1}'] = f'{i}'
    try:
      bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=ctf_text(ctf), reply_markup=buttons_creator(keyboards, 8))
      bot.answer_callback_query(callback_query_id=call.id)
    except Exception as e:
      handled = False
      bot.answer_callback_query(callback_query_id=call.id, text='Данная стф уже выведена!')

@bot.message_handler(func=lambda message: True)
def hi_text(message):
  if (message.chat.type == "private"):
    global chatId
    global ChatIDs
    chatId = message.chat.id
    bot.reply_to(message, f'Привет, {message.from_user.first_name}!\nДанный бот создан командой <a href="https://ctftime.org/team/146454">DHI</a> для быстрого просмотра новых ctf.\n<i>Приятного использования!</i>\n\nКоманды:\n/showctf - информация о любой ближайшей стф', parse_mode='HTML')
  try:
    r = open(f'./old_ctfs/{chatId}', 'r')
    ChatIDs = listdir('./old_ctfs/')
  except FileNotFoundError:
    w = open(f'./old_ctfs/{chatId}', 'w')
    ChatIDs = listdir('./old_ctfs/')
  log(message)

set_interval(current_ctf, 10)

bot.infinity_polling(timeout=5)