from hashids import Hashids


def hashid(*values, decode=False, min_length=7):
    hash_class = Hashids(min_length=min_length)
    # decode a dictionary
    if type(values[0]) == dict and decode:
        new_dict = {}
        for key, value in values[0].items():
            if value and hash_class.decode(value):
                value = hash_class.decode(value)
            if type(value) == tuple:
                value = value[0]
            new_dict.update({key: value})
        return new_dict

    if not decode:
        return hash_class.encode(*values)

    return Hashids().decode(*values)
