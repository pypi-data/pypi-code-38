'''
Random number generation functions.
'''

import random

def integer(min, max):
    '''
    Return an integer within a range.
    '''

    return random.randint(min, max)

def integers(min, max, num):
    '''
    Return a list of integers within a range.
    '''

    return [integer(min, max) for _ in range(num)]
