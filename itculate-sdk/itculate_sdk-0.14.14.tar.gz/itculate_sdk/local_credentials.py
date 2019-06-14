#
# (C) ITculate, Inc. 2015-2017
# All rights reserved
# Licensed under MIT License (see LICENSE)
#

# noinspection PyUnresolvedReferences
from six.moves import configparser
import os


def read_local_credentials(role="admin", home_dir=None):
    credentials_file_name = "credentials"

    home_dir = home_dir or os.path.expanduser("~")

    # Load the file (will load empty if file does not exist)
    credentials_path = os.path.join(home_dir, ".itculate", credentials_file_name)
    config = configparser.ConfigParser()
    config.read([credentials_path])

    try:
        api_key = config.get(role, "api_key")
        api_secret = config.get(role, "api_secret")

        return api_key, api_secret

    except configparser.NoSectionError:
        pass

    except configparser.NoOptionError:
        pass

    return None, None
