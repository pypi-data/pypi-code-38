import logging


def make_postgres_read_statement(table, kv_map, keys_to_get, limit, order_by,
                                 order_type, debug, clause, group_by, join_clause):
    _prefix = "SELECT"
    _join_by = " " + join_clause + " "
    _table_string = " ".join(["FROM", table])
    _key_string = _join_by.join([k + clause + "%s" for k in list(kv_map.keys())])
    values = list(kv_map.values())

    if clause.strip().lower() == "in":
        values = []
        _key_string = _join_by.join([k + clause + "(" + ",".join("'" + x + "'" for x in kv_map[k]) + ")" for k in list(kv_map.keys())])

    statement = " ".join([_prefix, ", ".join(sorted(keys_to_get)), _table_string])
    if len(list(kv_map.keys())) > 0:
      statement = " ".join([_prefix, ", ".join(sorted(keys_to_get)), _table_string, "WHERE", _key_string])
    if group_by is not None:
        statement += " GROUP BY " + group_by
    if order_by is not None:
        statement += " ORDER BY " + order_by + " " + order_type
    if limit is not None:
        statement += " LIMIT " + str(limit)
    if debug:
        logging.info("Reading From Db: %s, %s" %(statement, list(kv_map.values())))
    return statement, values

def prepare_values(all_values, keys_to_get):
    ret_val = []
    if all_values is None:
        return None
    k = sorted(keys_to_get)
    for row in all_values:
        row_kv = {}
        if len(row) == len(keys_to_get):
            for idx in range(0, len(row)):
                row_kv[k[idx]] = str(row[idx])
        else:
            logging.error("Number of keys to be fetched are not correct")
            continue
        ret_val.append(row_kv)
    return ret_val

