###############################################################################
#
#   Copyright 2018-2019 Telefónica
#
#   Quickmock is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


import json
import logging

from quickmock.utils.exceptions import CorruptConfigurationFormatException
from quickmock.utils.mimetypes import MIMETYPES


class ConfigurationReader(object):
    """Object in charge of reading and validating a configuration file"""
    def _is_valid_json(self, data):
        """Checks if a string is a correct JSON

        Args:
            data (string). Checks if the data provided is a valid json.

        Return:
            dict/bool.
        """
        try:
            return json.loads(data)
        except Exception as e:
            raise CorruptConfigurationFormatException(f"Incorrect JSON format: {e}")

    def _is_correct_response(self, response):
        """Checks if a response object has a correct format

        It checks whether a response has a "checks" or "response" attribute. Additionally,
        it is checked whether the only checks in `checks` are linked to `data` and `headers`.
        In the responseit is checked whether the `return` and `status` are provided.
        Mimetype is optional.


        Args:
            response (dict): A candidate response.

        Returns:
            bool.

        Raises:
            quickmock.exceptions.CorruptConfigurationFormatException.
        """
        for key in response.keys():
            if key == "checks":
                if not response[key].keys():
                    for check in response["checks"].keys():
                        if check not in ("data", "headers"):
                            raise CorruptConfigurationFormatException(f"'{check}' check unknown")

            elif key == "response":
                if "status" not in response[key].keys():
                    raise CorruptConfigurationFormatException("Missing status in response")
                try:
                    status = response[key]["status"]
                    int(response[key]["status"])
                except ValueError as e:
                    raise CorruptConfigurationFormatException(f"'{status}' is not an int")

                if "return" not in response[key].keys():
                    raise CorruptConfigurationFormatException("Missing return in response")

                if response[key].get("mimetype"):
                    mime = response[key].get("mimetype")
                    if mime not in MIMETYPES:
                        raise CorruptConfigurationFormatException(f"'{mime}' unknown")
            else:
                raise CorruptConfigurationFormatException(f"Unknown parameter '{key}' in response")

        return True

    def _has_correct_format(self, data_dict):
        """Checks if a given JSON file is in a correct format

        Args:
            data_dict (dict): A dictionary containing the configuration options.

        Return:
            bool.

        Raises:
            quickmock.exceptions.CorruptConfigurationFormatException.
        """
        if "responses" in data_dict.keys():
            for m in data_dict["responses"].keys():
                if m not in ("GET", "POST", "PATCH", "DELETE"):
                    raise CorruptConfigurationFormatException(f"'{m}' is not a valid HTTP method")
                else:
                    for url, response_list in data_dict["responses"][m].items():
                        if type(response_list) is not list:
                            raise CorruptConfigurationFormatException(f"Response SHOULD be a list")

                        for r in response_list:
                            self._is_correct_response(r)
            return True
        else:
            raise CorruptConfigurationFormatException("No responses found")

    def get_configuration(self, data):
        """Read a configuration file and parse it onto a dict

        Args:
            data (str): The configuration data to be analysed.

        Returns:
            dict.

        Raises:
            quickmock.exceptions.CorruptConfigurationFormatException.
        """
        configuration = self._is_valid_json(data)

        if self._has_correct_format(configuration):
            return configuration
        else:
            raise CorruptConfigurationFormatException()
