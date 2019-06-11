import random


def get_random(lst: list):
    return {'result': random.choice(lst)}


actions = {"choose random": {'run': get_random}}
