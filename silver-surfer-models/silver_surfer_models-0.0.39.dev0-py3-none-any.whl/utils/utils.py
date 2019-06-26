import json
import pytz
from datetime import datetime
from marshmallow import ValidationError
from sqlalchemy.sql.expression import ClauseElement


# converts sql row to dict
def build_object(row):
    d = {}
    if row is None:
        return d

    for column in row.__table__.columns:
        # TODO: Need try-except for python2.7 inside docker container
        # After figuring out venv inside docker, relative imports
        # remove this hack
        try:
            a = str(getattr(row, column.name))
        except UnicodeEncodeError:
            a = getattr(row, column.name).encode('utf-8')
        d[column.name] = a

    return d


# converts sql rows to list of dicts
def build_objects(rows):
    return [build_object(row) for row in rows]


# helper for PATCH
def update_model(resource, model):
    for k, v in resource.items():
        model.__setattr__(k, v)


def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        params = dict((k, v) for k, v in kwargs.items() if
                      not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)
        return instance, True


# converts returned data to json; used in tests
def to_json(data):
    return json.loads(data.data.decode('utf8'))


def validate_data(schema, params):
    errors = schema.validate(data=params)
    if errors:
        raise ValidationError(errors)


def convert_to_boolean(value):
    """
    >>> convert_to_boolean(True)
    True
    >>> convert_to_boolean('True')
    True
    >>> convert_to_boolean('true')
    True
    >>> convert_to_boolean('1')
    True
    >>> convert_to_boolean(1)
    True
    >>> convert_to_boolean('False')
    False
    """
    truthy = {'t', 'T', 'true', 'True', 'TRUE', '1', 1, True}
    falsy = {'f', 'F', 'false', 'False', 'FALSE', '0', 0, 0.0, False}
    if value is None:
        return None
    elif value in truthy:
        return True
    elif value in falsy:
        return False

    return bool(value)


def get_time_india():
    tz = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(tz)
    return current_time


def localize_time(t):
    """
    >>> x = datetime(2017, 5, 16)
    >>> localize_time(x)
    datetime.datetime(2017, 5, 16, 0, 0, tzinfo=<DstTzInfo 'Asia/Kolkata' IST+5:30:00 STD>)  # noqa
    """
    tz = pytz.timezone('Asia/Kolkata')
    result = tz.localize(t)
    return result


def convert_string_to_datetime(date, string_format='%Y-%m-%d'):
    """
    >>> convert_string_to_datetime('2017-05-16')
    '2017-05-16T00:00:00'
    """
    return datetime.strptime(date, string_format).isoformat()


def convert_datetime_to_string(date):
    """
    >>> x = datetime(2017, 5, 16)
    >>> convert_datetime_to_string(x)
    '2017-05-16'
    """
    return date.strftime('%Y-%m-%d')


def pre_load_date_fields(in_data, date_fields, date_format='%m-%d-%Y'):
    """
    Converts the date fields into datetime objects

    Args:
        in_data: dict
        date_fields: list<str>
        date_format: str

    Returns: dict

    """
    for date_field in date_fields:
        value = in_data.get(date_field)
        if value:
            if value == '-':
                in_data[date_field] = None
            else:
                in_data[date_field] = convert_string_to_datetime(
                    date=value,
                    string_format=date_format,
                )
        else:
            in_data[date_field] = None
    return in_data


if __name__ == '__main__':
    from doctest import testmod
    testmod()
