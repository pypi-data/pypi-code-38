import logging

def make_postgres_write_statement(table, kv_map, debug=True):
    _prefix = "INSERT INTO"
    keys = ",".join(list(kv_map.keys()))
    values = []
    for value in list(kv_map.values()):
      if type(value) == bool:
        if value == True:
          values.append('true')
        else:
          values.append('false')
      else:
        values.append(value)
  
    value_proxy_array = ["%s"] * len(kv_map)
    value_proxy_string = ", ".join(value_proxy_array)
    statement = " ".join([_prefix, table, "(", keys ,")", "VALUES", "(", value_proxy_string ,")"])
    if debug:
        logging.info("Writing into Db: %s, %s" % (statement, values))
    return statement, list(kv_map.values())



def get_multi_insert_str(columns_to_insert,insert_values_dict_lst):
    """
    get_multi_insert_str creates the placeholder string for multiple insertion values.
    :param columns_to_insert:
    :param insert_values_dict_lst:
    :return:
    """
    dict_lst= []
    placeholder_str = ["%s"]*len(columns_to_insert)
    row_str = ",".join(placeholder_str)
    row_str = "("+row_str+")"
    row = [row_str]
    multi_row_str_lst = row*len(insert_values_dict_lst)
    multi_row_str = ",".join(multi_row_str_lst)
    return multi_row_str

def get_multi_values(columns_to_insert,insert_values_dict_lst):
    """
    returns the values for the placeholders in query.
    :param columns_to_insert:
    :param insert_values_dict_lst:
    :return:
    """
    values = []
    for value_dict in insert_values_dict_lst:
        for col in columns_to_insert:
            value = value_dict[col]
            values.append(value)
    return  values


def make_postgres_write_multiple_statement(table, columns_to_insert_lst, insert_values_dict_lst, print_debug_log=True):
    """
    make_postgres_write_multiple_statement generates the posgresql query.

    :param table:
    :param columns_to_insert_lst:
    :param insert_values_dict_lst:
    :param print_debug_log:
    :return:
    """
    prefix = "INSERT INTO"
    TABLE_NAME = table
    columns_str = "("+",".join(columns_to_insert_lst) + ")"
    values_placeholder = get_multi_insert_str(columns_to_insert_lst, insert_values_dict_lst)
    values = get_multi_values(columns_to_insert_lst,insert_values_dict_lst)
    statement = " ".join([prefix, TABLE_NAME, columns_str, "VALUES", values_placeholder])
    return statement,values

