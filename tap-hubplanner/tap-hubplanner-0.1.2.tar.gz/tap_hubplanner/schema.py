import os
import json

SCHEMAS = None


def get_abs_path(path):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), path)


def load_schemas():
    schemas = {}

    for filename in os.listdir(get_abs_path('schemas')):
        path = get_abs_path('schemas') + '/' + filename
        file_raw = filename.replace('.json', '')
        with open(path) as file:
            schemas[file_raw] = json.load(file)

    return schemas


def get_schemas():
    global SCHEMAS

    if SCHEMAS:
        return SCHEMAS

    SCHEMAS = load_schemas()

    return SCHEMAS
