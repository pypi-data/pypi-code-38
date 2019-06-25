import datetime


def calc_movement(change, price):
    if change == 0:
        return 0
    if price == 0:
        return 0
    return (float(change) / float(price)) * 100


def calc_change(price, open):
    return (float(price) - float(open))
