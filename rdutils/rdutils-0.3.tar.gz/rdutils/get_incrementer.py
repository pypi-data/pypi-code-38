# get_incrementer.py
"""Helper function to create counter strings with a set length throughout."""
__version__ = '0.2'
__author__ = 'Rob Dupre (KU)'


def get_incrementer(num, num_digits):
    """Returns string containing num prefixed by zeros such that the final length is equal to num_digits
    :param num: an integer number
    :param num_digits: the desired length of the returned number
    :return: string number
    """
    if type(num) != int:
        print('Number is not an Int.')
        return None

    if num >= 10**num_digits:
        print('NUMBER IS LARGER THAN THE MAX POSSIBLE BASED ON num_digits')
        return None
    else:
        if num > 9999999:
            number_length = 8
        elif num > 999999:
            number_length = 7
        elif num > 99999:
            number_length = 6
        elif num > 9999:
            number_length = 5
        elif num > 999:
            number_length = 4
        elif num > 99:
            number_length = 3
        elif num > 9:
            number_length = 2
        else:
            number_length = 1

    char = ''
    for i in range(num_digits - number_length):
        char = char + '0'
    return char + str(num)


def get_num_length(num):
    """Returns the number of characters contained in num
    :param num: an integer number
    :return: number of characters in num
    """
    if type(num) == int:
        return len(str(num))
    else:
        print('Number is not an Int. Length will include the decimal')
        return len(str(num))
