import uuid
import shlex
import ujson as json
import datetime
import random
import rethinkdb as r
from networktools.colorprint import gprint, bprint, rprint
from itertools import product


def all_variants(word):
    word_set = {''.join(x) for x in product(
        *[{c.upper(), c.lower()} for c in word])}
    return word_set


def random_char():
    """
    Alphabetic uppercase and number 0 to 9 on a random
    selection
    """
    #symbols = list(range(91,96))+ list(range(123,126))
    nums = list(range(48, 58))
    alfab = list(range(65, 91))
    chars = nums + alfab
    char_num = random.choice(chars)
    return chr(char_num)


def my_random_string(string_length=10):
    """Returns a random string of length string_length.

    :param string_length: a positive int value to define the random length
    :return:
    """
    a = 3
    assert string_length >= a, "No es un valor positivo sobre " + str(a)
    rand_list = [random_char() for i in range(string_length)]
    random = "".join(rand_list)
    return random


def complete_nro(val, character='0', n=3):
    """
    Complete with 0 a number until n chars
    """
    s_val = str(val).upper()
    ln = len(s_val)
    delta = n - ln
    s_out = ''
    for k in range(delta):
        s_out += character
    s_out += s_val
    return s_out


def hextring(value: int) -> str:
    """
    Parse a int to hexadecimal and transfor to string without x part
    """
    return str(hex(value)).split('x')[1]


def hextring2int(value: str):
    """
    The inverse as before, parse a string that is hexadecimal, to int

    """
    return int("0x" + value, 16)


def check_type(value, tipo='boolean'):
    """
    Check if some value is on trues or falses, so
    if the value is in a set, give us the correct boolean

    """
    trues = {'true', 't', 'T',
             'True', 'verdadero',
             '1', 's', 'S', 'Si', 'si', 1, True}
    falses = {'falso', 'false', 'False',
              'f', '0', 'n', 'N', 'No', 'no', '', 0, False, None}
    if tipo == 'int':
        value = int(value)
    elif tipo == 'boolean':
        if value in trues:
            value = True
        elif value in falses:
            value = False
        else:
            value = False
    elif tipo in {'double', 'float', 'real'}:
        value = float(value)
    return value


def reverse_dict(commands):
    reverse_commands = {give_name(value): key
                        for key, value in commands.items()}
    return reverse_commands


def choice_input(choices_dict,
                 type_opt_lambda=lambda x: True,
                 xprint=print):
    """
    For command line, you give a dictionary with options and ask to you what of these options you
    need to run, so you can write the keys or the values

    """
    commands = choices_dict
    reverse_commands = reverse_dict(commands)
    options = ["%s -> %s" % (key, give_name(value))
               for key, value in commands.items()]
    key = ""
    msg_type = type_opt_lambda(None)
    option_nr = 0
    while key not in commands:
        [xprint(option) for option in options]
        option = ''
        try:
            option = input("Choose an option: \n")
        except EOFError as error:
            raise error
        command, key, option_nr = get_command(
            commands,
            reverse_commands,
            option)
    msg_type = type_opt_lambda(option_nr)
    return command, option, msg_type


def choice_action(choices_dict,
                  choice,
                  type_opt_lambda=lambda x: True,
                  xprint=print):
    """
    For command line, you give a dictionary with options and ask to you what of these options you
    need to run, so you can write the keys or the values

    """
    option = choice
    print("Choice ib choice_action-->", choice)
    commands = choices_dict
    reverse_commands = reverse_dict(commands)
    options = ["%s -> %s" % (key, give_name(value))
               for key, value in commands.items()]
    key = ""
    msg_type = type_opt_lambda(None)
    option_nr = 0
    command, key, option_nr = get_command(
        commands,
        reverse_commands,
        option)
    print("Select result::: command, key, option_nr")
    print(command, key, option_nr)
    msg_type = type_opt_lambda(option_nr)
    return command, option, msg_type


def get_command(commands, reverse_commands, option):
    """
    Obtain a command from a dict of commands

    """
    option_nr = 0
    if not option:
        option = ""
    if option.isdigit():
        option = int(option)
        if option in commands:
            command = commands.get(option)
            option_nr = option
        else:
            command = 'PRINT'
            option_nr = option
    else:
        # command is the value
        result_k, key, command = multikey(commands, option)
        result_v = False
        if result_k:
            option = key
        else:
            # command is the key
            result_v, key = multivalue(
                reverse_commands, option)
            command = commands.get(key)
            if result_v:
                option = key
        if result_k or result_v:
            option_nr = reverse_commands.get(command)
    return command, option, option_nr


def multikey(commands, key):
    """
    Given an string key, look for the value in commands, if key
    has upper or lower case, consider that.
    """
    result = False
    final_key = key
    command = None
    if key in commands:
        command = commands.get(key)
        result = True
    elif key.lower() in commands:
        final_key = key.lower()
        command = commands.get(final_key)
        result = True
    elif key.upper() in commands:
        final_key = key.upper()
        command = commands.get(final_key)
        result = True
    # here command is the value of the key
    return result, final_key, command


def multivalue(reverse_commands, value):
    """
    Given an string value, look for the key in commands, if value
    has upper or lower case, consider that.
    """
    result = False
    final_value = value
    key = None
    if value in reverse_commands:
        key = reverse_commands.get(value)
        result = True
    elif value.lower() in reverse_commands:
        final_value = value.lower()
        key = reverse_commands.get(final_value)
        result = True
    elif value.upper() in reverse_commands:
        final_value = value.upper()
        key = reverse_commands.get(final_value)
        result = True
    # here command is the key
    return result, key


def give_name(value):
    """
    Give the name of the object, if is callable (funcion, generator, coroutine, etc) returns name, else
    the string method on the object

    """
    if callable(value):
        return value.__name__
    else:
        return str(value)


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


def key_on_dict(key, mydict):
    """
    Check if key on dict, is old because a dict has .get method
    """
    if key in mydict:
        if mydict[key]:
            return True
        else:
            return False
    else:
        return False


def check_gsof(mydict):
    return key_on_dict('ECEF', mydict) and key_on_dict('POSITION_VCV', mydict)


def gns_dumps(string, char='#'):
    a = json.dumps(string)
    b = a.replace('\"', char)
    q = 3*char
    c = b.replace('\\#', '$%s' % q)
    return c


def gns_loads(string, char='#'):
    q = 3*char
    a = string.replace('$%s' % q, '\\#')
    b = a.replace(char, '\"')
    c = json.loads(b)
    return c


def context_split(value, separator='|'):
    """
    Split and take care of \"\"
    """
    try:
        q = shlex.shlex(value, posix=True)
        q.whitespace += separator
        q.whitespace_split = True
        q.quotes = '\"'
        q_list = list(q)
        return q_list
    except Exception as e:
        print("Error en separación de contexto %s" % e)
        raise e


def geojson2angularjson(content):
    """
    content is a GeoJson object must be converted to a Angular Chart JSON object....
    """

    dt = datetime.utcfromtimestamp(int(content['properties']['time'])/1000)
    new_value = dict(
        source="DataWork",
        station_name=content['properties']['station'],
        timestamp=dt,
        data={
            'N': {
                'value': content['features'][0]['geometry']['coordinates'][0],
                'error': content['properties']['NError'],
                'min': content['features'][0]['geometry']['coordinates'][0]-content['properties']['NError'],
                'max': content['features'][0]['geometry']['coordinates'][0]+content['properties']['NError']
            },
            'E': {
                'value': content['features'][0]['geometry']['coordinates'][1],
                'error': content['properties']['EError'],
                'min': content['features'][0]['geometry']['coordinates'][1]-content['properties']['EError'],
                'max': content['features'][0]['geometry']['coordinates'][1]+content['properties']['EError']

            },
            'U': {
                'value': content['features'][0]['geometry']['coordinates'][2],
                'error': content['properties']['UError'],
                'min': content['features'][0]['geometry']['coordinates'][2]-content['properties']['UError'],
                'max': content['features'][0]['geometry']['coordinates'][2]+content['properties']['UError']
            },
        }
        # last_update=datetime.utcnow()
    )

    return new_value


def geojson2rethinkjson(content):
    """
    content is a GeoJson object must be converted to a RethinkDB JSON object....
    """

    try:
        # print("Content...:%s"%content['properties'])
        time = content['properties']['time']
        dt0 = content['properties']['dt']
        #print("Datetime Original %s" %dt0)
        c_datetime = dt0.isoformat()
        #print("Fecha y tiempo %s" %dt0.isoformat())
        dt = r.iso8601(dt0.isoformat())
        dt_gen = content['properties']['DT_GEN']
    except Exception as exec:
        print("Error en calcular fecha tiempo %s" % exec)
        raise exec
    new_value = dict(
        source="DataWork",
        station_name=content['properties']['station'],
        DT_GEN=dt_gen,
        timestamp=time,
        data={
            'N': {
                'value': content['features'][0]['geometry']['coordinates'][0],
                'error': content['properties']['NError'],
                'min': content['features'][0]['geometry']['coordinates'][0]-content['properties']['NError'],
                'max': content['features'][0]['geometry']['coordinates'][0]+content['properties']['NError']
            },
            'E': {
                'value': content['features'][0]['geometry']['coordinates'][1],
                'error': content['properties']['EError'],
                'min': content['features'][0]['geometry']['coordinates'][1]-content['properties']['EError'],
                'max': content['features'][0]['geometry']['coordinates'][1]+content['properties']['EError']

            },
            'U': {
                'value': content['features'][0]['geometry']['coordinates'][2],
                'error': content['properties']['UError'],
                'min': content['features'][0]['geometry']['coordinates'][2]-content['properties']['UError'],
                'max': content['features'][0]['geometry']['coordinates'][2]+content['properties']['UError']
            },
        }
        # last_update=datetime.utcnow()
    )

    return new_value


def geojson2json(content, destiny="plot"):
    """
    content is a GeoJson object must be converted to a RethinkDB JSON object....
    """

    try:
        # print("Content...:%s"%content['properties'])
        time = content['properties']['time']
        dt0 = content['properties']['dt']
        #print("Datetime Original %s" %dt0)
        c_datetime = dt0.isoformat()
        #print("Fecha y tiempo %s" %dt0.isoformat())
        dt = dt0.isoformat()
        if destiny == 'plot':
            dt_gen = content['properties']['DT_GEN'].isoformat()
        else:
            dt_gen = content['properties']['DT_GEN']
    except Exception as exec:
        print("Error en calcular fecha tiempo %s" % exec)
        raise exec
    new_value = dict(
        source="DataWork",
        station_name=content['properties']['station'],
        DT_GEN=dt_gen,
        timestamp=time,
        data={
            'N': {
                'value': content['features'][0]['geometry']['coordinates'][0],
                'error': content['properties']['NError'],
                'min': content['features'][0]['geometry']['coordinates'][0]-content['properties']['NError'],
                'max': content['features'][0]['geometry']['coordinates'][0]+content['properties']['NError']
            },
            'E': {
                'value': content['features'][0]['geometry']['coordinates'][1],
                'error': content['properties']['EError'],
                'min': content['features'][0]['geometry']['coordinates'][1]-content['properties']['EError'],
                'max': content['features'][0]['geometry']['coordinates'][1]+content['properties']['EError']

            },
            'U': {
                'value': content['features'][0]['geometry']['coordinates'][2],
                'error': content['properties']['UError'],
                'min': content['features'][0]['geometry']['coordinates'][2]-content['properties']['UError'],
                'max': content['features'][0]['geometry']['coordinates'][2]+content['properties']['UError']
            },
        }
        # last_update=datetime.utcnow()
    )

    return new_value
