def crontab_split(crontab):
    return crontab.split(" ")


def convert(crontab, from_tz, to_tz):
    """
    given a crontab with `from` timezone, convert it to `to` timezone

    Returns:
        A list of new crontabs
    """
    minute, hour, day, month, weekday = crontab_split(crontab)

    return [crontab]
