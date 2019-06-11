import uuid
import shlex
import json


def my_random_string(string_length=10):
    """Returns a random string of length string_length.

    :param string_length: a positive int value to define the random length
    :return:
    """
    a = 3
    assert string_length >= a, "No es un valor positivo sobre " + str(a)
    random = str(uuid.uuid4())  # Convert UUID format to a Python string.
    random = random.upper()  # Make all characters uppercase.
    random = random.replace("-", "")  # Remove the UUID '-'.
    return random[0:string_length]  # Return the random string.
# str(my_random_string(6))
# print(my_random_string(6)) # For example, D9E50C


def fill_pattern(var_list, pattern):
    """
    Replace values in pattern
    var_list has to have 'pattern' and 'value' keys
    pattern is a string with some keys inside
    """
    code = pattern
    for lista in var_list:
        keys = lista.keys()
        # print(lista)
        assert 'pattern' in keys and 'value' \
            in keys, "Lista incorrecta en " + str(lista)
        code = code.replace(lista['pattern'], lista['value'])
    # print(code)
    return code


def pattern_value(pattern_str, val):
    "Return a specific dictionary with keys pattern and value"
    return dict(pattern=pattern_str, value=val)


def gns_dumps(string, char='#'):
    a = json.dumps(string)
    b = a.replace('\"', char)
    return b


def gns_loads(string, char='#'):
    a = string.replace(char, '\"')
    b = json.loads(a)
    return b


def context_split(value, separator='|'):
    """
    Split and take care of \"\"
    """
    q = shlex.shlex(value, posix=True)
    q.whitespace += separator
    q.whitespace_split = True
    q.quotes = '\"'
    q_list = list(q)
    return q_list
