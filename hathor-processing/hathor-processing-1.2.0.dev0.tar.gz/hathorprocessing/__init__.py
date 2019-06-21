import os

import pandas
from sqlalchemy import create_engine


def save_result(result):
    if not isinstance(result, pandas.DataFrame):
        raise ValueError('Result should be type of DataFrame')
    file = os.path.join(os.getenv('RESULT_PATH'), 'result.json')
    result.to_json(file, orient='records')


def read_prev_result():
    file = os.path.join(os.getenv('RESULT_PATH'), 'result.json')
    return pandas.read_json('file://' + file, orient='records')


def read_data(table, columns, chunksize=1000):
    conn = create_engine(os.getenv('DB_URL')).connect()
    return pandas.read_sql_table(table, conn, columns=columns, chunksize=chunksize)
