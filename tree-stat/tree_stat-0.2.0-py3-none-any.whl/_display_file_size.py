import math


COMMERCIAL = 1000
INFORMATICS = 2**10
__coefficient_symbols = '_KMGTPEZY'


def display_file_size(size, unit_base=INFORMATICS):
    if size == 0:
        return '0 B'

    size_log = math.floor(math.log(size, unit_base))

    if size_log == 0:
        return '{} B'.format(size)

    coefficients = [s + 'i' if unit_base == INFORMATICS else s for s in __coefficient_symbols]

    if size_log >= len(__coefficient_symbols):
        return '{number:.3f} {coefficient}B'.format(
            number=size / unit_base ** (len(__coefficient_symbols) - 1),
            coefficient=coefficients[-1])

    return '{number:.3f} {coefficient}B'.format(
        number=size / unit_base ** size_log,
        coefficient=coefficients[size_log])
