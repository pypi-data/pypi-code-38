'''
Dice notation parsing functions.
'''

import re

DEFAULT = {'dice': 1, 'plus': 0}
REGEXPS = [
    r'd(?P<size>\d+)',
    r'(?P<dice>\d+)d(?P<size>\d+)',
    r'(?P<dice>\d+)d(?P<size>\d+)\+(?P<plus>\d+)',
]

def parse(string):
    '''
    Return a dice dict from a parsed notation string.
    '''

    for regexp in REGEXPS:
        match = re.fullmatch(regexp, string)
        if match:
            data = {**DEFAULT, **match.groupdict()}
            return {key: int(val) for key, val in data.items()}

    raise ValueError(f'cannot parse notation {string!r}')
