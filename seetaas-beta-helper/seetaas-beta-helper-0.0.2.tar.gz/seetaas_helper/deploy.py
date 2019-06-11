from __future__ import unicode_literals
import json
import os
import multiprocessing

import gunicorn.app.base
from gunicorn.six import iteritems
try:
    from urllib.parse import parse_qs
except ImportError:
    from urlparse import parse_qs


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(StandaloneApplication, self).__init__()

    def init(self, parser, opts, args):
        pass

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def response_404(environ, start_response):
    status = '404'

    response_json = json.dumps(dict(code=404, err_msg='Not found'))
    response_bytes = bytes(response_json, encoding='utf-8')

    response_headers = [('Content-Type', 'text/html'),
                        ('Content-Length', str(len(response_json)))]

    start_response(status, response_headers)

    return [response_bytes]


def handle_get(environ, start_response):
    status = '200 OK'
    response_json = json.dumps(dict(code=200, data='OK'))

    response_bytes = bytes(response_json, encoding='utf-8')

    data_len = str(len(response_json))
    response_headers = [('Content-Type', 'text/html'),
                        ('Content-Length', data_len)]

    start_response(status, response_headers)
    return [response_bytes]


def handle_post(environ, start_response):
    # the environment variable CONTENT_LENGTH may be empty or missing
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0

    request_body = bytes.decode(environ['wsgi.input'].read(request_body_size))
    post_data = parse_qs(request_body)

    base64_image = post_data.get('base64_image', [''])[0]

    if len(base64_image) < 1:
        return response_404(environ, start_response)

    status = '200 OK'

    response_json = json.dumps(dict(code=200, data=Deploy.func(base64_image)))

    response_bytes = bytes(response_json, encoding='utf-8')
    response_headers = [('Content-Type', 'text/html'),
                        ('Content-Length', str(len(response_json)))]

    start_response(status, response_headers)

    return [response_bytes]


def application(environ, start_response):
    method = environ['REQUEST_METHOD']
    path = environ['PATH_INFO']
    print(method, path)
    if method == 'GET' and path == '/_health':
        return handle_get(environ, start_response)
    elif method == 'POST' and path == "/":
        return handle_post(environ, start_response)
    else:
        return response_404(environ, start_response)


class Deploy:
    func = None

    @staticmethod
    def register(handler):
        if not callable(handler):
            raise Exception("Handler must be callable")
        Deploy.func = handler

    @classmethod
    def run(cls, num_worker=1):
        options = {
            'bind': '%s:%s' % ('0.0.0.0', '5050'),
            'workers': num_worker or cls.num_of_workers(),
        }
        if not callable(Deploy.func):
            raise Exception("Please register your handle function begin run")
        StandaloneApplication(application, options).run()

    @classmethod
    def num_of_workers(cls):
        workers = os.environ["AUTOCNN_WORKERS"] or 1
        if isinstance(workers, str) and workers.isdigit():
            workers = int(workers)
        assert workers > 0, ValueError
        return workers if workers < multiprocessing.cpu_count() * 2 else multiprocessing.cpu_count() * 2


if __name__ == '__main__':
    @Deploy.register
    def handle(base64_str):
        print(base64_str)

    Deploy.run()
