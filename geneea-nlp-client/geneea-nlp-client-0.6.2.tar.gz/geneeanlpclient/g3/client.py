# Copyright 2019 Geneea Analytics s.r.o.
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

"""
This module implements function that encapsulate Geneea General NLP REST API V3 calls.
"""
import json
import os
import warnings

import requests

from geneeanlpclient.common.restutil import remoteCall, DEFAULT_READ_TIMEOUT, DEFAULT_CONNECT_TIMEOUT
from geneeanlpclient import g3


class Client:
    DEFAULT_URL = 'https://api.geneea.com/v3/analysis'
    """The default address of the Geneea NLP G3 API."""

    def __init__(self, *, url: str, userKey: str) -> None:
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'user_key {userKey}',
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept': 'application/json; charset=UTF-8'
        })

    @staticmethod
    def create(*, url: str = DEFAULT_URL, userKey: str = None) -> 'Client':
        """
        Call Geneea G3 Client.

        :param url: Interpretor API URL to call
        :param userKey: API user key, if not specified, loaded from GENEEA_API_KEY environment variable
        :return: G3 client
        """
        if not userKey:
            userKey = os.getenv('GENEEA_API_KEY')

        if not userKey:
            warnings.warn('No user key specified: neither as parameter nor as GENEEA_API_KEY environment variable')

        return Client(url=url, userKey=userKey)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()

    def analyze(self, req: g3.Request, *,
        connectTimeout: float = DEFAULT_CONNECT_TIMEOUT,
        readTimeout: float = DEFAULT_READ_TIMEOUT,
    ) -> g3.G3:
        """
        Call Geneea G3 API.

        :param req: request (data to analyze and parameters)
        :param connectTimeout: connection timeout see: http://docs.python-requests.org/en/latest/user/advanced/#timeouts
        :param readTimeout: read timeout see: http://docs.python-requests.org/en/latest/user/advanced/#timeouts
        :return: analysis as an G3 object
        """

        return remoteCall(
            inputData=req,
            url=self.url,
            serialize=lambda x: json.dumps(x.toDict()),
            deserialize=lambda x: g3.fromDict(json.loads(x)),
            session=self.session,
            connectTimeout=connectTimeout,
            readTimeout=readTimeout
        )



