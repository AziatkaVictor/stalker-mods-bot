# -*- coding: utf-8 -*-

from lxml import html
import requests
from telebot import types
import telebot
import random
import json
import urllib
import os.path
import re

print('Запуск бота...')

# Регистрация бота
bot = telebot.TeleBot('***')

# Глобальная переменная массива
global generating
generating = False

def get_emoji(number):
    # Эмодзи: 1 - злой, 2 - автор, 3 - дата, 4 - оценка, 5 - платформа
    all_emoji = ['\xF0\x9F\x98\xA1', '\xF0\x9F\x91\xA4', '\xF0\x9F\x93\x85', '\xE2\xAD\x90', '\xF0\x9F\x92\xBB']
    return all_emoji[number].encode('raw-unicode-escape').decode('utf-8')

# Функция сканирования страницы, нужен для синхронизации базы.
def check_page(page_number, save):
    sqr = 'https://ap-pro.ru/stuff/page/'
    print('Получение страницы №' + str(page_number) + '...')
    page = requests.get(sqr + str(page_number) + '/')
    page_tree = html.fromstring(page.content)
    save.extend(page_tree.xpath('//h2[@class="ipsType_newsandmods ipsContained_container"]/span/a/@href'))

@bot.message_handler(commands = ['stop'])
def stop(message):

    if message.from_user.id == 738946698:
        msg = bot.send_message(message.chat.id, 'Отключить бота?\n\nДа (+)\nНет (-)')
        bot.register_next_step_handler(msg, check_stop)

    else:
        bot.send_message(message.chat.id, 'У вас нету прав, для этой команды!')

def check_stop(message):
    if message.from_user.id == 738946698:
        if message.text == '+':
            bot.send_message(message.chat.id, 'Отключение бота ' + get_emoji(1))
            os._exit(0)
        elif message.text == '-':
            bot.send_message(message.chat.id, 'Ну ладно...')
        elif message.text != '-' and message.text != '+':
            msg = bot.send_message(message.chat.id, 'Неверный символ!')
            bot.register_next_step_handler(msg, check_stop)
            return
    else:
        msg = bot.send_message(message.chat.id, 'Нету прав.')
        bot.register_next_step_handler(msg, check_stop)
        return

@bot.message_handler(commands = ['help'])
def help(message):

    if message.from_user.id == 738946698:
        bot.send_message(message.chat.id, '/info - Информация об боте\n/random - Случайный мод\n/random_soc - Случайный мод на Тень Чернобыля\n/random_cs - Случайный мод на Чистое Небо\n/random_cop - Случайный мод на Зов Припяти\n/new - Последние релизы\n/generate - Генерация списка, ты знаешь, зачем она тебе UwU\n/stop - Остановка бота')
    else:
        bot.send_message(message.chat.id, '/info - Информация об боте\n/random - Случайный мод\n/random_soc - Случайный мод на Тень Чернобыля\n/random_cs - Случайный мод на Чистое Небо\n/random_cop - Случайный мод на Зов Припяти\n/new - Последние релизы')

# Синхронизация базы данных
@bot.message_handler(commands = ['generate'])
def get_pages(message):

    if message.from_user.id == 738946698:

        bot.send_message(message.chat.id, 'Идет генерация списка списка, подожди пару секунд...')

        global generating
        generating = True
        saved_mods = []

        i = 1

        page = requests.get('https://ap-pro.ru/stuff/page/1/')
        page_tree = html.fromstring(page.content)
        last_page = page_tree.xpath('//li[@class="ipsPagination_last"]/a/@href')
        last_page = last_page[0].encode('raw-unicode-escape').decode('utf-8')
        last_page = int(last_page[29:-1])

        message_ids = bot.send_message(message.chat.id, 'Загружено 0 из ' + str(last_page) + ' стр.')

        while i <= last_page:
            check_page(i, saved_mods)
            bot.edit_message_text(text='Загружено ' + str(i) + ' из ' + str(last_page) + ' стр.', chat_id=message.chat.id, message_id=message_ids.message_id)
            i = i + 1

        bot.send_message(message.chat.id, 'Парсинг закончен.')

        if os.path.isfile('mods.txt') == True:
            os.remove('mods.txt')

        with open('mods.txt', 'w') as fw:
            json.dump(saved_mods, fw)

        i = 0
        message_ids = bot.send_message(message.chat.id, 'Загружено ' + str(i) + ' из ' + str(len(saved_mods)) + ' логотипов модов.')

        while i < len(saved_mods):
            result = saved_mods[i]

            page = requests.get(result)
            page_tree = html.fromstring(page.content)

            photo = page_tree.xpath('//*[@id="ipsLayout_mainArea"]/div[1]/ul/li[3]/div[2]/div[1]/div//@style')
            photo = photo[0]
            photo = photo[15:-98]

            if os.path.isfile('img/' + str(i) + '.jpg') == True:
                os.remove('img/' + str(i) + '.jpg')
                print('Файл "' + str(i) + '.jpg" удалён!')

            f = open('img/' + str(i) + '.jpg', 'wb')
            f.write(urllib.request.urlopen(photo).read())
            f.close()

            print('Файл "' + str(i) + '.jpg" создан!')

            i = i + 1

            bot.edit_message_text('Загружено ' + str(i) + ' из ' + str(len(saved_mods)) + ' логотипов модов.', chat_id=message.chat.id, message_id=message_ids.message_id)

        bot.send_message(message.chat.id, 'Все фото загружены.')

        if os.path.isfile('version.txt') == True:

            with open('version.txt', 'r') as fw:
                version = json.load(fw)

            version = version + 0.1

            with open('version.txt', 'w') as fw:
                json.dump(version, fw)

        else:
            version = 0.1

            with open('version.txt', 'w') as fw:
                json.dump(version, fw)

        generating = False
        bot.send_message(message.chat.id, 'Генерация закончена!')

    else:
        bot.send_message(message.chat.id, 'У вас нету нужных прав для генерации списка!')

@bot.message_handler(commands = ['check_list'])
def check_list(message):

    if os.path.exists('users/' + str(message.from_user.id) + '_config.txt') == True and os.path.exists('users/' + str(message.from_user.id) + '.txt') == True:

        with open('users/' + str(message.from_user.id) + '_config.txt', 'r') as fw:
            check_list = json.load(fw)

        check_list = not check_list

        with open('users/' + str(message.from_user.id) + '_config.txt', 'w') as fw:
            json.dump(check_list, fw)

        if check_list == True:
            text = ', включена проверка списка пройденных модификаций. Моды из списка более не будет появляться.'
        else:
            text = ', отключена проверка списка пройденных модификаций.'

    elif os.path.exists('users/' + str(message.from_user.id) + '.txt') == True:
        check_list = True

        with open('users/' + str(message.from_user.id) + '_config.txt', 'w') as fw:
            json.dump(check_list, fw)

        text = ', включена проверка списка пройденных модификаций. Моды из списка более не будет появляться.'

    else:

        text = ', проверка не включена, так как у вас нету модов в списке пройденных!'

    if message.from_user.username != None:
        bot.send_message(message.chat.id, str(message.from_user.username) + text)
    elif message.from_user.first_name != None and (message.from_user.last_name) != None:
        bot.send_message(message.chat.id, str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + text)
    elif message.from_user.first_name != None:
        bot.send_message(message.chat.id, str(message.from_user.first_name) + text)
    elif message.from_user.last_name != None:
        bot.send_message(message.chat.id, str(message.from_user.last_name) + text)


@bot.message_handler(commands = ['all'])
def all_mods(message):

    if generating == False and message.from_user.id == 738946698:

        with open('mods.txt', 'r') as fw:
            saved_mods = json.load(fw)

        i = 0
        while i < len(saved_mods):
            page = requests.get(saved_mods[i])
            page_tree = html.fromstring(page.content)

            # Получение загаловка
            title = page_tree.xpath('//*[@id="ipsLayout_mainArea"]/div[1]/ul/li[3]/div[1]/h1/span/text()')
            title = title[0].encode('raw-unicode-escape').decode('utf-8')

            print(str(i + 1) + '. ' + title)
            i = i + 1

@bot.message_handler(commands = ['new'])
def new_mods(message):

    if generating == False:

        with open('mods.txt', 'r') as fw:
            saved_mods = json.load(fw)

        text = '<b>Пять последних релизов:</b>\n'

        i = 0
        while i < 5:
            page = requests.get(saved_mods[i])
            page_tree = html.fromstring(page.content)

            # Получение загаловка
            title = page_tree.xpath('//*[@id="ipsLayout_mainArea"]/div[1]/ul/li[3]/div[1]/h1/span/text()')
            title = title[0].encode('raw-unicode-escape').decode('utf-8')

            # Получение описания мода
            description = page_tree.xpath('//*[@id="ipsLayout_mainArea"]/div[1]/ul/li[3]/article/div[1]/section/p/text()')
            description = description[0].encode('raw-unicode-escape').decode('utf-8')

            # Получение оценки и количества отзывов
            mark = page_tree.xpath('//*[@id="ipsLayout_mainArea"]/div[1]/ul/li[3]/div[2]/div[2]/ul/li[5]/span/text()[1]')
            mark = mark[0]

            # Получение платформы мода
            platform = page_tree.xpath('//*[@id="ipsLayout_mainArea"]/div[1]/ul/li[3]/div[2]/div[2]/ul/li[2]/span/a/text()')
            platform = platform[0].encode('raw-unicode-escape').decode('utf-8')

            text = text + '\n<b>' + str(i+1) + '. <a href="' + saved_mods[i] + '">' + title + '</a></b> ' + get_emoji(3) + ' ' + str(mark[1:]) + 'из 10\n\n' + 'Мод на ' + platform + '. ' + str(description[2:])
            i = i + 1

        bot.send_message(message.chat.id, text, parse_mode='HTML', disable_web_page_preview=True)

    else:
        bot.send_message(message.chat.id, 'Данная функция сейчас недоступна, попробуйте чуть позже!')

@bot.message_handler(commands = ['random_soc'])
def random_mod_soc(message):
    if generating == False:
        random_mod(message,1)
    else:
        bot.send_message(message.chat.id, 'Данная функция сейчас недоступна, попробуйте чуть позже!')

@bot.message_handler(commands = ['random_cs'])
def random_mod_cs(message):
    if generating == False:
        random_mod(message, 2)
    else:
        bot.send_message(message.chat.id, 'Данная функция сейчас недоступна, попробуйте чуть позже!')

@bot.message_handler(commands = ['random_cop'])
def random_mod_cop(message):
    if generating == False:
        random_mod(message, 3)
    else:
        bot.send_message(message.chat.id, 'Данная функция сейчас недоступна, попробуйте чуть позже!')

@bot.message_handler(commands = ['random'])
def random_mod_cop(message):
    if generating == False:
        random_mod(message, 4)
    else:
        bot.send_message(message.chat.id, 'Данная функция сейчас недоступна, попробуйте чуть позже!')

def random_mod(message, type):

    if os.path.exists('users/' + str(message.from_user.id) + '_config.txt') == True and os.path.exists('users/' + str(message.from_user.id) + '.txt') == True:

        with open('users/' + str(message.from_user.id) + '_config.txt', 'r') as fw:
            check_list = json.load(fw)

        with open('users/' + str(message.from_user.id) + '.txt', 'r') as fw:
            base = json.load(fw)

    else:
        check_list = False

    # Открытие базы данных со списком всех модов и получение списка.
    with open('mods.txt', 'r') as fw:
        saved_mods = json.load(fw)

    # Подсчет количества модов, нужно для рандома
    max_num = len(saved_mods)

    print('ID: ' + str(message.from_user.id) + '\nНик: ' + str(message.from_user.username) + '\nИмя: ' + str(message.from_user.first_name) + ' ' + str(message.from_user.last_name))

    if check_list == True and len(base) < max_num:

        find = False
        k = 0

        while find == False:

            correct_type = False

            while correct_type == False:
                # Получение рандомной ссылки из базы данных
                random_num = random.randint(0, max_num)
                result = saved_mods[random_num]

                result_num = len(list(result))

                if type == 1:

                    number = 40 - result_num

                    if result[:number] == 'https://ap-pro.ru/stuff/ten_chernobylja/':
                        print('Тип мода: ТЧ')
                        correct_type = True

                elif type == 2:

                    number = 37 - result_num

                    if result[:number] == 'https://ap-pro.ru/stuff/chistoe_nebo/':
                        print('Тип мода: ЧН')
                        correct_type = True

                elif type == 3:

                    number = 37 - result_num

                    if result[:number] == 'https://ap-pro.ru/stuff/zov_pripjati/':
                        print('Тип мода: ЗП')
                        correct_type = True

                elif type == 4:
                    correct_type = True

                result_find = []
                i = 0

                while i < len(base):

                    base_cash = base[i].split('*')
                    result_find.append(base_cash[0])

                    i = i + 1

                if result in result_find:
                    find = False
                    k = k + 1
                else:
                    find = True

                if k == 200:
                    bot.send_message(message.chat.id, 'Ошибка, слишком много попыток найти мод!')
                    return

    elif check_list == True and len(base) >= max_num:

        print('Тип мода: Возрат')

        text = ', к сожалению, в твоём списке все моды, которые вышли на данный момент, мне нечего тебе предложить...'

        if message.from_user.username != None:
            bot.send_message(message.chat.id, str(message.from_user.username) + text)
        elif message.from_user.first_name != None and (message.from_user.last_name) != None:
            bot.send_message(message.chat.id, str(message.from_user.first_name) + ' ' + str(message.from_user.last_name) + text)
        elif message.from_user.first_name != None:
            bot.send_message(message.chat.id, str(message.from_user.first_name) + text)
        elif message.from_user.last_name != None:
            bot.send_message(message.chat.id, str(message.from_user.last_name) + text)

        return

    else:
        correct_type = False

        while correct_type == False:
            # Получение рандомной ссылки из базы данных
            random_num = random.randint(0, max_num)
            result = saved_mods[random_num]

            result_num = len(list(result))

            if type == 1:

                number = 40 - result_num

                if result[:number] == 'https://ap-pro.ru/stuff/ten_chernobylja/':
                    print('Тип мода: ТЧ')
                    correct_type = True

            elif type == 2:

                number = 37 - result_num

                if result[:number] == 'https://ap-pro.ru/stuff/chistoe_nebo/':
                    print('Тип мода: ЧН')
                    correct_type = True

            elif type == 3:

                number = 37 - result_num

                if result[:number] == 'https://ap-pro.ru/stuff/zov_pripjati/':
                    print('Тип мода: ЗП')
                    correct_type = True

            elif type == 4:
                correct_type = True

    # Постройка структуры страницы по полученной ссылке
    page = requests.get(result)
    page_tree = html.fromstring(page.content)

    # Получение загаловка
    title = page_tree.xpath('//*[@id="ipsLayout_mainArea"]/div[1]/ul/li[3]/div[1]/h1/span/text()')
    title = title[0].encode('raw-unicode-escape').decode('utf-8')

    img = open('img/' + str(random_num) + '.jpg', 'rb')

    # Получение описания мода
    description = page_tree.xpath('//*[@id="ipsLayout_mainArea"]/div[1]/ul/li[3]/article/div[1]/section/p/text()')
    description = description[0].encode('raw-unicode-escape').decode('utf-8')

    # Получение авторов
    author = page_tree.xpath('//*[@id="ipsLayout_mainArea"]/div[1]/ul/li[3]/div[2]/div[2]/ul/li[1]/span/text()')
    author = author[0].encode('raw-unicode-escape').decode('utf-8')

    # Получение даты релиза
    time = page_tree.xpath('//*[@id="ipsLayout_mainArea"]/div[1]/ul/li[3]/div[2]/div[2]/ul/li[3]/span/text()')
    time = time[0].encode('raw-unicode-escape').decode('utf-8')

    # Получение оценки и количества отзывов
    mark = page_tree.xpath('//*[@id="ipsLayout_mainArea"]/div[1]/ul/li[3]/div[2]/div[2]/ul/li[5]/span/text()[1]')
    mark = mark[0]

    num = page_tree.xpath('//*[@id="ipsLayout_mainArea"]/div[1]/ul/li[3]/div[2]/div[2]/ul/li[5]/span/text()[2]')
    num = num[0].encode('raw-unicode-escape').decode('utf-8')

    # Получение платформы мода
    platform = page_tree.xpath('//*[@id="ipsLayout_mainArea"]/div[1]/ul/li[3]/div[2]/div[2]/ul/li[2]/span/a/text()')
    platform = platform[0].encode('raw-unicode-escape').decode('utf-8')

    with open('version.txt', 'r') as fw:
        version = json.load(fw)

    callback_text = 't,' + str(type) + ',' + str(random_num) + ',' + str(version)
    print('Версия: ' + str(version))
    print('\n')

    # Настройки кнопки "Скачать"
    markup = types.InlineKeyboardMarkup()
    btn_d = types.InlineKeyboardButton(text='Скачать', url=result)
    btn_g = types.InlineKeyboardButton(text='Я прошел мод!', callback_data=callback_text)
    markup.add(btn_d, btn_g)

    # Отправка фото и всего текста
    bot.send_photo(message.chat.id, img)
    bot.send_message(message.chat.id, '<b>' + str(title) + '</b>' + '\n\n' + get_emoji(1) + ' <b>Автор: </b>' + str(author[6:]) + '\n' + get_emoji(4) + ' <b>Платформа: </b>' + str(platform) + '\n' + get_emoji(2) + ' <b>Дата релиза: </b>' + str(time[6:]) + '\n' + get_emoji(3) + ' <b>Оценка: </b>' + str(mark[1:]) + str(num[7:]) + '\n\n' + str(description[2:]), parse_mode='HTML', reply_markup = markup)

@bot.callback_query_handler(lambda call: True)
def callback_inline(call):

    info = call.data.split(',')

    if info[0] == 't':

        with open('version.txt', 'r') as fw:
            version = json.load(fw)

            text_error = ', кнопка более не работоспособна, сообщение устарело!'
            text_done = ' записан!'
            text_stop = ' уже есть в твоем списке!'

        if len(info) != 4:
            if call.from_user.username != None:
                bot.send_message(call.message.chat.id, str(call.from_user.username) + text_error)
            elif call.from_user.first_name != None and (call.from_user.last_name) != None:
                bot.send_message(call.message.chat.id, str(call.from_user.first_name) + ' ' + str(call.from_user.last_name) + text_error)
            elif call.from_user.first_name != None:
                bot.send_message(call.message.chat.id, str(call.from_user.first_name) + text_error)
            elif call.from_user.last_name != None:
                bot.send_message(call.message.chat.id, str(call.from_user.last_name) + text_error)
        else:
            if version != float(info[3]):
                if call.from_user.username != None:
                    bot.send_message(call.message.chat.id, str(call.from_user.username) + text_error)
                elif call.from_user.first_name != None and (call.from_user.last_name) != None:
                    bot.send_message(call.message.chat.id, str(call.from_user.first_name) + ' ' + str(call.from_user.last_name) + text_error)
                elif call.from_user.first_name != None:
                    bot.send_message(call.message.chat.id, str(call.from_user.first_name) + text_error)
                elif call.from_user.last_name != None:
                    bot.send_message(call.message.chat.id, str(call.from_user.last_name) + text_error)
            else:
                with open('mods.txt', 'r') as fw:
                    saved_mods = json.load(fw)

                url = saved_mods[int(info[2])]

                page = requests.get(url)
                page_tree = html.fromstring(page.content)

                # Получение загаловка
                title = page_tree.xpath('//*[@id="ipsLayout_mainArea"]/div[1]/ul/li[3]/div[1]/h1/span/text()')
                title = title[0].encode('raw-unicode-escape').decode('utf-8')

                result = [url + '*' + title]

                if os.path.exists('users/' + str(call.from_user.id) + '.txt') == True:
                    with open('users/' + str(call.from_user.id) + '.txt', 'r') as fw:
                        base = json.load(fw)

                    new = False
                    i = 0
                    while i < len(base):
                        if base[i] != result[0]:
                            new = True
                        else:
                            new = False
                            break
                        i = i + 1

                    if new == True:
                        base.extend(result)
                        with open('users/' + str(call.from_user.id) + '.txt', 'w') as fw:
                            json.dump(base, fw)
                        if call.from_user.username != None:
                            bot.send_message(call.message.chat.id, str(call.from_user.username) + ', ' + title + text_done)
                        elif call.from_user.first_name != None and (call.from_user.last_name) != None:
                            bot.send_message(call.message.chat.id, str(call.from_user.first_name) + ' ' + str(call.from_user.last_name) + ', ' + title + text_done)
                        elif call.from_user.first_name != None:
                            bot.send_message(call.message.chat.id, str(call.from_user.first_name) + ', ' + title + text_done)
                        elif call.from_user.last_name != None:
                            bot.send_message(call.message.chat.id, str(call.from_user.last_name) + ', ' + title + text_done)
                    else:
                        if call.from_user.username != None:
                            bot.send_message(call.message.chat.id, str(call.from_user.username) + ', ' + title + text_stop)
                        elif call.from_user.first_name != None and (call.from_user.last_name) != None:
                            bot.send_message(call.message.chat.id, str(call.from_user.first_name) + ' ' + str(call.from_user.last_name) + ', ' + title + text_stop)
                        elif call.from_user.first_name != None:
                            bot.send_message(call.message.chat.id, str(call.from_user.first_name) + ', ' + title + text_stop)
                        elif call.from_user.last_name != None:
                            bot.send_message(call.message.chat.id, str(call.from_user.last_name) + ', ' + title + text_stop)
                else:
                    with open('users/' + str(call.from_user.id) + '.txt', 'w') as fw:
                        json.dump(result, fw)
                    if call.from_user.username != None:
                        bot.send_message(call.message.chat.id, str(call.from_user.username) + text_done)
                    elif call.from_user.first_name != None and (call.from_user.last_name) != None:
                        bot.send_message(call.message.chat.id, str(call.from_user.first_name) + ' ' + str(call.from_user.last_name) + text_done)
                    elif call.from_user.first_name != None:
                        bot.send_message(call.message.chat.id, str(call.from_user.first_name) + text_done)
                    elif call.from_user.last_name != None:
                        bot.send_message(call.message.chat.id, str(call.from_user.last_name) + text_done)

@bot.message_handler(commands = ['my_mods'])
def my_mods(message):
    if os.path.exists('users/' + str(message.from_user.id) + '.txt') == True:
        with open('users/' + str(message.from_user.id) + '.txt', 'r') as fw:
            base = json.load(fw)
        with open('mods.txt', 'r') as fw:
            saved_mods = json.load(fw)

        text = '<b>Проейденные вами модификации:</b>\n'

        i = 0
        while i < len(base):
            result = base[i].split('*')

            print(result)

            title = result[1]
            url = result[0]

            if url in saved_mods:
                text = text + '\n<b>' + str(i + 1) + '. <a href="' + url + '">' + title + '</a></b> '
            else:
                bot.send_message(message.chat.id, 'Удаляем ' + title + ', потому что этого мода нету в базе данных.', parse_mode='HTML', disable_web_page_preview=True)
                base.pop(i)

                with open('users/' + str(message.from_user.id) + '.txt', 'w') as fw:
                    json.dump(base, fw)

            i = i + 1

        bot.send_message(message.chat.id, text, parse_mode='HTML', disable_web_page_preview=True)
    else:
        bot.send_message(message.chat.id, 'У тебя нету пройденных модификаций!')

@bot.message_handler(commands = ['delete_my_mods'])
def delete_my_mods(message):
    if os.path.exists('users/' + str(message.from_user.id) + '.txt') == True:
        with open('users/' + str(message.from_user.id) + '.txt', 'r') as fw:
            base = json.load(fw)
        with open('mods.txt', 'r') as fw:
            saved_mods = json.load(fw)

        text = '<b>Проейденные вами модификации:</b>\n'

        i = 0
        while i < len(base):
            result = base[i].split('*')
            title = result[1]
            url = result[0]

            if url in saved_mods:
                text = text + '\n<b>' + str(i + 1) + '. <a href="' + url + '">' + title + '</a></b> '
            else:
                bot.send_message(message.chat.id, 'Удаляем ' + title + ', потому что этого мода нету в базе данных.',
                                 parse_mode='HTML', disable_web_page_preview=True)
                base.pop(i)

                with open('users/' + str(message.from_user.id) + '.txt', 'w') as fw:
                    json.dump(base, fw)

            i = i + 1

        bot.send_message(message.from_user.id, text, parse_mode='HTML', disable_web_page_preview=True)
        msg = bot.send_message(message.from_user.id, 'Введите номер из списка, который нужно удалить. Либо "-", если передумали.', parse_mode='HTML', disable_web_page_preview=True)
        bot.register_next_step_handler(msg, check_delete_my_mods)
    else:
        bot.send_message(message.from_user.id, 'У тебя нету пройденных модификаций, нечего удалять!')

def check_delete_my_mods(message):
    if os.path.exists('users/' + str(message.from_user.id) + '.txt') == True:
        with open('users/' + str(message.from_user.id) + '.txt', 'r') as fw:
            base = json.load(fw)
        with open('mods.txt', 'r') as fw:
            saved_mods = json.load(fw)

        if message.text.isdigit() == True:
            if int(message.text) >= 1 and int(message.text) <= len(base):
                result = base[int(message.text) - 1].split('*')
                title = result[1]

                bot.send_message(message.from_user.id, 'Удаляем ' + title)

                base.pop(int(message.text) - 1)

                if len(base) == 0:
                    if os.path.exists('users/' + str(message.from_user.id) + '_config.txt') == True:
                        check_list = False

                        with open('users/' + str(message.from_user.id) + '_config.txt', 'w') as fw:
                            json.dump(check_list, fw)

                        text = ', в вашем списке не осталось модов, проверка отключена!'

                        if message.from_user.username != None:
                            bot.send_message(message.chat.id, str(message.from_user.username) + text)
                        elif message.from_user.first_name != None and (message.from_user.last_name) != None:
                            bot.send_message(message.chat.id, str(message.from_user.first_name) + ' ' + str(
                                message.from_user.last_name) + text)
                        elif message.from_user.first_name != None:
                            bot.send_message(message.chat.id, str(message.from_user.first_name) + text)
                        elif message.from_user.last_name != None:
                            bot.send_message(message.chat.id, str(message.from_user.last_name) + text)

                with open('users/' + str(message.from_user.id) + '.txt', 'w') as fw:
                    json.dump(base, fw)

                with open('users/' + str(message.from_user.id) + '.txt', 'r') as fw:
                    base = json.load(fw)

                text = '<b>Проейденные вами модификации:</b>\n'

                i = 0
                while i < len(base):
                    result = base[i].split('*')
                    title = result[1]
                    url = result[0]

                    if url in saved_mods:
                        text = text + '\n<b>' + str(i + 1) + '. <a href="' + url + '">' + title + '</a></b> '
                    else:
                        bot.send_message(message.chat.id, 'Удаляем ' + title + ', потому что этого мода нету в базе данных.', parse_mode='HTML', disable_web_page_preview=True)
                        base.pop(i)

                        with open('users/' + str(message.from_user.id) + '.txt', 'w') as fw:
                            json.dump(base, fw)

                    i = i + 1

                bot.send_message(message.from_user.id, text, parse_mode='HTML', disable_web_page_preview=True)

            elif int(message.text) < 1 or int(message.text) > len(base):
                msg = bot.send_message(message.from_user.id, 'Такого номера нету в списке!')
                bot.register_next_step_handler(msg, check_delete_my_mods)
        else:
            if message.text == '-':
                bot.send_message(message.from_user.id, 'Отменяем операцию...')
                return
            else:
                msg = bot.send_message(message.from_user.id, 'Неверный символ! Если писали число, то его нужно писать без каких-либо знаков.')
                bot.register_next_step_handler(msg, check_delete_my_mods)
    else:
        bot.send_message(message.from_user.id, 'У тебя нету пройденных модификаций, нечего удалять!')
        return

@bot.message_handler(commands = ['info'])
def get_num_mods(message):
    with open('mods.txt', 'r') as fw:
        saved_mods = json.load(fw)

    max_num = len(saved_mods)

    markup = types.InlineKeyboardMarkup()
    btn_d = types.InlineKeyboardButton(text='Написать в тему', url='https://ap-pro.ru/forums/topic/2492-telegram-bot-s-podborkoy-sluchaynyh-modov/')
    markup.add(btn_d)

    bot.send_message(message.chat.id, '<b>Создатель бота:</b> AziatkaVictor\n<b>Дата первого билда:</b> 04.04.2021\n\nУ нас в базе данных около ' + str(max_num) + ' модов!\nЕсли у тебя есть идеи по улучшению бота или ты заметил какую-то ошибку, то смело можешь писать в тему, ссылку на которую указана ниже.', parse_mode='HTML', reply_markup = markup)

@bot.message_handler(commands = ['start'])
def get_start(message):
    bot.send_message(message.chat.id, 'Привет, напиши /help чтобы увидеть список команд.')

@bot.message_handler(content_types=['text'])
def get_text(message):

    text = str(message.text.lower())

    if re.search(r'\bпосоветуйте мод\b', text) or re.search(r'\bво что поиграть\b', text) or re.search(r'\bв какой мод поиграть\b', text):
        mods = []
        titles = []
        i = 0

        sqr = 'https://ap-pro.ru/stuff/page/1'
        page = requests.get(sqr)
        page_tree = html.fromstring(page.content)
        mods.extend(page_tree.xpath('//*[@id="ipsLayout_mainArea"]/div[1]/ul/li[2]/div/p[1]/a[@class="ipsButton ipsButton_veryVerySmall ipsButton_primary buttoncaatmods"]/@href'))
        titles.extend(page_tree.xpath('//*[@id="ipsLayout_mainArea"]/div[1]/ul/li[2]/div/p[1]/a[@class="ipsButton ipsButton_veryVerySmall ipsButton_primary buttoncaatmods"]/text()'))

        text = '<b>Если не знаешь, во что поиграть, то вот тебе разделы, по категориям:</b>\n'

        while i < len(mods):

            title = [titles[i]]
            title = title[0].encode('raw-unicode-escape').decode('utf-8')
            title = title.replace('  ','')
            title = title.replace('   ', '')
            title = title.replace('    ', '')
            title = title.replace('\n', '')

            url = [mods[i]]
            url = 'https://ap-pro.ru/' + url[0].encode('raw-unicode-escape').decode('utf-8')

            text = text + '\n<b>' + str(i + 1) + '.</b> <a href="' + url + '">' + title + '</a>'
            text = text + '\n<b>' + str(i + 1) + '.</b> <a href="' + url + '">' + title + '</a>'

            i = i + 1

        text = text + '\n\n<b>Также можешь написать следующие команды:</b>\n\n/random - Случайный мод\n/random_soc - Случайный мод на Тень Чернобыля\n/random_cs - Случайный мод на Чистое Небо\n/random_cop - Случайный мод на Зов Припяти\n/new - Последние релизы'

        bot.send_message(message.chat.id, text, parse_mode='HTML', disable_web_page_preview=True)

bot.polling(none_stop=True, interval=0)
