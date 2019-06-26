from __future__ import unicode_literals
import os
import multiprocessing
import gunicorn.app.base
from gunicorn.six import iteritems
from seetaas_helper.base import logger
from flask import Flask
from flask import request, jsonify, abort
from flask_cors import CORS
app = Flask('seetaas-deploy')
CORS(app, supports_credentials=True)


class _StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(_StandaloneApplication, self).__init__()

    def init(self, parser, opts, args):
        pass

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


@app.route("/", methods=['POST'])
def _handle_image():
    logger.info("receive request")
    try:
        req = request.get_json(force=True)
        base64_image = req['base64_image']
    except KeyError:
        logger.error("not found base64 image")
        return abort(400)
    if len(base64_image) == 0:
        logger.error("base64 image is null")
        return abort(400)
    logger.info("algorithm infer...")
    return jsonify(_Deploy.func(base64_image))


class _Deploy:
    func = None

    @staticmethod
    def register(handler):
        if not callable(handler):
            raise Exception("Handler must be callable")
        _Deploy.func = handler

    @classmethod
    def run(cls, num_worker=1):
        options = {
            'bind': '%s:%s' % ('0.0.0.0', '5050'),
            'workers': num_worker or cls.num_of_workers(),
        }
        if not callable(_Deploy.func):
            raise Exception("Please register your handle function begin run")
        _StandaloneApplication(app, options).run()

    @classmethod
    def num_of_workers(cls):
        workers = os.environ["AUTOCNN_WORKERS"] or 1
        if isinstance(workers, str) and workers.isdigit():
            workers = int(workers)
        assert workers > 0, ValueError
        return workers if workers < multiprocessing.cpu_count() * 2 else multiprocessing.cpu_count() * 2


register_handle = _Deploy.register
run_server = _Deploy.run


if __name__ == '__main__':
    @register_handle
    def handle(base64_str):
        return {
            "object_list": [
                {
                    "class_id": 1,
                    "score": 0.98,
                    "location": [33, 23, 45, 74]
                }
            ]
        }
    _Deploy.run()
