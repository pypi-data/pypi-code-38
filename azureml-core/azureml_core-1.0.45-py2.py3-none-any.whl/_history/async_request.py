# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
import uuid

import requests

from azureml._history.utils.async_task import AsyncTask


class AsyncRequest(AsyncTask):
    """a request"""

    def __init__(self, request=None, ident=None, handler=None, logger=None):
        if ident is None:
            ident = str(uuid.uuid4())
        if logger is None:
            logger = logging.getLogger(__name__)
        else:
            logger.getChild("AsyncRequest")
        super().__init__(ident, request, logger, handler)
        self._request = request

    def wait(self):
        if self._request:
            return self._request.result()
        else:
            return requests.Response()

    def result(self):
        return self.wait()
