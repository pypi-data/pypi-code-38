from datetime import datetime


def get_createdAt(trip):
    """
    :param trip: trip Object
    :return: createdAt datetime object
    """
    time = trip['createdAt']
    if isinstance(time, str):
        time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%fz")
    return time
