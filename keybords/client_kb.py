from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# main_menu
button_help = KeyboardButton('/Help')
button_contacts = KeyboardButton('/Contacts')
button_menu = KeyboardButton('/Menu')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client.\
    add(button_menu).\
    add(button_contacts).\
    insert(button_help)

# button_menu
button_search_number_request = KeyboardButton('/Search_result')
button_search_number_request_full_info = KeyboardButton('/Advanced_Search_result')
button_search_by_date = KeyboardButton('/Search_by_date')
button_back = KeyboardButton('/Back')

kb_button_menu = ReplyKeyboardMarkup(resize_keyboard=True)

kb_button_menu.\
    add(button_search_number_request).\
    insert(button_search_by_date).\
    add(button_search_number_request_full_info).\
    add(button_back)
