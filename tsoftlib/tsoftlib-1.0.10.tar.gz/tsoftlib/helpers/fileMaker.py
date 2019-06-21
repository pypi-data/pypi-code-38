import os

def makeFolderIfNotExists(path):
        os.makedirs(path, exist_ok=True)
