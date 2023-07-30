from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import os

from create_bot import dp, bot
from keybords import kb_client, kb_button_menu
from main_funcs import read_xlsx_file, search_number_request, assembly_message, save_xlsx


class FSMSearch(StatesGroup):
    number_request = State()


# Начало поиска простого поиска результата
# @dp.message_handler(commands='Search_result', state=None)
async def command_start_search_simple(message: types.Message):
    await FSMSearch.number_request.set()
    await bot.send_message(message.from_user.id, 'Введи номер заявки')


# Получаем номер заявки
# @dp.message_handler(state=FSMSearch.number_request)
async def take_number_request(message: types.Message, state: FSMContext):
    nir = read_xlsx_file('NIR_results.xlsx')
    my_cwd = os.getcwd()
    async with state.proxy() as data:
        data['number_request'] = message.text
        search_result = search_number_request(nir, data['number_request'])
        text_for_mes = assembly_message(search_result, data['number_request'])
        if len(text_for_mes) > 4096:
            await bot.send_message(message.from_user.id,
                                   'Слишком длинное сообщение с результатами анализов.\nБот пришлет .xlsx фаил с результатами.')
            save_xlsx(nir, data['number_request'])
            name_for_open = data['number_request'].replace('/', '-')
            path = os.path.join(my_cwd, name_for_open)
            xlsx_file = open(f'{path}.xlsx', 'rb')
            await bot.send_document(message.from_user.id, xlsx_file)
        else:
            await bot.send_message(message.from_user.id, text_for_mes)
            save_xlsx(nir, data['number_request'])
            name_for_open = data['number_request'].replace('/', '-')
            path = os.path.join(my_cwd, name_for_open)
            xlsx_file = open(f'{path}.xlsx', 'rb')
            await bot.send_document(message.from_user.id, xlsx_file)
    os.remove(f'{name_for_open}.xlsx')
    await state.finish()


# @dp.message_handler(commands=['start'])
async def command_start(message: types.Message):
    await bot.send_message(message.from_user.id,
                           f'Привет, {message.from_user.first_name}! Воспользуйся кнопками меню для упрощенного взаимодействия c ботом.',
                           reply_markup=kb_client)


# @dp.message_handler(commands=['help'])
async def command_help(message: types.Message):
    await bot.send_message(message.from_user.id, '''Бот имеет клавиатуру с основными кнопками:
    ->/Menu - Меню основных функций бота
    ->/Contacts - Список номеров всех аналитиков 
    
    Основные функции бота
    ->/Menu->/Search_result - Поиск результатов по номеру заявки НИР, в ответ бот пришлет сообщение и .xlsx файл с результатами.(если сообщение будет превышать 4096 символов, то только .xlsx файл) 
    Пример номера заявки, который нужно написать боту - 10-001/01-23
    ->/Menu->/Search_by_date - ''')


# @dp.message_handler(commands=['contacts'])
async def command_contact(message: types.Message):
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
    dp.register_message_handler(command_start_search_simple, commands=['Search_result'], state=None)
    dp.register_message_handler(take_number_request, state=FSMSearch.number_request)
