import os

def makeIfNotExists(name):
    if not os.path.dirname(name):
        os.makedirs(dir)