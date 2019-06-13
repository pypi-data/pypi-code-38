"""
url search class
"""

import urllib

class UrlRequest():
    """
    Issue url request response is set in
    status and message properties
    POST if data is not None
    GET is data is None

    Args:
        url (:obj:`str`, optional): URL for request
        data (:obj:`dict`, optional): dictionary with data for GET
        headers (:obj:`dict`, optional): dictionary with any needed headers

    Attributes:
        status (int): status code from request
        message (str): message response from request
    """

    def __init__(self, url=None, data=None, headers=None):

        self.url = url
        self.data = data
        self.headers = headers

        self.status = None
        self.message = None

        self._urlSearch()

    def request(self, url=None, data=None, headers=None):
        """
        Issue a new request for url

        Args:
            url (str): URL for request
            data (:obj:`dict`, optional): dictionary with data for GET
            headers (:obj:`dict`, optional): dictionary with any needed headers

        """
        self.url = url
        self.status = data
        self.message = headers

        self.status = None
        self.message = None

        self._urlSearch()

    def _urlSearch(self):
        """
        request url and update
        status and message properties
        """

        if self.url is not None:

            if self.data is not None:
                request = urllib.request.Request(self.url, self.data)
            else:
                request = urllib.request.Request(self.url)

            if self.headers is not None:
                for key in self.headers:
                    request.add_header(key, self.headers[key])

            result = urllib.request.urlopen(request)

            if result:

                self.status = result.status
                self.message = result.read()
