""" Server """
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import uuid
import datetime

from tensorflow.logging import debug, error, fatal, info, warn
import pytz
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from tfmodelserver.timer import Timer


class Server:
    def __init__(self, name: str, host='0.0.0.0', port=9000):
        self._name = name
        self._host = host
        self._port = port

        self._loaded = False

        self._app = Flask(self.name)
        CORS(self.app)

        self._models = {}

    @property
    def name(self):
        return self._name

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def loaded(self):
        return self._loaded

    @property
    def models(self):
        return self._models

    @property
    def app(self):
        return self._app

    def model(self, models):
        if not isinstance(models, list):
            models = [models]

        self.models.update(map(lambda model: (model.name, model), models))
        # for model in models:
        #     self._models.update({model.name: model})

        return self

    def route(self, rule, resolvers=None, models=None, **options):
        if models is not None:
            self.model(models)

        resolvers = resolvers or []
        models = models or []

        orig_decor = self.app.route(rule, **options)

        def decorator(f):
            def wrapped_f(*args, **kwargs):
                with request.timer.start('total'):
                    def mapper(resolver):
                        files = request.files
                        form = request.form
                        return resolver.name, resolver(files=files, form=form)

                    try:
                        kwargs.update(map(mapper, resolvers))
                    except (KeyError, ValueError) as e:
                        return abort(400, e)

                    # TODO: Load input/output tensors
                    kwargs.update(map(lambda model: (model.name, model), models))

                    # TODO: Log function name? or end point

                    return f(*args, **kwargs)

            wrapped_f.__name__ = f.__name__

            return orig_decor(wrapped_f)

        return decorator

    def load(self):
        ###############
        # Load models #
        ###############
        if self.loaded:
            return

        for model in self.models.values():
            info('Loading Model `{}`...'.format(model.name))
            model.load()
            info('Model `{}` is loaded'.format(model.name))

        self._loaded = True

    def run(self):
        self.load()

        def error_handler_generator(status):
            def error_handler(e: Exception):
                res = {
                    'status': status,
                    'msg': str(e)
                }

                info(e)

                return jsonify(res), status

            return error_handler

        for status in [400, 404, 500]:
            self.app.register_error_handler(status, error_handler_generator(status))

        @self.app.errorhandler(400)
        def bad_request(e: Exception):
            res = {
                'status': 400,
                'msg': str(e)
            }

            info(e)

            return jsonify(res), 400

        @self.app.before_request
        def before_request():
            request.timer = Timer()

        @self.app.after_request
        def after_request(res):
            json_obj = res.json

            json_obj.update({
                'request_id': str(uuid.uuid4()),
                'created': datetime.datetime.now(pytz.timezone('Asia/Seoul')).isoformat(),
                'time_elapsed': vars(request.timer),
            })

            if 'status' not in json_obj:
                json_obj.update(status=200)

            res.set_data(json.dumps(json_obj))

            return res

        info('Starting server...')
        self.app.run(host=self.host, port=self.port)
        info('Server Stopped')
