import configparser
import os
import re

PATH = '.'



def in_(str_, exclude):
    for exc in exclude:
        if exc in str_:
            return True
    return False


def get_files(path, exclude, exts):
    path_files = list()
    for root, dirs, files in os.walk(path, topdown=True):
        if not in_(root, exclude):
            for file in files:
                if in_(file, exts):
                    path_files.append(os.path.join(root, file))
    return path_files


def str2array(str_):
    str_s = re.split('\n|,', str_)
    return [s for s in str_s if s]

def check_config(file_config):
    if not os.path.isfile(file_config):
        print(f'{file_config} not found')
        return False
    return True


def get_config():
    global PATH
    file_config = os.path.join(PATH, 'vell.ini')

    if not check_config(file_config):
        return None

    config = configparser.ConfigParser()
    config.read(file_config)

    # Files will be checked spell
    exclude = str2array(config['path']['exclude'])
    exts = str2array(config['spell']['extensions'])
    files = get_files(PATH, exclude, exts)

    # Ignore words
    ignore_words = str2array(config['spell']['ignore_words'])

    # Level ignore
    level_ignore = int(config['spell']['level_ignore'])

    return {
        'files': files,
        'ignore_words': ignore_words,
        'level_ignore': level_ignore
    }
