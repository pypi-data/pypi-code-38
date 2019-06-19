import os


def extract_extension(path):
    filename, file_extension = os.path.splitext(path)
    return file_extension
