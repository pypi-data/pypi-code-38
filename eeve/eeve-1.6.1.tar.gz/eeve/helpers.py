def strip_split(s, *args, **kwargs):
    return list(map(lambda x: x.strip(), s.split(*args, **kwargs)))


def try_cast(tp, obj):
    try:
        tp(obj)
        return True
    except:
        return False


def get_true_value(x):
    if try_cast(int, x):
        return int(x)
    elif try_cast(float, x):
        return float(x)
    elif x.lower() == 'true':
        return True
    elif x.lower() == 'false':
        return False
    else:
        return x


def split_args(arg_string, return_args, return_kwargs):
    args = strip_split(arg_string, mappings.char_map[','])
    for arg in args:
        if mappings.char_map['='] in arg:
            k, v = strip_split(arg, mappings.char_map['='], maxsplit=1)
            return_kwargs[k] = get_true_value(v)
        else:
            return_args.append(get_true_value(arg))


import eeve.mappings as mappings


def process_args(command_string, return_init_args):
    init_args, run_args = [], []
    init_kwargs, run_kwargs = {}, {}
    if mappings.char_map[':'] in command_string:
        command_name, temp_args = strip_split(command_string, mappings.char_map[':'], maxsplit=1)

        arg_split = strip_split(temp_args, mappings.char_map['|'], maxsplit=1)
        if len(arg_split) == 1:
            temp_init_args = None
            temp_run_args = arg_split[0]
        else:
            temp_init_args, temp_run_args = arg_split

        if temp_init_args:
            split_args(temp_init_args, init_args, init_kwargs)

        split_args(temp_run_args, run_args, run_kwargs)

    else:
        command_name = command_string

    if return_init_args:
        return command_name, init_args, init_kwargs, run_args, run_kwargs
    else:
        return command_name, run_args, run_kwargs