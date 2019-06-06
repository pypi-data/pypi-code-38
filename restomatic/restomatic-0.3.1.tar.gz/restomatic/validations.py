
def type_pos_int(value):
    value = int(value)
    if value <= 0:
        raise ValueError('Provided value must be a positive integer (not zero)')
    return value


def type_non_neg_int(value):
    value = int(value)
    if value < 0:
        raise ValueError('Provided value must be a non-negative integer')
    return value


def cast_expect_type(value, cast_type, error_msg_name):
    try:
        return cast_type(value)
    except (ValueError, TypeError):
        raise TypeError(f'Expected type of {cast_type.__name__} for {error_msg_name}')


def expect_type(value, types, error_msg_name):
    if not isinstance(value, types):
        raise TypeError(f'Expected {error_msg_name} to be type of {types}')


def expect_in(value, valid_values, error_msg_name):
    if value not in valid_values:
        raise ValueError(f'Expected {error_msg_name} to be one of {valid_values}')


def expect_len(value, expected_len, error_msg_name):
    if len(value) != expected_len:
        raise ValueError(f'Expected {error_msg_name} to have length of {expected_len}')


def expect_len_range(value, min_len, max_len, error_msg_name):
    actual_len = len(value)
    if actual_len < min_len or actual_len > max_len:
        raise ValueError(f'Expected {error_msg_name} to have length of {min_len} to {max_len}')


def expect_only_one_of(values, error_msg_names):
    found = False
    for v in values:
        if v is not None:
            if found:
                raise ValueError('Expected only one of (' + ','.join(error_msg_names) + ') to be set')
            found = True

    if not found:
        raise ValueError('Must set one of (' + ','.join(error_msg_names) + ')')


def set_dict_data_only_once(dictionary, keys, value, error_msg):
    final_key = keys.pop()
    for key in keys:
        if key not in dictionary:
            dictionary[key] = {}
        dictionary = dictionary[key]

    if final_key in dictionary and dictionary[final_key]:
        raise ValueError(f'Multiple definitions given for {error_msg}')

    dictionary[final_key] = value
