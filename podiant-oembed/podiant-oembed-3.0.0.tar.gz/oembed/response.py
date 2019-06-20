from django.http.response import HttpResponse
import json


class OEmbedResponse(HttpResponse):
    def __init__(self, kind, width, height, html, version=1.0, title=None):
        super().__init__()

        self.__data = {
            'type': kind,
            'html': html,
            'width': width,
            'height': height,
            'version': version,
            'title': title
        }

        self.content = json.dumps(self.__data)
        self['Content-Type'] = 'application/json'

    def jsonp(self, callback):
        self.content = '%s(%s)' % (
            callback,
            json.dumps(self.__data)
        )

        self['Content-Type'] = 'text/javascript'
        return self
