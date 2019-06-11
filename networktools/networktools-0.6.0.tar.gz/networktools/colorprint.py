from termcolor import colored, cprint
import random

"""
Print in Colors

Generate random colors

Print a list of elements with some print fn
"""

def gprint(text, flush = False):
    msg = colored(text, 'green', attrs=['reverse'])
    print(msg, flush=flush)

def bprint(text, flush = False):
    msg = colored(text, 'blue', attrs=['reverse'])
    print(msg, flush=flush)

def rprint(text, flush = False):
    msg = colored(text, 'red', attrs=['reverse'])
    print(msg, flush=flush)


def color_print(color, text):
    msg = colored(text, color, attrs=['reverse'])
    print(msg)


def random_color():
    R = random.randint(10, 255)
    G = random.randint(10, 255)
    B = random.randint(10, 255)
    return (R, G, B)


def get_colors(N):
    list_colors = set()
    for i in range(N):
        while True:
            new_color = random_color()
            if not new_color in list_colors:
                list_colors.add(new_color)
                break
    return list(list_colors)


def deep_print(element, xprint=bprint, char='=#='):
    """
    Print the attributes of an object
    """
    xprint(char*30)
    [print(s) for s in dir(element)]
    xprint(char*30)
