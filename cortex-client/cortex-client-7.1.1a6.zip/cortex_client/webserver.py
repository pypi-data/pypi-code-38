"""
Copyright 2018 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import json

import flask

from .types import InputMessage
from .utils import get_logger
from .utils import json_str

log = get_logger(__name__)

webserver_app = flask.Flask(__name__)


@webserver_app.route("/health")
def health():
    """
    Route to provide a health check on the flask container.
    """
    return flask.Response(response='OK!', status=200, mimetype='application/json')

@webserver_app.route("/inquire", methods=['POST'])
def inquire():
    """
    Route to provide inquiry on a model.
    """
    input_msg = _get_input_message_request()
    result = webserver_app.modelrunner.run_inquire(input_msg)
    return json_str(result)

@webserver_app.route("/initialize", methods=['POST'])
def initialize():
    """
    Route to initialize a model.
    """
    input_msg = _get_input_message_request()
    result = webserver_app.modelrunner.run_inquire_init(input_msg)
    return json_str(result)

## Private ##

def _get_input_message_request():
    log.info("Got: {}".format(flask.request.json))
    return InputMessage.from_params(flask.request.json)


if __name__ == "__main__":
    webserver_app.run(host='0.0.0.0', debug=True, port=9091, use_reloader=False)
