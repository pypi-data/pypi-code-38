import json


def json_to_obj(json_data, class_type):
    ct = class_type()
    j = json.loads(json_data)
    for i in dir(ct):
        if not i.startswith("__"):
            setattr(ct, i, j[i] if i in j else None)
    return ct


def obj_to_json(obj):
    json_obj = json.dumps(obj, default=lambda x: x.__dict__)
    return json_obj
