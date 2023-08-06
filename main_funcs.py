import datetime

import pandas as pd
import pandasql as ps


def read_xlsx_file(file_name: str):
    """
    Функция читает xlsx, после отдает файл в DataFrame
    :param file_name: file name.xlsx
    :return:<class 'pandas.core.frame.DataFrame'>
    """
    file = pd.read_excel(file_name)
    file_df = pd.DataFrame(file)
    file_df['start_date'] = pd.to_datetime(file_df['start_date'])
    file_df['end_date'] = pd.to_datetime(file_df['end_date'])
    return file_df


def search_number_request(data, number: str):
    """
    Функция находит в xlsx файле результаты анализов по номеру заявки
    :param number: номер заявки на анализ
    :param data: таблица результатов в DataFrame
    :return: срез данных из data DataFrame
    """
    df = data
    sql_select = '''
    SELECT number_request, product_name, series_number, analysis_method, result
    FROM df
    WHERE number_request = "{0}"
    '''.format(number)
    select_result = ps.sqldf(sql_select, locals())
    return select_result


def assembly_message(select_df, number_request: str):
    """
    Функция вспомогательная для формирования сообщения пользователю
    :param select_df: таблица результатов в DataFrame
    :param number_request: номер заявки на анализ
    :return: текст сообщения str
    """
    df = select_df
    series_products = df.series_number.unique()
    text_message = '''По номеру заявки {0} нашлось {1} анализ(а-ов).\n\n'''.format(number_request, len(df))
    for series_product in series_products:
        mes = str()
        sql_select = '''
        SELECT product_name, analysis_method, result
        FROM df
        WHERE series_number LIKE "{0}"
        '''.format(series_product)
        select_result = ps.sqldf(sql_select, locals())
        mes += '\n\n{0} - {1}\n\n'.format(select_result['product_name'][0], series_product)
        df_str = select_result.to_string(index=False)
        mes += df_str
        text_message += mes
    return text_message


def save_xlsx(df, number_request: str):
    """
    Функция сохраняет DataFrame в xlsx
    :param df: DataFrame
    :param number_request: используется для имени xlsx файла (number_request.xlsx)
    :return:
    """
    name_for_save = number_request.replace('/', '-')
    df_result = search_number_request(df, number_request)
    df_result.to_excel(f'{name_for_save}.xlsx')


def search_by_date(data, date):
    """

    :param data:
    :param date:
    :return:
    """
    date += '%'
    df = data
    sql_select = '''
    SELECT DISTINCT(number_request), product_name, series_number, start_date
    FROM df
    WHERE start_date LIKE '{0}' 
    '''.format(date)
    select_result = ps.sqldf(sql_select, locals())
    return select_result
