# -*- coding: UTF-8 -*
'''
Created on 2018-06-15

@author: trb
'''


def get_mongo_db(dbname, host='localhost', port=27017):
    try:
        from pymongo import Connection
        return Connection(host=host, port=port)[dbname]
    except ImportError as e:
        from pymongo import MongoClient
        client = MongoClient(host=host, port=port)
        return client.get_database(dbname)


def day_end(dt):
    import datetime
    if dt and type(dt) == datetime.date:
        return datetime.datetime(dt.year, dt.month, dt.day, 23, 59, 59)
    return dt
