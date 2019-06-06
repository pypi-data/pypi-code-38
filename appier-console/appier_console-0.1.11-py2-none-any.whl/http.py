#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (c) 2008-2019 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2019 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import time
import contextlib

from . import base

@contextlib.contextmanager
def ctx_http_callbacks(
    name,
    color = None,
    end_newline = True
):

    with base.ctx_loader(
        color = color,
        end_newline = end_newline
    ) as loader:

        status = dict(
            length = -1,
            received = 0,
            flushed = 0,
            percent = 0.0,
            start = None
        )

        def callback_init(connection):
            loader.set_template("{{spinner}} [%s] Establishing connection " % name)
            loader.flush()

        def callback_open(connection):
            loader.set_template("{{spinner}} [%s] Connection established " % name)
            loader.flush()

        def callback_headers(headers):
            _length = headers.get("content-length", None)
            if _length == None: _length = "-1"
            status["length"] = int(_length)
            status["received"] = 0
            status["flushed"] = 0
            status["percent"] = 0.0
            status["start"] = time.time()

        def callback_data(data):
            status["received"] += len(data)
            if not status["length"] == -1:
                status["percent"] = float(status["received"]) / float(status["length"]) * 100.0
            status["flushed"] = status["received"]
            output()

        def callback_result(result):
            status["percent"] = 100.0
            output()

        def output():
            delta = time.time() - status["start"]
            if delta == 0.0: delta = 1.0
            speed = float(status["received"]) / float(delta) / (1024 * 1024)
            loader.set_template("{{spinner}} [%s] %.02f%% %.02fMB/s" % (name, status["percent"], speed))
            if loader.is_tty: loader.flush()

        yield dict(
            callback_init = callback_init,
            callback_open = callback_open,
            callback_headers = callback_headers,
            callback_data = callback_data,
            callback_result = callback_result
        )
