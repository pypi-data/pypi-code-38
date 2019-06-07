from ._db_object import Db
from ._write import make_postgres_write_statement, make_postgres_write_multiple_statement
from ._read import make_postgres_read_statement, prepare_values
from ._update import make_postgres_update_statement
from ._update import make_postgres_update_multiple_statement
from ._delete import make_postgres_delete_statement
from ._update import make_postgres_update_multiple_column_statement
from ._update import check_parameters_multicol
import logging

db_dict = {}

def get_db(server="default"):
    db_obj = db_dict.get(server, None)
    return db_obj

print_debug_log = True


def pg_server(db_name, username, password, host_address, debug=True, server="default"):
    global print_debug_log
    params_map = {
        'dbname'  : db_name,
        'user'    : username,
        'password': password,
        'host'    : host_address,
    }
    db_obj = Db(params_map)
    db_dict[server] = db_obj
    print_debug_log = debug
    return db_obj


def write(table, kv_map, server="default"):
    """
    :param table: String.
    :param kv_map: Key values.
    :param server: Alias of the server
    :return success_bool:
    """
    global print_debug_log
    db_obj = get_db(server)
    connection = db_obj.get_connection()

    command, values = make_postgres_write_statement(table, kv_map, print_debug_log)
    try:
        cursor = db_obj.get_cursor()
        cursor.execute(command, values)
        connection.commit()

    except Exception as e:
        logging.info("Db Cursor Write Error: %s" % e)
        db_obj_reconnect = Db(db_obj.params)
        db_dict.pop(server)
        db_dict[server] = db_obj_reconnect
        return False
    return True

def read(table, keys_to_get, kv_map, limit=None, order_by=None, order_type=None, clause="=", group_by=None,
         join_clause=' AND ', server="default"):
    """
    :param table: String
    :param keys_to_get: list of strings
    :param kv_map: key value map, if this is None, then limit is maxed at 1000
    :param limit: None or integer
    :param order_by: None or must be of a type String
    :param order_type: String None, "ASC" or "DESC" only
    :return: values in an array of key value maps
    """
    error_return = None
    db_obj = get_db(server)
    cursor = db_obj.get_cursor()
    command, values = make_postgres_read_statement(table, kv_map, keys_to_get,
                                                   limit, order_by, order_type, print_debug_log,
                                                   clause, group_by, join_clause)

    try:
        cursor.execute(command, values)
        all_values = cursor.fetchall()
        return prepare_values(all_values, keys_to_get)
    except Exception as e:
        logging.warning("Db Cursor Read Error: %s" % e)
        return []

def update(table, update_kv_map, where_kv_map, clause='=', server="default"):
    """
    :param table: table name, type string
    :param update_kv_map: the NEW keyvalue map for values to be updated
    :param where_kv_map: the kv map to search for values, all values ARE ANDed.
    :return: Success or Failure.
    """
    global print_debug_log
    db_obj = get_db(server)
    connection = db_obj.get_connection()
    cursor = db_obj.get_cursor()
    command, values = make_postgres_update_statement(table, update_kv_map, where_kv_map,
                                                     clause, print_debug_log)
    try:
        cursor.execute(command, values)
        return_dict = {'Status': True}
        logging.info("%s Record(s) Updated", cursor.rowcount)
        connection.commit()
    except Exception as e:
        logging.warning("Db Cursor Update Error: %s" % e)
        db_obj_reconnect = Db(db_obj.params)
        db_dict.pop(server)
        db_dict[server] = db_obj_reconnect
        return False
    return return_dict

def read_raw(command, values, server="default"):
    """
    :param table: String
    :param keys_to_get: list of strings
    :param kv_map: key value map, if this is None, then limit is maxed at 1000
    :param limit: None or integer
    :param order_by: None or must be of a type String
    :param order_type: String None, "ASC" or "DESC" only
    :return: values in an array of key value maps
    """
    db_obj = get_db(server)
    cursor = db_obj.get_cursor()
    try:
        if values not in [None, [], {}]:
            cursor.execute(command, values)
        else:
            cursor.execute(command)
        all_values = cursor.fetchall()
        return all_values
    except Exception as e:
        logging.warning("Db Cursor Read Error: %s" % e)
        return []

def write_raw(command, values, server="default"):
    """
    :params command, values. Execution commands dirctly for postgres
    """
    global print_debug_log
    db_obj = get_db(server)
    connection = db_obj.get_connection()
    cursor = db_obj.get_cursor()
    try:
        cursor.execute(command, values)
        connection.commit()
    except Exception as e:
        logging.warning("Db Cursor Write Error: %s" % e)
        db_obj_reconnect = Db(db_obj.params)
        db_dict.pop(server)
        db_dict[server] = db_obj_reconnect
        return False
    return True


def update_raw(command, server="default"):
    """
    Update statement in the raw format,
    :param command: SQL command
    :return: number of rows affected
    """
    global print_debug_log
    db_obj = get_db(server)
    connection = db_obj.get_connection()
    cursor = db_obj.get_cursor()
    try:
        cursor.execute(command)
        rowcount = cursor.rowcount
        connection.commit()
    except Exception as e:
        logging.warning("Db Cursor Update Error: %s" % e)
        db_obj_reconnect = Db(db_obj.params)
        db_dict.pop(server)
        db_dict[server] = db_obj_reconnect
        return -1
    return rowcount

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_ok(s):
    print((bcolors.OKGREEN + s + bcolors.ENDC))

def print_warn(s):
    print((bcolors.WARNING + s + bcolors.ENDC))

def print_fail(s):
    print((bcolors.FAIL + s + bcolors.ENDC))

def close(server="default"):
    logging.info("Closing connection for server %s" %server)
    db_obj = get_db(server)
    connection = db_obj.get_connection()
    try:
        cursor = db_obj.get_cursor()
        db_obj.close_cursor(cursor)
        db_obj.close_connection()
    except Exception as e:
        logging.error("Could not close connection properly: %s" % e)


def close_all():
    for server in list(db_dict.keys()):
        close(server)


def delete(table, where_kv_map, server="default"):
    """
    Delete the rows resulting from the mentined kv map. No limit.
    :param table: table name, must be string
    :param where_kv_map: the kv map to search for values, all values ARE ANDed.
    :return: True or False
    """
    global print_debug_log
    db_obj = get_db(server)
    connection = db_obj.get_connection()
    cursor = db_obj.get_cursor()
    command, values = make_postgres_delete_statement(table, where_kv_map, print_debug_log)
    try:
        cursor.execute(command, values)
        logging.info("%s Record(s) Deleted" %cursor.rowcount)
        connection.commit()
    except Exception as e:
        logging.warning("Db Cursor Delete Error: %s" % e)
        db_obj_reconnect = Db(db_obj.params)
        db_dict.pop(server)
        db_dict[server] = db_obj_reconnect
        return False
    return True

def check_parameters(column_to_update, columns_to_query_lst, query_values_dict_lst):
    """
    check_prarameters checks whether the passed parameters are valid or not.
    :param column_to_update: name of column that is to be updated.
    :param columns_to_query_lst: list of column names that is used in where clause.
    :param query_values_dict_lst: list of dictionaries containing values for where clause and target column.
    :return: boolean
    """
    # check if dimensions are correct.
    expected_length = 1 + len(columns_to_query_lst)
    all_columns_name = ["update"] + columns_to_query_lst
    flag = 0
    for dict_val in query_values_dict_lst:
        # check dimensions.
        if len(dict_val) != expected_length:
            logging.error("%s doesn't match the dimensions" % (dict_val))
            return False

        # check columns present.
        for column in all_columns_name:
            if column not in dict_val:
                logging.error("%s column isn't present in dictionary" % (column))
                return False
    return True

def update_multiple(table, column_to_update, columns_to_query_lst,
                    query_values_dict_lst, server="default", typecast = ""):
    """
    Multiple update support in pg_python
    :param table: table to update into
    :param column_to_update: Single column for set clause
    :param columns_to_query_lst: column names for where clause
    :param query_values_dict_lst: values for where and Set.
    :param server: server from the pg_server's db_obj list
    :param typecast: typecase statement to be appended after c.update e.g. "::int", must be a string
    :return:
    """
    global print_debug_log
    db_obj = get_db(server)
    connection = db_obj.get_connection()
    cursor = db_obj.get_cursor()
    is_parameters_correct = check_parameters(column_to_update, columns_to_query_lst, query_values_dict_lst)
    if not is_parameters_correct:
        logging.error("ERROR in parameters passed")
        return
    if not isinstance(typecast, str):
        logging.error("typecase param is not a string, it must be a string")
    command, values = make_postgres_update_multiple_statement(table,
                                                              column_to_update,
                                                              columns_to_query_lst,
                                                              query_values_dict_lst,
                                                              print_debug_log,
                                                              typecast_suffix=typecast)
    try:
        cursor.execute(command, values)
        return_dict = {'Status': True}
        count = cursor.rowcount
        return_dict['rowcount'] = count

        connection.commit()
    except Exception as e:
        logging.warning("Db Cursor update_multiple Error: %s" % e)
        db_obj_reconnect = Db(db_obj.params)
        db_dict.pop(server)
        db_dict[server] = db_obj_reconnect
        return {'status': False}
    return return_dict

def update_multiple_col(table, columns_to_update_lst, columns_to_query_lst, query_values_dict_lst,
                        server="default"):
    """
    Multiple update support in pg_python
    :param table: table to update into, string
    :param columns_to_update_lst: list of column names to be updated for set clause, list of strings
    :param columns_to_query_lst: list of column names to be queried for where clause, list of strings
    :param query_values_dict_lst: list of dictionaries with values for where query and update params. Has 2 items-
            update dictionary - with key='update' and value as dictionary of column name and values to be updated
            where dictionary - with key='where' and value as dictionary of column names and values to be queried
            e.g. [{'where':{'id':1}, 'update':{'col1':'ABC', 'col2':'XYZ'}}]
    :return: dictionary of status (boolean) and num of updated records - {'status':True,'updated_records':1}
    """
    global print_debug_log
    db_obj = get_db(server)
    connection = db_obj.get_connection()
    cursor = db_obj.get_cursor()
    is_parameters_correct = check_parameters_multicol(columns_to_update_lst, columns_to_query_lst,
                                                      query_values_dict_lst)
    if not is_parameters_correct:
        logging.error("ERROR in parameters passed")
        return {'status': False}

    command, values =  make_postgres_update_multiple_column_statement(table,
                                                                      columns_to_update_lst,
                                                                      columns_to_query_lst,
                                                                      query_values_dict_lst,
                                                                      print_debug_log)
    try:
        cursor.execute(command, values)
        count = cursor.rowcount
        connection.commit()
    except Exception as e:
        logging.warning("Db Cursor update_multiple Error: %s" % e)
        db_obj_reconnect = Db(db_obj.params)
        db_dict.pop(server)
        db_dict[server] = db_obj_reconnect
        return {'status': False}
    return {'status':True, 'updated_records':count}

def check_multiple_insert_param(columns_to_insert, insert_values_dict_lst):
    """
    Checks if the pararmeter passed are of correct order.
    :param columns_to_insert:
    :param insert_values_dict_lst:
    :return:
    """
    column_len = len(columns_to_insert)
    for row in insert_values_dict_lst:
        if column_len != len(row):
            logging.error("%s doesn't match the dimensions" % (row))
            return False
        for column in columns_to_insert:
            if column not in row:
                logging.error("%s column isn't present in dictionary" % (column))
                return False
    return True

def insert_multiple(table, columns_to_insert_lst, insert_values_dict_lst, server="default"):
    """
    Multiple row insert in pg_python
    :param table: table to insert into.
    :param columns_to_insert_lst: columns value provided.
    :param insert_values_dict_lst: values of corresponding columns.
    :return:
    """
    global print_debug_log
    db_obj = get_db(server)
    connection = db_obj.get_connection()
    cursor = db_obj.get_cursor()
    is_pararmeters_correct = check_multiple_insert_param(columns_to_insert_lst, insert_values_dict_lst)
    if not is_pararmeters_correct:
        logging.error("ERROR in parameters passed")
        return
    command, values = make_postgres_write_multiple_statement(table, columns_to_insert_lst, insert_values_dict_lst,
                                                             print_debug_log)
    try:
        cursor.execute(command, values)
        connection.commit()
    except Exception as e:
        logging.error("Db Cursor Write Error: %s" % e)
        db_obj_reconnect = Db(db_obj.params)
        db_dict.pop(server)
        db_dict[server] = db_obj_reconnect
        return False
    return True
