#!/usr/bin/env python

# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import logging


def runapp(debug=False):
    from fastr.web import app
    from fastr import config

    # Add werkzeug logger to the mix for debugging http requests.
    if debug:
        _logger = logging.getLogger('werkzeug')
        _logger.setLevel(logging.INFO)
        _logger.addHandler(logging.StreamHandler())

    app.logger.info("Starting web server (on {}:{}).".format(config.web_hostname, config.web_port))
    app.run(host=config.web_hostname, port=config.web_port, debug=debug)
    app.logger.info("Web server has stopped.")


def main():
    parser = argparse.ArgumentParser(description="Fastr web client")
    parser.add_argument('-d', '--debug', action="store_true", help="Debug mode.")
    args = parser.parse_args()

    runapp(args.debug)

if __name__ == "__main__":
    main()
