import datetime


def calc_movement(change, price):
    return (change / price) * 100


def calc_change(price, open):
    return (price - open)
