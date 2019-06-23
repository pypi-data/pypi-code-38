"""
  Copyright (c) 2019 Atrio, Inc.

  All rights reserved.
"""

def format_si(number, factor=2 ** 10, prefixes="KMGTPEZY", inner="i", unit="B"):
    """Returns a humanized string representation of a quantity, usually a number of bytes

    :param number: the quantity to be humanized
    :param factor: the factor to be used between prefixes, by default 1024, could be 1000
    :param prefixes: the list of prefixes, by default the official SI ones
    :param inner: the indication of a non-standard factor, by default "i" (the "i" to write GiB instead of GB)
    :param unit: the main base unit that the quantity is expressed in, by default "B" to represent bytes
    :return:
    """
    size = float(number)
    steps = 0
    while size >= factor and steps < len(prefixes):
        size = size / factor
        steps += 1

    prefix = prefixes[steps-1] + inner if steps > 0 else ""
    format_string = "{0:.2f} {1}{2}" if float(size) - int(size) > 0.005 else "{0:.0f} {1}{2}"
    return format_string.format(size, prefix, unit)
