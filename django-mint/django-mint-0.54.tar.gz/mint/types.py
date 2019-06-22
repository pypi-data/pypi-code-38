from dateutil.parser import parse


def datetime(input):
    return parse(input)


def date(input):
    return parse(input).date()