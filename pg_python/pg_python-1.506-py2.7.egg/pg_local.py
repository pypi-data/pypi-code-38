from ._db_object import Db
from ._write import make_postgres_write_statement,make_postgres_write_multiple_statement
from ._read import make_postgres_read_statement, prepare_values
from ._update import make_postgres_update_statement
from ._update import make_postgres_update_multiple_statement
from ._delete import make_postgres_delete_statement


local_db = None

def _get_db():
    global local_db
    return local_db

print_debug_log = True
params_map = {}


def pg_server(db_name, username, password, host_address, debug=True, send_keep_alive_probes=False, socket_idle_time=120):
  global local_db, print_debug_log, params_map
  params_map = {
    'dbname': db_name,
    'user': username,
    'password': password,
    'host': host_address,
    'send_keep_alive_probes': send_keep_alive_probes,
    'socket_idle_time': socket_idle_time,
    }
  local_db = Db(params_map)
  print_debug_log = debug
  return local_db



def write(table, kv_map):
    """
    :param table: String.
    :param kv_map: Key values.
    :return success_bool:
    """
    global local_db, print_debug_log, params_map
    connection = local_db.get_connection()
    cursor = local_db.get_cursor()
    command, values = make_postgres_write_statement(table, kv_map, print_debug_log)
    try:
        cursor.execute(command, values)
        connection.commit()
    except Exception as e:
        print(("Db Cursor Write Error: %s" % e))
        local_db = Db(params_map)
        return False
    return True

def read(table, keys_to_get, kv_map, limit=None, order_by=None, order_type=None, clause = "=", group_by = None, join_clause = ' AND '):
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
    cursor = local_db.get_cursor()
    command, values = make_postgres_read_statement(table, kv_map, keys_to_get,
                                                   limit, order_by, order_type, print_debug_log,
                                                   clause, group_by, join_clause)
    try:
        cursor.execute(command, values)
        all_values = cursor.fetchall()
        return prepare_values(all_values, keys_to_get)
    except Exception as e:
        print(("Db Cursor Read Error: %s" % e))
        return []

def update(table, update_kv_map, where_kv_map, clause = '='):
    """
    :param table: table name, type string
    :param update_kv_map: the NEW keyvalue map for values to be updated
    :param where_kv_map: the kv map to search for values, all values ARE ANDed.
    :return: Success or Failure.
    """
    global local_db, print_debug_log, params_map
    connection = local_db.get_connection()
    cursor = local_db.get_cursor()
    command, values = make_postgres_update_statement(table, update_kv_map, where_kv_map,
                                                     clause, print_debug_log)
    try:
        cursor.execute(command, values)
        connection.commit()
    except Exception as e:
        print(("Db Cursor Update Error: %s" % e))
        local_db = Db(params_map)
        return False
    return True

def read_raw(command, values):
    """
    :param table: String
    :param keys_to_get: list of strings
    :param kv_map: key value map, if this is None, then limit is maxed at 1000
    :param limit: None or integer
    :param order_by: None or must be of a type String
    :param order_type: String None, "ASC" or "DESC" only
    :return: values in an array of key value maps
    """
    cursor = local_db.get_cursor()
    try:
        if values is not None:
          cursor.execute(command, values)
        else:
          cursor.execute(command)
        all_values = cursor.fetchall()
        return all_values
    except Exception as e:
        print(("Db Cursor Read Error: %s" % e))
        return []

def write_raw(command, values):
    """
    :params command, values. Execution commands dirctly for postgres
    """
    global local_db, print_debug_log, params_map
    connection = local_db.get_connection()
    cursor = local_db.get_cursor()
    try:
        cursor.execute(command, values)
        connection.commit()
    except Exception as e:
        print(("Db Cursor Write Error: %s" % e))
        local_db = Db(params_map)
        return False
    return True


def update_raw(command):
    """
    Update statement in the raw format,
    :param command: SQL command
    :return: number of rows affected
    """
    global local_db, print_debug_log, params_map
    connection = local_db.get_connection()
    cursor = local_db.get_cursor()
    try:
        cursor.execute(command)
        rowcount = cursor.rowcount
        connection.commit()
    except Exception as e:
        print(("Db Cursor Update Error: %s" % e))
        local_db = Db(params_map)
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


def close():
    global local_db, print_debug_log, params_map
    connection = local_db.get_connection()
    cursor = local_db.get_cursor()
    local_db.close_cursor(cursor)
    local_db.close_connection()

def delete(table, where_kv_map):
    """
    Delete the rows resulting from the mentined kv map. No limit.
    :param table: table name, must be string
    :param where_kv_map: the kv map to search for values, all values ARE ANDed.
    :return: True or False
    """
    global local_db, print_debug_log, params_map
    connection = local_db.get_connection()
    cursor = local_db.get_cursor()
    command, values = make_postgres_delete_statement(table, where_kv_map, print_debug_log)
    try:
        cursor.execute(command, values)
        connection.commit()
    except Exception as e:
        print(("Db Cursor Delete Error: %s" % e))
        local_db = Db(params_map)
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
    flag =0
    for dict_val in query_values_dict_lst:
        # check dimensions.
        if len(dict_val)!= expected_length:
            print(("%s doesn't match the dimensions"%(dict_val)))
            return False

        # check columns present.
        for column in all_columns_name:
            if column not in dict_val:
                print(("%s column isn't present in dictionary"%(column)))
                return False
    return True


def update_multiple(table, column_to_update, columns_to_query_lst,
                    query_values_dict_lst):
    """
    Multiple update support in pg_python
    :param table: table to update into
    :param column_to_update: Single column for set clause
    :param columns_to_query_lst: column names for where clause
    :param query_values_dict_lst: values for where and Set.
    :return:
    """
    global local_db, print_debug_log, params_map
    connection = local_db.get_connection()
    cursor = local_db.get_cursor()
    is_pararmeters_correct = check_parameters(column_to_update, columns_to_query_lst, query_values_dict_lst)
    if not is_pararmeters_correct:
        print("ERROR in parameters passsed")
        return

    command,values= make_postgres_update_multiple_statement(table,
                                                              column_to_update,
                                                              columns_to_query_lst,
                                                              query_values_dict_lst,
                                                              print_debug_log)
    try:
        cursor.execute(command,values)
        connection.commit()
    except Exception as e:
        print(("Db Cursor update_multiple Error: %s" % e))
        local_db = Db(params_map)
        return False
    return True



def check_multiple_insert_param(columns_to_insert,insert_values_dict_lst):
    """
    Checks if the pararmeter passed are of correct order.
    :param columns_to_insert:
    :param insert_values_dict_lst:
    :return:
    """
    column_len = len(columns_to_insert)
    for row in insert_values_dict_lst:
        if column_len!= len(row):
            print(("%s doesn't match the dimensions" % (row)))
            return False
        for column in columns_to_insert:
            if column not in row:
                print(("%s column isn't present in dictionary"%(column)))
                return False
    return True



def insert_multiple(table, columns_to_insert_lst, insert_values_dict_lst):
    """
    Multiple row insert in pg_python
    :param table: table to insert into.
    :param columns_to_insert_lst: columns value provided.
    :param insert_values_dict_lst: values of corresponding columns.
    :return:
    """
    global local_db, print_debug_log, params_map
    connection = local_db.get_connection()
    cursor = local_db.get_cursor()
    is_pararmeters_correct = check_multiple_insert_param(columns_to_insert_lst, insert_values_dict_lst)
    if not is_pararmeters_correct:
        print("ERROR in parameters passsed")
        return
    command,values = make_postgres_write_multiple_statement(table, columns_to_insert_lst, insert_values_dict_lst, print_debug_log)
    try:
        cursor.execute(command, values)
        connection.commit()
    except Exception as e:
        print(("Db Cursor Write Error: %s" % e))
        local_db = Db(params_map)
        return False
    return True

