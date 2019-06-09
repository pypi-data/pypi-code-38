from random import random


def get_random_second(low, high, rnd=2):
    width = high - low
    v = low+random()*width
    return round(v, rnd)
