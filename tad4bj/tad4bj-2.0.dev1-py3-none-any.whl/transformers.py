import sqlite3
import json
try:
    import cPickle as pickle
except ImportError:
    import pickle

try:
    import yaml
except ImportError:
    yaml = None


def convert_yaml(s):
    if yaml is None:
        raise ImportError("No YAML library available, YAML is unsupported")
    return yaml.load(s)


def yaml_adapter(obj):
    if yaml is None:
        raise ImportError("No YAML library available, YAML is unsupported")
    return yaml.dump(obj)


def convert_json(s):
    return json.load(s)


def json_adapter(obj):
    return json.dumps(obj)


def convert_pickle(s):
    return pickle.loads(s)


def pickle_adapter(obj):
    return pickle.dumps(obj)


def identity_adapter(obj):
    return obj


def register_converters():
    sqlite3.register_converter("yaml", convert_yaml)
    sqlite3.register_converter("json", convert_json)
    sqlite3.register_converter("pickle", convert_pickle)


DECLTYPE_ADAPTERS = {
    "yaml": yaml_adapter,
    "json": json_adapter,
    "pickle": pickle_adapter,
}
