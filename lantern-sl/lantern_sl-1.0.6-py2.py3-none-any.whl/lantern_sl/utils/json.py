import decimal

def _transform_node(node_data, format_from, format_to):
    """ Helper to transform node elements from one format to another, recursive """
    if type(node_data) == str:
        return node_data
    if type(node_data) == format_from:
        node_data = round(format_to(node_data), 9) # 9 decimals always
    if type(node_data) == dict:
        for key in node_data.keys():
            if type(node_data[key]) == format_from:
                node_data[key] = round(format_to(node_data[key]), 9) # 9 decimals always
            elif type(node_data[key]) == dict or type(node_data[key]) == list:
                node_data[key] = _transform_data_types(
                    node_data[key], format_from, format_to)
    return node_data


def _transform_data_types(data, format_from, format_to):
    """ Helper for transforming data type """
    if type(data) == list:
        data_total = []
        for ele in data:
            if type(ele) == list:
                data_total.append(_transform_data_types(ele, format_from, format_to))
            else:
                data_total.append(_transform_node(ele, format_from, format_to))
    else:
        data_total = _transform_node(data, format_from, format_to)
    return data_total


def json_decimal_to_float(data):
    """ convert all decimal.Decimal numbers in the json root to float
    """
    return _transform_data_types(data, format_from=decimal.Decimal, format_to=float)


def json_float_to_decimal(data):
    """ convert all float numbers in the json root to decimal.Decimal
    """
    return _transform_data_types(data, format_from=float, format_to=decimal.Decimal)
