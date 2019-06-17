def flatten(d):
    out = {}
    if isinstance(d, str):
        return d

    for key, val in d.items():
        if isinstance(val, dict):
            val = [val]
        if isinstance(val, list):
            if len(val) == 1:
                for subdict in val:
                    if isinstance(subdict, (dict)):
                        deeper = flatten(subdict).items()
                        out.update({key + '.' + key2: val2 for key2, val2 in deeper})
                    else:
                        out.update({key + '.0': val[0]})
            else:
                for list_key, subdict in enumerate(val):
                    if isinstance(subdict, (dict)):
                        deeper = flatten(subdict).items()
                        out.update({key + '.' + str(list_key) + '.' + key2: val2 for key2, val2 in deeper})
                    else:
                        out.update({key + '.' + str(list_key): subdict})
        else:
            out[key] = val
    return out


def to_csv(dics, filename, keys=None):
    """
    Create a CSV from a dictionary list
    :param dics: dictionary list
    :param filename: output filename
    :param keys: Optional, subset of keys. Default is all keys.
    :return: None
    """
    if isinstance(dics, dict):
        dics = [dics]

    if isinstance(dics, set):
        dics = list(dics)

    if isinstance(dics[0], dict):
        dics = [flatten(dic) for dic in dics]

        if not keys:
            keys = sorted(set().union(*(d.keys() for d in dics)))
    
        import csv
        with open(filename, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(dics)

    # Caso uma lista seja passada
    else:
        with open(filename, 'w') as output_file:
            output_file.write('\n'.join([str(d) for d in dics]))


def datetime_to_unix_miliseconds_epoch(dt):
    """
    The number of milliseconds after Jan 1, 1970 00:00:00 UTC
    """
    import time
    return time.mktime(dt.timetuple()) * 1e3 + dt.microsecond / 1e3


def to_unix_epoch(dic):
    from datetime import datetime
    from dateutil import parser
    for key in dic:
        if not isinstance(dic[key], (int, datetime)):
            try:
                dic[key] = parser.parse(dic[key])
            except ValueError:
                pass
        if isinstance(dic[key], datetime):
            dic[key] = int(
                datetime_to_unix_miliseconds_epoch(dic[key])
            )
    return dic


def path(full_path, obj):
    """
    Get value from obj following a path
    :param full_path:
    :param obj:
    :return:
    """
    if full_path == '':
        return obj

    if '.' in full_path:
        data = obj
        nodes = full_path.split('.')
        data_list = []
        for node in nodes:
            if node in data:
                data = data[node]
            else:
                return None

            if isinstance(data, list):
                for d in data:
                    data_list += [path(full_path.split(node)[1][1:], d)]
                break
        if len(data_list):
            return data_list
        return data

    else:
        if full_path in obj:
            return obj[full_path]
        else:
            return None


def unpack(obj):
    """
    Unpack while obj isn't a obj
    """

    if isinstance(obj, list) and not isinstance(obj, str):
        if len(obj) == 1:
            return obj[0]
        else:
            new = []
            for i in obj:
                new += [unpack(i)]
            return new
    return obj


def flat(objs):
    ret = []

    # Teste de sanidade: Se é um único item
    if isinstance(objs, dict) or isinstance(objs, str):
        return objs

    for i in objs:
        if isinstance(i, list):
            ret += i
        else:
            ret += [i]
    return ret


def field_comparison(value, expression):
    if value == expression:
        return True

    import re
    try:
        return re.match('^' + expression + '$', value)
    except TypeError as e:
        return False
