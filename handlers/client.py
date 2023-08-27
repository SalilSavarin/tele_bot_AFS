import datetime
import sqlite3

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import os
import logging

from create_bot import bot
from keybords import kb_client, kb_button_menu
from utils.main_funcs import read_xlsx_file, \
    search_number_request, \
    assembly_message, \
    save_xlsx_for_num_req, \
    search_by_date, \
    search_result_file,\
    checking_repeating_objects

logging.basicConfig(filename='bot_log.log',
                    filemode='a',
                    encoding='UTF-8',
                    level=logging.INFO,
                    format='%(asctime)s %(message)s')


class FSMSearch_request(StatesGroup):
    number_request = State()


class FSMSearch_by_date(StatesGroup):
    date = State()


class FSMadd_requests_to_tracking(StatesGroup):
    number_request = State()


# Начало поиска простого поиска результата по номеру заявки
# @dp.message_handler(commands='Search_result', state=None)
async def command_start_search_request(message: types.Message):
    await FSMSearch_request.number_request.set()
    await bot.send_message(message.from_user.id, 'Введи номер заявки (Пример номера заявки 10-001/01-23)')


# Получаем номер заявки
# @dp.message_handler(state=FSMSearch.number_request)
async def take_number_request(message: types.Message, state: FSMContext):
    nir = read_xlsx_file('NIR_results.xlsx')
    my_cwd = os.getcwd()
    async with state.proxy() as data:
        data['number_request'] = message.text
        list_file = search_result_file(number_request=data['number_request'])
        search_result = search_number_request(nir, data['number_request'])
        text_for_mes = assembly_message(search_result, data['number_request'])
        logging.info("Пользователь {0} предал боту номер заявки {1}."
                     " Длинна сообщения {2}".format(message.from_user.first_name,
                                                    data['number_request'],
                                                    len(text_for_mes)))
        if len(text_for_mes) > 4096:
            await bot.send_message(message.from_user.id,
                                   'Слишком длинное сообщение с результатами анализов.'
                                   '\nБот пришлет .xlsx фаил с результатами.')
            save_xlsx_for_num_req(nir, data['number_request'])
            name_for_open = data['number_request'].replace('/', '-')
            path = os.path.join(my_cwd, name_for_open)
            xlsx_file = open(f'{path}.xlsx', 'rb')
            await bot.send_document(message.from_user.id, xlsx_file)
            os.remove(f'{name_for_open}.xlsx')
        elif len(search_result) == 0:
            await bot.send_message(message.from_user.id, f'По номеру заявки: {data["number_request"]} '
                                                         f'ничего не нашлось.\n'
                                                         f'Проверьте корректность номера или анализ еще не готов.')
        else:
            await bot.send_message(message.from_user.id, text_for_mes)
            save_xlsx_for_num_req(nir, data['number_request'])
            name_for_open = data['number_request'].replace('/', '-')
            path = os.path.join(my_cwd, name_for_open)
            xlsx_file = open(f'{path}.xlsx', 'rb')
            await bot.send_document(message.from_user.id, xlsx_file)
            os.remove(f'{name_for_open}.xlsx')
            if list_file is not None:
                media = types.MediaGroup()
                for file_path in list_file:
                    media.attach_document(types.InputFile(file_path))
                await bot.send_media_group(message.from_user.id, media=media)
    await state.finish()


# Начало поиска заявок по дате
# @dp.message_handler(commands=['Search_by_date'])
async def command_search_by_date(message: types.Message):
    await FSMSearch_by_date.date.set()
    await bot.send_message(message.from_user.id, 'Введи дату, когда отдавали на анализ (Пример даты 2023-12-31)')


# Получаем дату анализа
# @dp.register_message_handler(FSMSearch_by_date.date)
async def take_date(message: types.Message, state: FSMContext):
    nir = read_xlsx_file('NIR_results.xlsx')
    my_cwd = os.getcwd()
    async with state.proxy() as data:
        data['date'] = message.text
        search_result = search_by_date(data=nir, date=data['date'])
        text = 'По дате {0} было найдено:\n {1}'.format(data['date'], search_result.to_string(index=False))
        logging.info('Пользователь {0} передал боту дату {1}. '
                     'Длинна сообщения {2}.'.format(message.from_user.first_name,
                                                    data['date'],
                                                    len(text)))
        if len(text) > 4096:
            await bot.send_message(message.from_user.id, 'Слишком длинное сообщение с результатами анализов.'
                                                         '\nБот пришлет .xlsx фаил с результатами.')
            search_result.to_excel('slice_by_date.xlsx')
            path = os.path.join(my_cwd, 'slice_by_date')
            xlsx_file = open(f'{path}.xlsx', 'rb')
            await bot.send_document(message.from_user.id, xlsx_file)
            os.remove('slice_by_date.xlsx')
        elif len(search_result) == 0:
            await bot.send_message(message.from_user.id,
                                   f'По дате: {data["date"]} ничего не нашлось.\n'
                                   f'Проверьте корректность даты - укажите другую дату.')
        else:
            await bot.send_message(message.from_user.id, text)
            search_result.to_excel('slice_by_date.xlsx')
            path = os.path.join(my_cwd, 'slice_by_date')
            xlsx_file = open(f'{path}.xlsx', 'rb')
            await bot.send_document(message.from_user.id, xlsx_file)
            os.remove('slice_by_date.xlsx')
    await state.finish()


# @dp.message_handler(commands=['Add_request_to_tracking'])
async def command_add_requests_to_tracking(message: types.Message):
    await FSMadd_requests_to_tracking.number_request.set()
    await bot.send_message(message.from_user.id, 'Введите номер заявки для отслеживания.\n'
                                                 'Пример номера заявки - 10-001/01-23')


async def start_tracking(message: types.Message, state: FSMContext):
    date = datetime.date.today()
    async with state.proxy() as data:
        data['number_request'] = message.text
        conn = sqlite3.connect(r'C:\Users\yan-s\Desktop\MyRepo\bot_AFS\database\tracking_requests.db')
        check = checking_repeating_objects(data['number_request'], message.from_user.id, conn)
        if check is False:
            await bot.send_message(message.from_user.id,
                                   'Вами уже была добавлена заявка {0} в отслеживание'.format(data['number_request']))
            await state.finish()
            return
        cursor = conn.cursor()
        req = '''INSERT INTO users_requests 
        (telegram_id, user_name, number_requests, date)
        VALUES (?, ?, ?, ?)'''
        cursor.execute(req, (message.from_user.id, message.from_user.first_name, data['number_request'], date))
        conn.commit()
        conn.close()
        await bot.send_message(message.from_user.id,
                               'Заявка {0} была успешно добавлена для отслеживания'.format(data['number_request']))
    await state.finish()


# @dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    await bot.send_message(message.from_user.id,
                           f'Привет, {message.from_user.first_name}! '
                           f'Воспользуйся кнопками меню для упрощенного взаимодействия c ботом.',
                           reply_markup=kb_client)


# @dp.message_handler(commands=['help'])
async def command_help(message: types.Message):
    await bot.send_message(message.from_user.id, '''Бот имеет клавиатуру с основными кнопками:
    ->/Menu - Меню основных функций бота.
    ->/Contacts - Список номеров всех сотрудников ОКК. 
    
    Основные функции бота
    ->/Menu->/Search_result - Поиск результатов по номеру заявки НИР, в ответ бот пришлет сообщение и .xlsx файл с 
    результатами и хроматограммы анализа.
    Пример номера заявки, который нужно написать боту - 10-001/01-23
    ->/Menu->/Search_by_date - Поиск заявок по дате, в ответ бот пришлет сообщение и .xlsx файл с номерами заявок, 
    названием продукта и серией.
    Пример даты, который нужно написать боту - 2023-12-31
    ->/Menu->/Add_request_to_tracking - Добавляет номер заявки в отслеживание. По готовности бот пришлет сообщение и 
    .xlsx файл с результатами. 
    
    ***
    Если сообщение будет превышать 4096 символов, то бот присылает только .xlsx файл
    ***''')


# @dp.message_handler(commands=['contacts'])
async def command_contact(message: types.Message):
    print(message.chat.id)
    await bot.send_message(message.from_user.id, 'Савицкий Ян +79998887766')


async def command_menu(message: types.Message):
    if message.text == '/Menu':
        await bot.send_message(message.from_user.id, '/Menu', reply_markup=kb_button_menu)


async def command_back_menu(message: types.Message):
    if message.text == '/Back':
        await bot.send_message(message.from_user.id, '/Back', reply_markup=kb_client)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start'])
    dp.register_message_handler(command_help, commands=['Help'])
    dp.register_message_handler(command_contact, commands=['Contacts'])
    dp.register_message_handler(command_menu, commands=['Menu'])
    dp.register_message_handler(command_back_menu, commands=['Back'])
    dp.register_message_handler(command_start_search_request, commands=['Search_result'], state=None)
    dp.register_message_handler(take_number_request, state=FSMSearch_request.number_request)
    dp.register_message_handler(command_search_by_date, commands=['Search_by_date'], state=None)
    dp.register_message_handler(take_date, state=FSMSearch_by_date.date)
    dp.register_message_handler(command_add_requests_to_tracking, commands=['Add_request_to_tracking'])
    dp.register_message_handler(start_tracking, state=FSMadd_requests_to_tracking.number_request)
