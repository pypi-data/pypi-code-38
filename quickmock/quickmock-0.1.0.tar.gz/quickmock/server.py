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


import argparse
import json
import logging
import os
import sys

from flask import Flask
from flask import Response
from flask import request

import quickmock
import quickmock.server as server
from quickmock.validation import ConfigurationReader
from quickmock.utils.exceptions import CorruptConfigurationFormatException


def generate_response(path, method, responses, headers=None, data=None):
    """Method that processes the response

    This method loads. Check the examples directory for different example.

    Args:
        path (str): The path of the request.
        method (str): The method of the HTTP request performed.
        responses (dict): A dictionary where the keys are the methods. The information is
            matched with the information set in the configuration file.
        {
            "host": "0.0.0.0",
            "port": 6000,
            "responses": {
                "GET": {
                    "/simple/1": [
                        {
                            "response": {
                                "status": 200,
                                "return": {
                                    'name': 'James Bond'
                                },
                                "mimetype": "application/json"
                            }
                        }
                    ],
                    "/simple/1001": [
                        {
                            "response": {
                                "status": 200,
                                "return": {
                                    'name': 'James Bond'
                                },
                                "mimetype": "application/json"
                            }
                        }
                    ]
                }
            }
        }
        headers (dict): A dictionary containing the headers added with the request.
        data (dict): A dictionary containing the data included in the request.

    Returns:
        dict. The response to return.
    """
    try:
        candidates = responses[method][path]

        # Iterate through each candidate response
        for path_info in candidates:
                header_checks = path_info.get("checks", {}).get("headers")
                data_checks = path_info.get("checks", {}).get("data")

                if not header_checks:
                    if not data_checks:
                        # No headers | No data
                        return path_info["response"]
                    else:
                        if data_checks["valid"] == data:
                            # No headers | Valid data
                            return path_info["response"]
                        else:
                            # No headers | Invalid data
                            error = path_info["checks"]["data"].get("error")
                            if error:
                                return error
                elif header_checks["valid"] == headers:
                    if not data_checks:
                        # Valid Headers | No data
                        return path_info["response"]
                    else:
                        if data_checks["valid"] == data:
                            # Valid headers | Valid data
                            return path_info["response"]
                        else:
                            # Valid headers | Invalid data
                            error = path_info["checks"]["data"].get("error")
                            if error:
                                return error
                else:
                    # Invalid headers
                    error = path_info["checks"]["headers"].get("error")
                    if error:
                        return error

        # Generic error
        return {
            "status": 404,
            "return": {
                "code": 404,
                "msg": f"No response found for the '{path}'. Are the requirements fulfilled?"
            },
            "mimetype": "application/json"
        }
    except KeyError as e:
        return {
            "status": 404,
            "return": {
                "code": 404,
                "msg": f"URL '{path}' not implemented in the mock"
            },
            "mimetype": "application/json"
        }


def run(args):
    """Main method to deal with mocked services

    Args:
        args (parsed_args): Parsed arguments from the entry_point
    """
    logging.basicConfig(level=getattr(logging, args.logging_level))
    logging.debug(f"Set log level to {args.logging_level}")

    # Logging configuration files
    conf_reader = ConfigurationReader()
    conf = {}

    for c in args.configuration_files:
        try:
            with open(c, "r") as iF:
                text = iF.read()

                new_conf = conf_reader.get_configuration(text)

                if not conf:
                    conf = new_conf
                else:
                    try:
                        for method in new_conf["responses"].keys():
                            if not method in conf["responses"].keys():
                                conf["responses"][method] = new_conf["responses"][method]
                            else:
                                conf["responses"][method].update(new_conf["responses"][method])
                    except KeyError as e:
                        logging.error(
                            f"Format of the configuration found corrupted. The key '{e}' could "
                            "not be found."
                        )
                logging.info(f"Configuration from '{c}' loaded.")
        except FileNotFoundError:
            logging.error(f"File '{c}' not found.")
        except CorruptConfigurationFormatException as e:
            logging.error(f"Error when processing file '{c}': {e}")
    logging.debug(f"Configuration files loaded:\n{json.dumps(conf, indent=2)}")

    if not conf:
        logging.critical("No configuration file properly loaded. Exiting...")
        sys.exit(1)
    else:
        for method in conf["responses"].keys():
            logging.info(f"{method} ({len(conf['responses'][method].keys())} URLs):")
            for url in conf['responses'][method].keys():
                logging.info(f"\t- {url}")

    # Starting the app
    app = Flask(__name__)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>', methods=["GET", "POST"])
    def catch_all(path):
        logging.info(f"Processing {request.method} request to '{path}'...")

        # Get headers as dict
        headers = {}
        for key, value in request.headers.items():
            headers[key] = value
        logging.debug(f"Generated headers:\n{json.dumps(headers, indent=2)}")

        r = generate_response(
            path=path,
            method=request.method,
            responses=conf.get("responses", {}),
            headers=headers,
            data=request.form
        )
        logging.debug(f"Created response: {r}")

        if r.get("mimetype") == "application/json":
            response = json.dumps(r.get("return", "No data found in the response"), indent=2)
        else:
            response = str(r.get("return"))

        return app.response_class(
            response=response,
            status=r.get("status", 400),
            mimetype=r.get("mimetype", "application/json")
        )

    app.run(
        host=conf.get("host", "0.0.0.0"),
        port=conf.get("port", 5000)
    )
