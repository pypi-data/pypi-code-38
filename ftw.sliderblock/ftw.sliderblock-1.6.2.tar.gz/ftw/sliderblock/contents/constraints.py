import json


def validate_slick_config(value):
    try:
        json.loads(value)
    except ValueError:
        return False

    return True
