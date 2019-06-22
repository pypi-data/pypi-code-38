import dateutil.parser


def datetime_from_string(string):
    return dateutil.parser.parse(string)


def string_from_datetime(date):
    if date is None:
        return ""
    if isinstance(date, str):
        date = dateutil.parser.parse(date)
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


def time_from_string(string):
    return dateutil.parser.parse(string)


def string_from_time(time):
    if time is None:
        return ""
    return time.strftime("%H:%M:%S+0000")


def underscore_to_camel(string):
    name = ""
    for s in string.split("_"):
        name += s[0].upper() + s[1:]
    return name


def camel_to_underscore(string):
    name = ""
    i = 0
    for s in string:
        if s.isupper() and i > 0:
            name += "_"
        name += s.lower()
        i += 1
    return name


def str_to_class(name):
    #  Use with Caution! Do not pass any user-generated input into this method
    return eval(name)