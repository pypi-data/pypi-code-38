# Title: Arithmetic Addition
#
# Desc: In this module you can find functions for adding up different types
#       integers inside different objects and data structures
#
# Authors: Demir Antay -- demir99antay@gmail.com -- @demirantay
#


def add(num1, num2):
    '''
    definition: name(arg1, arg2) {...}
    objective : returns the sum of two arguments
    '''
    return num1 + num2


def add_nums(*arg):
    '''
    definition: name(*args, . . .) {...}
    objective : you can give as many arguments as you want to this function
                e.g. func(1, 5, 6) or func(9, 1002, 234)
    '''
    sum = 0

    for argument in arg:
        sum += argument

    return sum


def arr_sum(array):
    '''
    definition: name( array[] ) {...}
    objective : returns the sum of all elements in the given array
    '''

    sum = 0

    for element in array:
        sum += element

    return sum


def tup_sum(tuple):
    '''
    definition: name(tuple) {...}
    objective : returns the sum of all elements in the given tuple
    '''

    sum = 0

    for element in tuple:
        sum += element

    return sum
