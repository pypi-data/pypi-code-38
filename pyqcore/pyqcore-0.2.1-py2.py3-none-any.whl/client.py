"""
 * Copyright (c) 2019 QuantumCore Inc.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *    http://www.apache.org/licenses/LICENSE-2.0
 * 
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 """
import urllib.request
import json
import numpy as np


class _MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(_MyEncoder, self).default(obj)


class SimpleQCoreClient(object):
    def __init__(self):
        # REST API endpoint
        self._endpoint = "http://localhost:5000"
        # formatting
        self._headers = {"Content-Type": "application/json"}

    def _deserialize(self, content):
        # convert Json to python object
        return json.loads(content)

    def _request(self, path, method, data):
        # encode json
        json_data = json.dumps(data, cls=_MyEncoder).encode("utf-8")

        # call REST API
        request = urllib.request.Request(
            self._endpoint + path, data=json_data, method=method, headers=self._headers
        )

        # decode respose
        with urllib.request.urlopen(request) as response:
            response_body = response.read().decode("utf-8")

        return self._deserialize(response_body)

    def login(self, username, password, endpoint=None):
        # Endpoint setting
        if endpoint:
            self._endpoint = endpoint

        # set query parameters
        request_query = {"username": username, "password": password}

        return self._request("/auth", "POST", request_query)

    def classifier_train(self, X, Y, access_token):
        # token
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": "JWT " + str(access_token["access_token"]),
        }
        # set query parameters
        request_query = {"X": X, "Y": Y}

        return self._request("/classifier/train", "POST", request_query)

    def classifier_test(self, X, Y, access_token):
        # token
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": "JWT " + str(access_token["access_token"]),
        }
        # set query parameters
        request_query = {"X": X, "Y": Y}

        return self._request("/classifier/test", "POST", request_query)

    def classifier_predict(self, X, access_token, softmax_top=None):
        # token
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": "JWT " + str(access_token["access_token"]),
        }
        # set query parameters
        request_query = {"X": X, "softmax_top": softmax_top}

        return self._request("/classifier/predict", "POST", request_query)

    def regression_train(self, X, Y, access_token):
        # token
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": "JWT " + str(access_token["access_token"]),
        }
        # set query parameters
        request_query = {"X": X, "Y": Y}

        return self._request("/regression/train", "POST", request_query)

    def regression_test(self, X, Y, access_token):
        # token
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": "JWT " + str(access_token["access_token"]),
        }
        # set query parameters
        request_query = {"X": X, "Y": Y}

        return self._request("/regression/test", "POST", request_query)

    def regression_predict(self, X, access_token):
        # token
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": "JWT " + str(access_token["access_token"]),
        }
        # set query parameters
        request_query = {"X": X}

        return self._request("/regression/predict", "POST", request_query)

