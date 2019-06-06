from lantern_sl.utils.json import json_decimal_to_float, json_float_to_decimal

SYSTEM_COLUMNS = ["username", "app_id", "lantern_desc"]

STATUS_OK = "OK"
STATUS_ERROR = "Error"

def fn_cleanup_system_cols(data):
    """ Remove System columns from all returned objects
    """
    is_list = True if isinstance(data, list) else False
    data_total = data if is_list else [data]
    for record in data_total:
        for col in SYSTEM_COLUMNS:
            if col in record:
                del record[col]
    return data_total if is_list else data_total[0]


def http_response(data, count=None, next=None, cleanup_system_cols=True, convert_json_decimal_to_float=True):
    """ Format a return a valid JSON
    
    Arguments:
        data {json} -- Json to be returned
    
    Keyword Arguments:
        cleanup_system_cols {int} -- if True, cleanp system columns
        convert_json_decimal_to_float {json} -- if True, convert data json decimal to float
    """
    tot_data = json_decimal_to_float(data) if convert_json_decimal_to_float else data
    tot_data = fn_cleanup_system_cols(tot_data) if cleanup_system_cols else tot_data
    
    # TODO: if count and next are defined, return next after data (url for fetching next values)
    
    data_json = {
        "status": STATUS_OK,
        "data": tot_data
    }
    return data_json


def http_error(message, detail, e=None, raise_error=False):
    """ return a standard json response for errors """
    data = {
        "status": STATUS_ERROR,
        "message": message,
        "detail": detail,
    }
    if e:
        data["raw"] = str(e)
    
    if raise_error:
        raise Exception(data)
    else:
        return data


def res_ok(res):
    return True if "status" in res and res["status"] == STATUS_OK else False

def res_failed(res):
    return True if "status" in res and res["status"] == STATUS_ERROR else False