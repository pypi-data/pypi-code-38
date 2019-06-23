import os

def dir_dirs(directory:str):
    ''' Lists all subdirectorys of the given directory

    Args:
        directory (str): full path to a directory

    Returns:

        subdirs (list): all entries of directory which are also a directory

    '''
    return [
        os.path.join(directory, entry) for entry in os.listdir(directory)
        if os.path.isdir(os.path.join(directory, entry))
    ]
