import json


def load_conf(conf_file, verbose=True):
    """
    Load a configuration file (in JSON format) into a dictionary object.
    :param conf_file: path to configuration file
    :param verbose: whether or not to print detailed log message
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
        """
        Initialize class.
        :param verbose: if True, the log method will print out whatever message is sent to it
        """
        self.verbose = verbose

    def log(self, msg):
        """
        Print msg to stdout if verbose.
        :param msg: message to print
        :return: None
        """
        if self.verbose:
            print(msg)
