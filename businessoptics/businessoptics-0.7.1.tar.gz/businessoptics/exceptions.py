import pprint


class APIError(Exception):
    def __init__(self, url, response, response_json=None, message=None):
        self.url = url
        self.response = response
        self.response_json = response_json
        self._message = message

    def __str__(self):
        url = self.url
        code = self.response.status_code
        error = self._message or pprint.pformat((self.response_json or {}).get('error', 'No error field in response'),
                                                width=140)
        response_text = self.response.text[:5000]
        return ('Error at %(url)s, code %(code)s:\n'
                '%(error)s\n'
                'Response text: %(response_text)s' % locals())
