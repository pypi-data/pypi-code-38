import os

def subfolder_count(path):
    files = folders = 0

    for _, dirnames, filenames in os.walk(path):
        files += len(filenames)
        folders += len(dirnames)

    return folders-1