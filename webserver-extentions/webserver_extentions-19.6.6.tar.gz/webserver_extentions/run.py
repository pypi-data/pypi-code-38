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

cur_dir = os.path.split(os.path.realpath(__file__))[0]
sys.path.append("%s/" % cur_dir)


def flask_run(config):
    conf = config.flask_route
    static_url_path = config.flask_settings.get("static_url_path", None)
    static_folder = config.flask_settings.get("static_folder", "static")
    template_folder = config.flask_settings.get("template_folder", "templates")
    host = config.flask_settings.get("host", "0.0.0.0")
    port = int(config.flask_settings.get("port", 5000))
    debug = config.flask_settings.get("debug", True)
    app = blueprint_app.App(conf=conf, static_url_path=static_url_path, static_folder=static_folder,
                            template_folder=template_folder).create_app()
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    config = import_string("config")
    flask_run(config)
