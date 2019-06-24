import random


def baklava():
    return "yay"


def fib(x):
    """
    :returns an array of first x fib numbers
    :param x: length of to-be-found array
    :return: array of first x fib numbers
    """
    if type(x) != int:
        raise Exception("Input variable must be a positive int")
    if x < 0:
        raise Exception("Input variable must be a positive int")
    result = []
    a = 0
    b = 1
    c = 1
    while len(result) != x:
        result.append(a)
        a = b
        b = c
        c = a + b
    return result


def yesno():
    choices = (
        "Maybe",
        "Yes",
        "No",
        "Probably",
        "Probably not",
        "Perhaps",
        "Nah",
    )
    return random.choice(choices)
