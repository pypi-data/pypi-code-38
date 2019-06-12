# # # # # # # # # # # # # # # # # # # # # # # # # #
# Formatting routines
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

def compactify (resources):
    """Improve format of 'resources' dictionary."""

    compact = ''
    for resource in resources:
        compact += '/' + resource ['owner'] + ('-' + str(resource ['address']) if resource ['address'] is not None else '')
    return compact if compact != '' else '/'

import re
# filter to remove special characters from strings to be used as filenames
def plain (name):
    """Filter to remove special characters from strings to be used as filenames."""

    return re.sub (r'\W+', '', name)

def timestamp (time, precise=False, expand=False):
    """Formats time in seconds into a string of (years and days - only if needed), hours and minutes."""

    seconds = round (time)
    minutes = seconds // 60
    hours = minutes // 60
    seconds = seconds % 60
    minutes = minutes % 60
    if not expand:
        timestamp = '%02dh%02dm' % (hours, minutes)
        if precise:
            timestamp += '%02ds' % seconds
    else:
        days = hours // 24
        weeks = days // 7
        months = weeks // 4
        years = months // 12
        hours = hours % 24
        days = days % 7
        weeks = weeks % 4
        months = months % 12
        timestamp = '%d hours %d minutes' % (hours, minutes)
        if precise:
            timestamp += ' %d seconds' % seconds
        if years > 0:
            timestamp = '%d years %d months %d weeks %d days ' % (years, months, weeks, days) + timestamp
        elif months > 0:
            timestamp = '%d months %d weeks %d days ' % (months, weeks, days) + timestamp
        elif weeks > 0:
            timestamp = '%d weeks %d days ' % (weeks, days) + timestamp
        elif days > 0:
            timestamp = '%d days ' % (days) + timestamp
    return timestamp

def intf (number, table=1, empty=0, bar=0):
    """Integer format with multipliers K, M, etc."""

    if bar:
        if table:
            return '-----'
        else:
            return '-'
    if table:
        template = '%4d%1s'
    else:
        template = '%d%s'
    if number == 0 or number is None:
        if empty:
            if table:
                return '     '
            else:
                return ''
        else:
            return template % (0, '')
    from math import log, floor
    sign = -1 if number < 0 else 1
    number = abs (number)
    base = 1000
    magnitude = int ( floor ( log ( number, base ) ) )
    number    = int ( round ( number / ( base ** magnitude ) ) )
    return template % ( sign * number, ['', 'K', 'M', 'G', 'T', 'P', 'E'] [magnitude] )