import arrow


def time2timestamp(t):
    a = arrow.get(t)
    return a.timestamp
