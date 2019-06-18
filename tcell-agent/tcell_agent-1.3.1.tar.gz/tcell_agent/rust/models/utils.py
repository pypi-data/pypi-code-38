from future.utils import iteritems
from tcell_agent.converters.params import flatten_clean
from tcell_agent.utils.strings import ensure_str_or_unicode


# deprecated
def convert_params(encoding, params_dict, need_to_flatten=True):
    if params_dict is None:
        return []

    flattened_dict = params_dict
    if need_to_flatten:
        flattened_dict = flatten_clean(encoding, params_dict)

    flattened_params = []
    for param_name, param_value in iteritems(flattened_dict):
        flattened_params.append({"name": param_name[-1], "value": param_value})

    return flattened_params


def convert_single_dict_params(params_dict, value_size_limit, encoding=None):
    name_value_list = []
    if not params_dict:
        return name_value_list
    for name in params_dict.keys():
        value = ensure_str_or_unicode(encoding, params_dict[name])
        value = (value[:value_size_limit] + '..') if len(value) > value_size_limit else value
        name = ensure_str_or_unicode(encoding, name)
        name_value_list.append({"name": name, "value": value})
    return name_value_list


def convert_multidict_params(multi_dict, encoding=None):
    return convert_multidict_params_append(multi_dict, encoding, [])


def convert_multidict_params_append(multi_dict, encoding, extracted_params):
    if not multi_dict:
        return extracted_params
    # keys() + getlist(key) is faster using multi_dict.lists().  See benchmarks
    for name in multi_dict.keys():
        value_list = multi_dict.getlist(name)
        name = ensure_str_or_unicode(encoding, name)
        for value in value_list:
            value = ensure_str_or_unicode(encoding, value)
            extracted_params.append({"name": name, "value": value})
    return extracted_params


def convert_post_params(post_multi_dict, files_multi_dict, encoding=None):
    post_params_list = convert_multidict_params(post_multi_dict, encoding)
    combined = convert_multidict_params_append(files_multi_dict, encoding, post_params_list)
    return combined
