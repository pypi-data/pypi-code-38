import os
import random
import string
from bamboo_lib.connectors.models import Connector


def grab_connector(file_starting_point, cname):
    """ Given a filepath and connector name, retrieves and builds the
    connector configuration object.

    :param file_starting_point: filepath from which to base the search for the conns.yaml file.
    :param cname: name of the connector to look up
    :return: Connector object
    """
    # try local file first then fall back to global
    par_dir = os.path.abspath(os.path.join(file_starting_point, os.pardir))
    local_conn_path = os.path.join(par_dir, "conns.yaml")
    # source = local_conn_path.get(cname, global_conn_path.get(cname))
    try:
        connector = Connector.fetch(cname, open(local_conn_path))
    except ValueError:
        BAMBOO_FALLBACK_CONNS = os.environ.get("BAMBOO_FALLBACK_CONNS")
        # TODO allow env var to customize default fallback config path
        global_conn_path = os.path.expanduser(os.path.expandvars(BAMBOO_FALLBACK_CONNS))
        connector = Connector.fetch(cname, open(global_conn_path))
    return connector


def random_char(num_characters):
    """ Returns a string of num_characters random ASCII characters.

    :param num_characters: Integer representing the number of characters to appear in the output.
    :return: String
    """
    return ''.join(random.choice(string.ascii_letters) for x in range(num_characters))
