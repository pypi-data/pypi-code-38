import os
import sys
import configparser


def get_section(file, section):
    """
    Get section
    """
    filename = os.path.expanduser(file)
    if not os.path.isfile(filename):
        print("ERROR: {} does not exist".format(file))
        sys.exit(1)
    config = configparser.ConfigParser()
    config.read(filename)
    if section in config.sections():
        return config[section]
    else:
        return {}


def set_section(file, section, kv):
    """
    Write section
    """
    filename = os.path.expanduser(file)
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    config = configparser.ConfigParser()
    config.read(filename)
    if not config.has_section(section):
        config.add_section(section)
    for k, v in kv.items():
        config.set(section, k, v)
    with open(filename, 'w') as fp:
        config.write(fp)
