# Title: Arithmetic Subtraction
#
# Desc: In this module you can find functions for subtracting up different
#       types integers inside different objects and data structures
#
# Authors: Demir Antay -- demir99antay@gmail.com -- @demirantay
#


def subtract(num1, num2):
    '''
    definition: func(arg1, arg2) {...}
    objective : the function returns you arg1 - arg2
    '''
    return num1 - num2


def subtract_nums(*args):
    '''
    definition: func(*args, . . .) {...}
    objective : you can give as many arguments as you want to this function
                e.g. func(1, 5, 6) or func(9, 1002, 234) and every argument
                will get subtracted from the before argument
    '''

    result = 0

    for argument in args:
        result -= argument

    return result


def arr_subtract(array):
    '''
    definition: func( array[] ) {...}
    objective : returns the subtraction of all elements in the given array
    '''

    result = array[0]

    for i in range(1, len(array), 1):
        result -= array[i]

    return result


def tup_subtract(tuple):
    '''
    definition: func(tuple) {...}
    objective : returns the subtraction of all elements in the given tuple
    '''
    result = tuple[0]

    for i in range(1, len(tuple), 1):
        result -= tuple[i]

    return result
