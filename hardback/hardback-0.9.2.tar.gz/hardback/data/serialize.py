import attr


def unserialize(data, output):
    """Unserialize from JSON-like data (dicts, strings, etc) to a dataclass"""
    try:
        fields = attr.fields_dict(output.__class__)
    except Exception:
        try:
            return type(output)(data)
        except Exception:
            return data

    unknown = set(data) - set(fields)
    if unknown:
        raise ValueError('Do not understand fields:', *unknown)

    for k, v in data.items():
        subitem = getattr(output, k)
        setattr(output, k, unserialize(v, subitem))

    return output


def serialize(item):
    """Serialize from a dataclass to JSON-like data"""
    return attr.asdict(item)
