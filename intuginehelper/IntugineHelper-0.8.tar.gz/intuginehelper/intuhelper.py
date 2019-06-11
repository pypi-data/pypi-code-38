import math


def square(x):
    """
    Return square of a number
    :param x:
    :return: x * x
    """
    return x * x


def get_distance(src, dest):
    """
    Returns the distance between source and destination in meters
    :param src: [lat, lng]
    :param dest: [lat, lng]
    :return: Distance in meters between src and dest
    """
    radius = 6371000  # Radius of the earth in m
    d_lat = math.radians(dest[0] - src[0])
    d_lon = math.radians(dest[1] - src[1])
    a = square(math.sin(d_lat / 2)) + math.cos(math.radians(src[0])) * math.cos(math.radians(dest[0])) * square(
        math.sin(d_lon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return math.floor(radius * c)  # Distance in m


def get_days(diff):
    """
    Returns floating point number for days
    :param diff: timedelta
    :return: floating number
    """
    return diff.total_seconds() / (24 * 60 * 60)


def get_days(start, end):
    """
    :param start: start datetime object
    :param end: end datetime object
    :return: time difference in days as float
    """
    return get_days(end - start)
