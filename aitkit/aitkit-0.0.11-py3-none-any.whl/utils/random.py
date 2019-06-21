import string, random

"""Утилитарные методы cо случайными числами"""

def randomString(stringLength=10):
    """Генерирует случайную строку заданной длинны"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))