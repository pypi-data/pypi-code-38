# @Vendors
import pymongo

# @Error handler
from nlp_model_gen.packages.errorHandler.ErrorHandler import ErrorHandler

# @Log colors
from nlp_model_gen.packages.logger.assets.logColors import ERROR_COLOR

# @Constants
from nlp_model_gen.constants.constants import (
    DB_GENERAL_SETTINGS_DB,
    DB_AUTOINCREMENTAL_ID_COL,
    DB_CONNECTION_TIMEOUT,
    DB_OPERATION_DELETE,
    DB_OPERATION_DELETE_MANY,
    DB_OPERATION_INSERT,
    DB_OPERATION_INSERT_MANY,
    DB_OPERATION_UPDATE,
    DB_SERVER_URL
)

def connect():
    return pymongo.MongoClient(DB_SERVER_URL, serverSelectionTimeoutMS=DB_CONNECTION_TIMEOUT)

def db_check_collection(db_name, col_name):
    db = connect()[db_name]
    try:
        return col_name in db.collection_names()
    except Exception as e:
        ErrorHandler.raise_error('E-0002', [{'text': e, 'color': ERROR_COLOR}])

def get_collection(db_name, col_name):
    db = connect()[db_name]
    return db[col_name]

def db_get_item(db_name, col_name, query=None, fields=None):
    try:
        col = get_collection(db_name, col_name)
        return col.find_one(query, fields)
    except Exception as e:
        ErrorHandler.raise_error('E-0003', [{'text': e, 'color': ERROR_COLOR}])

def db_get_items(db_name, col_name, query=None, fields=None):
    try:
        col = get_collection(db_name, col_name)
        return list(col.find(query, fields))
    except Exception as e:
        ErrorHandler.raise_error('E-0004', [{'text': e, 'color': ERROR_COLOR}])

def db_insert_item(db_name, col_name, element):
    try:
        col = get_collection(db_name, col_name)
        return col.insert_one(element)
    except Exception as e:
        ErrorHandler.raise_error('E-0005', [{'text': e, 'color': ERROR_COLOR}])

def db_insert_items(db_name, col_name, elements):
    try:
        col = get_collection(db_name, col_name)
        return col.insert(elements)
    except Exception as e:
        ErrorHandler.raise_error('E-0006', [{'text': e, 'color': ERROR_COLOR}])

def db_update_item(db_name, col_name, query, updated_item):
    try:
        search_query = query if query is not None else {}
        col = get_collection(db_name, col_name)
        return col.update_one(search_query, {'$set': updated_item})
    except:
        ErrorHandler.raise_error('E-0007')

def db_update_many(db_name, col_name, query, updated_item):
    try:
        search_query = query if query is not None else {}
        col = get_collection(db_name, col_name)
        return col.update_many(search_query, {'$set': updated_item})
    except:
        ErrorHandler.raise_error('E-0008')

def db_delete_item(db_name, col_name, query):
    try:
        col = get_collection(db_name, col_name)
        return col.delete_one(query)
    except Exception as e:
        ErrorHandler.raise_error('E-0009', [{'text': e, 'color': ERROR_COLOR}])

def db_delete_items(db_name, col_name, query):
    try:
        col = get_collection(db_name, col_name)
        return col.delete_many(query)
    except Exception as e:
        ErrorHandler.raise_error('E-0010', [{'text': e, 'color': ERROR_COLOR}])

def db_drop_collection(db_name, col_name):
    try:
        col = get_collection(db_name, col_name)
        col.drop()
    except Exception as e:
        ErrorHandler.raise_error('E-0011', [{'text': e, 'color': ERROR_COLOR}])

def db_get_autoincremental_id(col_name):
    try:
        col = get_collection(DB_GENERAL_SETTINGS_DB, DB_AUTOINCREMENTAL_ID_COL)
        next_entry = col.find_and_modify(
            {'collection': col_name},
            {'$inc': {'next_id': 1}},
            True
        )
        return next_entry['next_id'] if next_entry else 1
    except Exception as e:
        ErrorHandler.raise_error('E-0117', [{'text': e, 'color': ERROR_COLOR}])

def insert(db, collection_name, data=None, query=None):
    col = db[collection_name]
    col.insert_one(data)

def insert_many(db, collection_name, data=None, query=None):
    col = db[collection_name]
    col.insert(data)

def update(db, collection_name, data=None, query=None):
    col = db[collection_name]
    col.update_one(query, {'$set': data})

def delete(db, collection_name, data=None, query=None):
    col = db[collection_name]
    col.delete_one(query)

def delete_all(db, collection_name, data=None, query=None):
    col = db[collection_name]
    col.delete_many(query)

transaction_operation_types = {
    DB_OPERATION_INSERT: insert,
    DB_OPERATION_UPDATE: update,
    DB_OPERATION_INSERT_MANY: insert_many,
    DB_OPERATION_DELETE: delete,
    DB_OPERATION_DELETE_MANY: delete_all
}

def db_batch_operation(db_name, operations):
    db = connect()[db_name]
    try:
        for operation in operations:
            col_name = operation['col_name']
            data = None
            query = None
            if 'data' in operation.keys():
                data = operation['data']
            if 'query' in operation.keys():
                query = operation['query']
            if operation['type'] in transaction_operation_types:
                transaction_operation_types[operation['type']](db, col_name, data=data, query=query)
    except Exception as e:
        ErrorHandler.raise_error('E-0012', [{'text': e, 'color': ERROR_COLOR}])
