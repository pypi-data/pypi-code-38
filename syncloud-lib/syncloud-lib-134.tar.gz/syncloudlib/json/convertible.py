import jsonpickle
import os
import datetime
import inspect

jsonpickle.set_preferred_backend('json')

def pretty_print():
    jsonpickle.set_encoder_options('json', indent=2)

def ugly_print():
    jsonpickle.set_encoder_options('json', indent=None)

class List:
    def __init__(self, item_type):
        self.item_type = item_type

class Field:
    def __init__(self, field_type=None, default=None):
        self.field_type = field_type
        self.default = default

class Struct(object):
    def __init__(self, adict):
        self.__dict__.update(adict)
        for k, v in adict.items():
            if isinstance(v, (dict, list)):
                self.__dict__[k] = to_object(v)


def get_field_value(field, field_meta, structure):
    if field in structure.keys():
        value = structure[field]
        if field_meta.field_type:
            return to_object(value, field_meta.field_type)
        return value
    else:
        if field_meta.default is not None:
            return field_meta.default
    return None


def to_object(structure, obj_type=None):
    if obj_type:
        if isinstance(obj_type, List):
            return [to_object(item, obj_type.item_type) for item in structure]
        else:
            obj = obj_type()
            for field, field_meta in inspect.getmembers(obj):
                if isinstance(field_meta, Field):
                    value = get_field_value(field, field_meta, structure)
                    setattr(obj, field, value)
            return obj
    else:
        if structure is None or isinstance(structure, (bool, basestring, str, unicode, int, long, float, datetime.datetime)):
            return structure
        if isinstance(structure, list):
            return [to_object(item) for item in structure]
        return Struct(structure)

def limit(dictionary, keys):
    filtered = [key for key in dictionary.keys() if key not in keys]
    for key in filtered:
        dictionary.pop(key, None)

def to_dict(value):
    if isinstance(value, list):
        return [to_dict(item) for item in value]
    if isinstance(value, dict):
        cloned = value.copy()
        for key, value in cloned.items():
            cloned[key] = to_dict(value)
        return cloned
    if value is None or isinstance(value, (bool, basestring, str, unicode, int, long, float, datetime.datetime)):
        return value
    result = value.__dict__.copy()
    if hasattr(value, '__public__'):
        limit(result, value.__public__)
    for member, mvalue in result.items():
        result[member] = to_dict(mvalue)
    return result

def from_json(json_text, obj_type=None):
    return to_object(jsonpickle.decode(json_text), obj_type)

def to_json(value):
    return jsonpickle.encode(value, unpicklable=False)

def reformat(json_text):
    return to_json(from_json(json_text))

def read_json(filename, obj_type=None):
    if not os.path.isfile(filename):
        return None
    with open(filename, 'r') as f:
        json = f.read()
    if json.strip(' \t\n\r') == '':
        return None
    return from_json(json, obj_type)

def write_json(filename, obj):
    if not obj:
        json = ''
    else:
        json = to_json(obj)
    with open(filename, 'w') as file:
        file.write(json)
