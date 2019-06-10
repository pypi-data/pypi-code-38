def clone(model):
    new_kwargs = dict(
        [(fld.name, getattr(model, fld.name)) for fld in model._meta.fields if fld.name != model._meta.pk])

    return model.__class__(**new_kwargs)


def get_field(clazz, name):
    for field in clazz._meta.fields:
        if field.name == name:
            return field

    return None


def set_attrs(object, map):
    for key, value in map.items():
        setattr(object, key, value)

    return object


def get_choice_label(choices, choice):
    for entry in choices:

        if entry[0] == choice:
            return entry[1]

    return ""


def get_choice_id(tuples, str_value):
    if str_value:
        s = str_value.lower()
        for t in tuples:
            if t[1].lower() == s:
                return t[0]
    return None
