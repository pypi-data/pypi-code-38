import json
from ms_sdk.Lib.Http.Meta import Meta


class Response:

    _meta = None

    def __init__(self, response):
        """
        Response initializer.
        :param response:
        """
        self.statusCode = response.status_code
        self.headers = response.headers

        contents = response.json()

        try:
            self.data = contents['data']

            if contents.get('status'):
                if contents.get('status') == 'OK':
                    self.success = True
                else:
                    self.success = None
            else:
                self.success = contents['success']
            self.errors = contents.get('error') or None
            self.version = contents['version']
            self.included = contents.get('included')

            try:
                if contents['meta']:
                    self._meta = Meta(contents['meta'].values())
            except:
                pass

        except Exception as ex:
            self.success = False
            self.errors = ex

    def getSuccess(self):
        return self.success

    def getData(self):
        return self.data

    def getErrors(self):
        return self.errors

    def getErrorMessage(self):
        return json.load(self.errors)

    def getVersion(self):
        return self.version

    def getIncluded(self):
        return self.included

    def getStatusCode(self):
        return self.statusCode

    def getMeta(self):
        return self._meta
