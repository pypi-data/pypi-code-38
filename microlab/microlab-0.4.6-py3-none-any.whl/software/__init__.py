from . import os, python, cv


def statistics():
    return {
            'os': os.statistics(),
            'python': python.statistics(),
            'cv': cv.statistics()
           }
