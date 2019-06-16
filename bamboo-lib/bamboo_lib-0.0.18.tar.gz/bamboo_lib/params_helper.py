from bamboo_lib.connectors.models import Connector


def find_param(pipeline_params, key):
    candidates = [x for x in pipeline_params if x.name == key]
    return candidates[0] if candidates else None


def extract(pipeline_params, raw_params):
    '''Given raw form data, coerece parameters to their appropriate types'''
    new_result = {}
    dtype_lookup = {p.name: p.dtype for p in pipeline_params}
    for key, value in raw_params:
        raw_value = dtype_lookup[key]
        # raise Exception(pipeline_params, key )
        param_obj = find_param(pipeline_params, key)
        if param_obj.dtype is Connector:
            value = Connector.fetch(None, value)
        else:
            value = raw_value(value)
        if key not in new_result:
            res = value
        elif isinstance(raw_params[key], list):
            res = raw_params[key] + [value]
        else:
            res = [raw_params[key]] + [value]
        new_result[key] = res
    return new_result
