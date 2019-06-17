"""
default rules
"""

def required(label, field, data, **kwargs):
    """Validates presence value.
    - when bool, return True
    - when None, return False,
    - when inexistent key, return False
    """
    if not field in data:
        return False

    value = data[field]

    if value == None:
        return False
    elif type(value) is bool:
        return True
    elif not value:
        return False

    return True
