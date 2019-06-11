import json


def load_conf(conf_file, verbose=True):
    """
    Load a configuration file (in JSON format) into a dictionary object.
    :param conf_file: path to configuration file
    :return: dictionary object with directives read from conf_file
    """
    if verbose:
        print("[*] Reading config from '%s'" % conf_file)
    with open(conf_file) as f:
        conf_data = json.loads(f.read())
    return conf_data


class AbstractLogUtils(object):
    """Class containing handy methods for logging purposes."""

    def __init__(self, verbose):
        self.verbose = verbose

    def log(self, msg):
        """
        Print msg to stdout if verbose.
        :param msg: message to print
        :return: None
        """
        if self.verbose:
            print(msg)
