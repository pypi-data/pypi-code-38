import random


def generate_django_secret_key():
    length = 50
    characters = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    return ''.join(
        [random.SystemRandom().choice(characters) for i in range(length)])
