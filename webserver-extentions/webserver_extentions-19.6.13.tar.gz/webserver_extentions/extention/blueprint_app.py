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

from flask import Flask
from flask import Blueprint
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import import_string



class App():
    def __init__(self, conf=None, static_url_path=None,
                 static_folder='static', template_folder='templates'):
        """

        :param conf:
            conf =
                {
                    "bp1":
                        {
                            "api_example.TestApi1": "/test/api/v1",
                            "api_example.TestApi2": "/test/api/v2",
                        }
                }
        """
        self.apis = list()
        self.conf = conf
        self.app = Flask(__name__, static_url_path=static_url_path, static_folder=static_folder,
                         template_folder=template_folder)
        self.db = SQLAlchemy()
        self.handle_exception = self.app.handle_exception

    def create_app(self):
        self.create_blueprint()
        self.regist_blueprint()
        return self.app

    def parse_conf(self):
        pass

    def create_blueprint(self):
        for bp in self.conf:
            blueprint = Blueprint(bp, bp)
            api = Api(blueprint)
            api_ = self.conf.get(bp)
            for a in api_:
                api.add_resource(import_string(a), api_.get(a))
            self.apis.append(blueprint)

    def regist_blueprint(self):
        for one in self.apis:
            self.app.register_blueprint(one)
        self.app.handle_exception = self.handle_exception


def test():
    conf = {
        "bp1":
            {
                "api_example:TestApi1": "/test/api/v1",
                "api_example:TestApi2": "/test/api/v2",
            }
    }

    app = App(conf=conf).create_app()
    app.run()


if __name__ == '__main__':
    test()
