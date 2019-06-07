import logging


def make_postgres_update_statement(table, kv_map, where_kv_map, clause, debug = True):
    _prefix = "UPDATE"
    clause = " " + clause + " "
    keys = ",".join([k + "=%s" for k in list(kv_map.keys())])
    where_keys = " AND ".join([k + clause + "%s" for k in list(where_kv_map.keys())])
    value_proxy_array = ["%s"] * len(kv_map)
    value_proxy_string = " , ".join(value_proxy_array)
    statement = " ".join([_prefix, table, "SET", keys, "WHERE", where_keys])
    if debug:
        logging.info("Updating into Db: %s, %s" %(statement, list(kv_map.values()) + list(where_kv_map.values())))
    return statement, list(kv_map.values()) + list(where_kv_map.values())


def get_from_clause(query_values_dict_lst,columns_to_query_lst):
    """
    returns from clause that contains tuples of placeholders
    :param query_values_dict_lst:
    :param columns_to_query_lst:
    :return:
    """
    from_str = "from (values "
    length = len(columns_to_query_lst)+1
    placeholder_str = ["%s"] * length
    row_str = ",".join(placeholder_str)
    row_str = "(" + row_str + ")"
    num_of_dict = len(query_values_dict_lst)
    multi_row_str = [row_str]*num_of_dict
    multi_row_str = ",".join(multi_row_str)
    from_str = from_str +multi_row_str +")"
    return from_str


def get_as_clause(columns_to_query_lst):
    """
    get_as_clause will return all column names tuples.
    :param columns_to_query_lst: columns for where clause
    :return:
    """
    column_str = ""
    for col in columns_to_query_lst:
        column_str = column_str + col + ","
    column_str += "update"
    as_clause = "as c(" + column_str + ")"
    return  as_clause


def get_where_clause(columns_to_query_lst):
    """
    get_where_clause returns the where clause from the given query list.
    :param columns_to_query_lst: columns for where clause.
    :return:
    """
    where_str = "where "
    equals_str =[]
    for row in columns_to_query_lst:
        temp_str =  "c." + row + " = t." + row
        equals_str.append(temp_str)
    joined_str = " AND ".join(equals_str)
    where_str = where_str + joined_str
    return where_str

def get_values(column_to_query_lst, query_values_dict_lst ):
    """
    makes flat list for update values.
    :param column_to_query_lst:
    :param query_values_dict_lst:
    :return:
    """
    column_to_query_lst.append("update")
    values = []
    for dict_row in query_values_dict_lst:
        for col in column_to_query_lst:
            values.append(dict_row[col])
    return values

def make_postgres_update_multiple_statement(table,column_to_update,
                                            columns_to_query_lst,
                                            query_values_dict_lst,
                                            print_debug_log = True,
                                            typecast_suffix = ""):
    """
    It makes query statement.
    :param table: table to update.
    :param column_to_update: column name that is to be updated.
    :param columns_to_query_lst: columns name that will we used for where clause.
    :param query_values_dict_lst: list of dictionary that contains values to update.
    :param print_debug_log:
    :return:
    """
    _prefix = "UPDATE"
    table_name = table + " as t"
    keys = column_to_update + " = c.update" + typecast_suffix + " "
    from_clause = get_from_clause(query_values_dict_lst, columns_to_query_lst)
    as_clause = get_as_clause(columns_to_query_lst)
    where_clause = get_where_clause(columns_to_query_lst)
    statement = " ".join([_prefix, table_name, "SET", keys, from_clause, as_clause, where_clause])
    values = get_values(columns_to_query_lst, query_values_dict_lst)
    if print_debug_log == True:
       logging.info("Updating multiple rows into db %s"%(statement))
    return  statement ,values


def make_keys_multicol(columns_to_update_lst):
    """
        returns keys to be updated and new names of columns to be updated
        :param columns_to_update_lst:
        :return joined_str: part of postgres query with keys. E.g. "col1=c.updatecol1 , col2=c.updatecol2"
                update_lst: list of new column names in intermediate tables. E.g. [updatecol1, updatecol2]
        """
    key_equal = []
    update_lst = []
    for key in columns_to_update_lst:
        temp_str = key + " = c.update" + key
        update_lst.append("update" +key)
        key_equal.append(temp_str)
    joined_str = ",".join(key_equal)
    return joined_str, update_lst


def get_from_clause_multicol(query_values_dict_lst,columns_to_query_lst, columns_to_update_lst):
    """
        returns from clause that contains tuples of placeholders
        :param query_values_dict_lst:
        :param columns_to_update_lst:
        :param columns_to_query_lst:
        :return from_str:string. E.g "from (value (%s,%s),(%s,%s))"
        """
    from_str = "from (values "
    length = len(columns_to_query_lst)+len(columns_to_update_lst)
    placeholder_str = ["%s"] * length
    row_str = ",".join(placeholder_str)
    row_str = "(" + row_str + ")"
    num_of_dict = len(query_values_dict_lst)
    multi_row_str = [row_str]*num_of_dict
    multi_row_str = ",".join(multi_row_str)
    from_str = from_str +multi_row_str +")"
    return from_str


def get_as_clause_multicol(columns_to_query_lst, update_param_list):
    """
        get_as_clause will return tuple of column names of intermediate table c of postgresql query.
        :param columns_to_query_lst: columns for where clause.E.g [col1]
        :param update_param_list: new column names for columns to be updated.E.g [updatecol2,updatecol3]
        :return as_clause: string. E.g "as c(col1,updatecol2,updatecol3)"
        """
    column_str = []
    for col in columns_to_query_lst:
        column_str.append(col)
    for col in update_param_list:
        column_str.append(col)
    as_clause = ",".join(column_str)
    as_clause = "as c(" + as_clause +  ")"
    return as_clause

def get_values_multicol(columns_to_query_lst, columns_to_update_lst, query_values_dict_lst ):
    """
        makes flat list for update values.
        :param columns_to_query_lst:
        :param columns_to_update_lst:
        :param query_values_dict_lst:
        :return values: list of user-given values for multirow query with first params to
                query and then params to update. E.g ['col2query1','col2update1','col2query2','col2update2']
        """
    values = []
    for dict_row in query_values_dict_lst:
        for col in columns_to_query_lst:
            values.append(dict_row['where'][col])
        for col in columns_to_update_lst:
            values.append(dict_row['update'][col])
    return values


def check_parameters_multicol(columns_to_update_lst, columns_to_query_lst, query_values_dict_lst):
    """
    Checks parameters for multirow multicolumn update
    :param columns_to_update_lst: list of column names to be updated for set clause, list of strings
    :param columns_to_query_lst: list of column names to be queried for where clause, list of strings
    :param query_values_dict_lst: list of dictionaries with values for where query and update params. Has 2 items-
            update dictionary - with key='update' and value as dictionary of column name and values to be updated
            where dictionary - with key='where' and value as dictionary of column names and values to be queried
            e.g. [{'where':{'id':1}, 'update':{'col1':'ABC', 'col2':'XYZ'}}]
    :return: boolean
    """
    expected_length_query_cols = len(columns_to_query_lst)
    expected_length_target_cols = len(columns_to_update_lst)
    for dict_val in query_values_dict_lst:
        #Check length of query columns
        if len(dict_val['where'])!=expected_length_query_cols:
            logging.error("Expected %s fields in query list (where clause), instead received %s: %s" % (
            expected_length_query_cols, len(dict_val['where']), dict_val))
            return False
        #Check length of target columns
        if len(dict_val['update'])!=expected_length_target_cols:
            logging.error("Expected %s fields in update list, instead received %s: %s" % (
            expected_length_target_cols, len(dict_val['update']), dict_val))
            return False
        # check columns present in update params
        for key in dict_val['update']:
            if key not in columns_to_update_lst:
                logging.error(
                    "'%s' attribute to update isn't present in update list: %s" % (key, columns_to_update_lst))
                return False
        # check columns present in query where params
        for key in dict_val['where']:
            if key not in columns_to_query_lst:
                logging.error("'%s' attribute to query isn't present in query list: %s" % (key,columns_to_query_lst))
                return False
    return True

def make_postgres_update_multiple_column_statement(table, columns_to_update_lst, columns_to_query_lst,
                                                   query_values_dict_lst, print_debug_log = True):
    """
    Makes the postgresql statement for multiple column multiple row update
    :param table: table to update into, string
    :param columns_to_update_lst: list of column names to be updated for set clause, list of strings
    :param columns_to_query_lst: list of column names to be queried for where clause, list of strings
    :param query_values_dict_lst: list of dictionaries with values for where query and update params. Has 2 items-
            update dictionary - with key='update' and value as dictionary of column name and values to be updated
            where dictionary - with key='where' and value as dictionary of column names and values to be queried
            e.g. [{'where':{'id':1}, 'update':{'col1':'ABC', 'col2':'XYZ'}}]
    :return statement:final postgres query statement
            values: list of values given by user corresponding to placeholders in statement
    """
    _prefix = "UPDATE"
    table_name = table + " as t"
    keys, update_param_list = make_keys_multicol(columns_to_update_lst)
    from_clause = get_from_clause_multicol(query_values_dict_lst, columns_to_query_lst, columns_to_update_lst)
    as_clause = get_as_clause_multicol(columns_to_query_lst, update_param_list)
    where_clause = get_where_clause(columns_to_query_lst)
    statement = " ".join([_prefix, table_name, "SET", keys, from_clause, as_clause, where_clause])
    values = get_values_multicol(columns_to_query_lst, columns_to_update_lst, query_values_dict_lst)
    if print_debug_log == True:
        logging.info("Updating multiple rows into db: %s, %s" % (statement, values))
    return statement, values
