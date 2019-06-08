import re

# based on https://docs.gitlab.com/ce/workflow/time_tracking.html#configuration
CONVERSION_RATE = {
    'mo': 576000,
    'w': 144000,
    'd': 28800,
    'h': 3600,
    'm': 60,
    's': 1,
}
UNITS = ('mo', 'w', 'd', 'h', 'm', 's')


def parse(s):
    """Return duration in seconds based on the raw string. Return 0 in case of parsing error."""

    try:
        raw_duration = re.search('(added|subtracted) (.*) of time', s).group(2)
    except AttributeError:
        return 0

    duration = 0
    for part in raw_duration.split():
        for unit in UNITS:
            if unit in part:
                duration += int(part.strip(unit)) * CONVERSION_RATE[unit]
                break

    if 'subtracted' in s:
        duration = -duration

    return duration

