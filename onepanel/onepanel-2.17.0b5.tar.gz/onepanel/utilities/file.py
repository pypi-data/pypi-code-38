import os


def get_file_tree(path, skip_hidden=True):
    """
    Finds all files in the specified path and subdirectories.

    :param path:
    :type path str
    :return: a map with key being the file path and value being the statistics of the file
    """

    result = []

    for root, subdirs, files in os.walk(path):
        if skip_hidden:
            files = [f for f in files if not f[0] == '.']
            subdirs[:] = [d for d in subdirs if not d[0] == '.']

        for name in files:
            result.append(os.path.join(root, name))

    return result
