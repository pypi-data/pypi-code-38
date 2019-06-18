from urllib import request
import sys


class DefaultHttpClient:
    def __init__(self):
        self.client = request

    def get(self, url, headers):
        req = self.client.Request(url, None, headers)
        try:
            res = self.client.urlopen(req)
            charset = res.headers.get_content_charset()
            responseData = res.read().decode(charset)
            return responseData
        except Exception as e:
            sys.stderr.write(repr(e) + "\n")
            return None
