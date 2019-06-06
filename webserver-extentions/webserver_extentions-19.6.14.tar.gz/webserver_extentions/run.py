#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@JackLee.com
===========================================
"""

import os
import sys
import json

try:
    reload(sys)
    sys.setdefaultencoding("utf8")
except:
    pass

cur_dir = os.path.split(os.path.realpath(__file__))[0]
sys.path.append("%s/" % cur_dir)

from webserver_extentions.extention import blueprint_app
from werkzeug.utils import import_string
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from tornado.wsgi import WSGIContainer

cur_dir = os.path.split(os.path.realpath(__file__))[0]
sys.path.append("%s/" % cur_dir)

def exceptionHandler(http_code, msg, app):
    @app.errorhandler(http_code)
    def handle(e):
        return msg


class FlaskApp():
    def __init__(self, config_name="config"):
        self.config = import_string(config_name)
        self.app = self.app_()

    def app_(self):
        conf = self.config.flask_route
        static_url_path = self.config.flask_settings.get("static_url_path", None)
        static_folder = self.config.flask_settings.get("static_folder", "static")
        template_folder = self.config.flask_settings.get("template_folder", "templates")
        app = blueprint_app.App(conf=conf, static_url_path=static_url_path, static_folder=static_folder,
                                template_folder=template_folder).create_app()
        return app

    def run(self):
        host = self.config.flask_settings.get("host", "0.0.0.0")
        port = int(self.config.flask_settings.get("port", 5000))
        debug = self.config.flask_settings.get("debug", True)
        self.app.run(host=host, port=port, debug=debug)

    def aysnc_run(self):
        port = int(self.config.flask_settings.get("port", 5000))
        server = HTTPServer(WSGIContainer(self.app))
        server.listen(port=port)
        IOLoop().current().start()


if __name__ == '__main__':
    app = FlaskApp()
    app.run()
