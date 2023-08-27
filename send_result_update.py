import pandasql as ps
import sqlite3
import os
import requests

from utils.main_funcs import read_xlsx_file, search_result_file, assembly_message, save_xlsx_for_num_req

os.environ["TOKEN_TELE"] = "сюда токен"


def send_update(conn):
    df = read_xlsx_file('NIR_results.xlsx')
    req = 'SELECT telegram_id, number_requests, len_result, count_file FROM users_requests'
    cursor = conn.execute(req)
    users_subscription = cursor.fetchall()
    for info in users_subscription:
        telegram_id = info[0]
        number_requests = info[1]
        len_result = info[2]
        count_file = info[3]
        sql_select = '''
            SELECT number_request, product_name, series_number, analysis_method, result
            FROM df
            WHERE number_request = "{0}"
            '''.format(number_requests)
        list_file = search_result_file(number_requests)
        select_result = ps.sqldf(sql_select, locals())
        if len(select_result) > len_result:
            text = assembly_message(select_result, number_requests)
            req = '''UPDATE users_requests SET len_result = (?)
            WHERE telegram_id = ? AND number_requests LIKE ?'''
            conn.execute(req, (len(select_result), telegram_id, number_requests))
            conn.commit()
            name_for_save = number_requests.replace('/', '-')
            select_result.to_excel(f'{name_for_save}.xlsx')
            requests.post(
                url='https://api.telegram.org/bot{0}/{1}'.format(os.getenv('TOKEN_TELE'), 'sendDocument'),
                data={'chat_id': telegram_id, 'caption': text},
                files={'document': open(f'{name_for_save}.xlsx', 'rb')}
            )
            os.remove(f'{name_for_save}.xlsx')
    #     if list_file is not None and len(list_file) > count_file:
    #         req = '''UPDATE users_requests SET count_file = (?)
    #         WHERE telegram_id = ? AND number_requests LIKE ?'''
    #         conn.execute(req, (len(list_file), telegram_id, number_requests))
    #         # conn.commit()
    #         files = [json.loads({'type': 'document', 'media': open(x, 'rb')}) for x in list_file]
    #         requests.post(
    #             url='https://api.telegram.org/bot{0}/{1}'.format(os.getenv('TOKEN_TELE'), 'sendMediaGroup'),
    #             data={'chat_id': telegram_id},
    #             files={'media': json.load(files)}
    #         )
    # return users_subscription


def main():
    conn = sqlite3.connect(r'C:\Users\yan-s\Desktop\MyRepo\bot_AFS\database\tracking_requests.db')
    send_update(conn)
    conn.close()

if __name__ == '__main__':
   main()
