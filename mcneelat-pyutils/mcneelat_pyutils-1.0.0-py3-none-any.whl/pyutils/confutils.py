import json


def load_conf(conf_file):
    """
    Load a configuration file (in JSON format) into a dictionary object.
    :param conf_file: path to configuration file
    :return: dictionary object with directives read from conf_file
    """

    print("[*] Reading config from '%s'" % conf_file)
    with open(conf_file) as f:
        conf_data = json.loads(f.read())
    return conf_data
