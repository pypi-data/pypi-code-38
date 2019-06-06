import io


class WSGIDebugger():
    def __init__(self, application):
        self.status = None
        self.headers = None
        self.application = application

    def start_response(self, status, headers):
        self.status = status
        self.headers = headers

    def test_endpoint(self, method, uri, body=None):
        environ = {
            'REQUEST_METHOD': method.upper(),
            'REQUEST_URI': uri,
        }

        if body:
            environ['CONTENT_LENGTH'] = len(body)
            environ['wsgi.input'] = io.StringIO(body)

        return self.application(environ, self.start_response)[0].decode('utf-8')
