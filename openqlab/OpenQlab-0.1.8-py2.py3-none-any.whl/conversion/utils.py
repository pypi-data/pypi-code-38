import numpy as np

def human_readable(value, unit=''):
    """
    Return an approximate string representation of a value, with
    appropriate unit prefixes (µ, k, M, ...) added. Values should be between
    1n and 1PHz. Accuracy is ~0.1%.

    Parameters
    ----------
    value: :obj:`float`
        the value to convert into human-readable representation
    unit: :obj:`string`
        an optional unit string, such as 'Hz', 'm'

    Returns
    -------
    :obj:`str`
        the human-readable representation
    """
    prefixes = ['n', 'µ', 'm', '', 'k', 'M', 'G', 'T']
    exp = int(np.log10(value) // 3)
    if exp < -3:
        exp = -3
    elif exp > 4:
        exp = 4
    return '{value:.4g}{prefix}{unit}'.format(
        value=value / 10 ** (exp * 3), prefix=prefixes[exp + 3], unit=unit)
