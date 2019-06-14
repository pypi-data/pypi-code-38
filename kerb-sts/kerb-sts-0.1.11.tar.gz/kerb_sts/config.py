# Copyright 2016 Commerce Technologies, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import logging
import os


def _get_default_config_filename():
    """
    Returns the path of the default Kerb-STS configuration file.
    This is the path that Kerb will look for configuration and
    the location it will write configuration to when the --configure
    parameter is passed in.
    """
    return os.path.expanduser('~/.kerb-sts/config.json')


class Config:
    """
    The Config object stores connection configuration for
    the tool.
    """
    IDP_URL_KEY = 'idp_url'
    ADFS_URL_KEY = 'adfs_url'
    KERB_HOSTNAME_KEY = 'kerb_hostname'
    REGION_KEY = 'region'
    PREFERRED_AUTH_TYPE = 'preferred_auth_type'

    def __init__(self, idp_url, kerb_hostname, region, preferred_auth_type):
        self.idp_url = idp_url
        self.kerb_hostname = kerb_hostname
        self.region = region
        self.preferred_auth_type = preferred_auth_type

    def save(self, filename=_get_default_config_filename()):
        """
        Serializes the config object into the default config location.
        :param filename: where to save the Config to
        """
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        dictionary = {
            Config.IDP_URL_KEY: self.idp_url,
            Config.KERB_HOSTNAME_KEY: self.kerb_hostname,
            Config.REGION_KEY: self.region,
            Config.PREFERRED_AUTH_TYPE: self.preferred_auth_type
        }
        with open(filename, 'w') as f:
            json.dump(dictionary, f)
            logging.info("config file saved to {}".format(filename))

    def is_valid(self):
        """
        Validates that the Config object is valid (non-null non-empty values).
        :return: True if the Config is valid
        """
        return (self.idp_url is not None and self.idp_url is not '' and
                self.region is not None and self.region is not '')

    @staticmethod
    def load(filename=_get_default_config_filename()):
        """
        A factory method for returning a Config object
        that has been deserialized from the given filename.
        :param filename: the path to the config file
        :return: a Config object constructed from the filename's contents
        """
        config = Config(idp_url='', kerb_hostname='', region='', preferred_auth_type='')
        try:
            with open(filename) as f:
                config_json = json.loads(f.read())
                if config_json:
                    if Config.IDP_URL_KEY in config_json:
                        config.idp_url = str(config_json[Config.IDP_URL_KEY])
                    elif Config.ADFS_URL_KEY in config_json:
                        config.idp_url = str(config_json[Config.ADFS_URL_KEY])

                    if Config.KERB_HOSTNAME_KEY in config_json:
                        config.kerb_hostname = str(config_json[Config.KERB_HOSTNAME_KEY])

                    if Config.REGION_KEY in config_json:
                        config.region = str(config_json[Config.REGION_KEY])

                    if Config.PREFERRED_AUTH_TYPE in config_json:
                        config.preferred_auth_type = str(config_json[Config.PREFERRED_AUTH_TYPE])
        except IOError:
            logging.warning("could not read config file {}".format(filename))
        return config
