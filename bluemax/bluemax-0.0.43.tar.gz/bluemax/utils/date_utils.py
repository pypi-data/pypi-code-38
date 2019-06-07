import datetime


def json_date(date):
    if date:
        return date.isoformat().replace("T", " ")


def parse_date(value):
    """
        Returns a Python datetime.datetime object,
        the input must be in some date ISO format
    """
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value
    result = None
    if value:
        try:
            result = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        except:
            try:
                result = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
            except:
                try:
                    result = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                except:
                    result = datetime.datetime.strptime(value, "%Y-%m-%d")

    return result


def parse_unix_time(value):
    return datetime.datetime.fromtimestamp(float(value))
