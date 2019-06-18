# -*- coding: utf-8 -*-
# Copyright (c) 2018  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Jan Kaluza <jkaluza@redhat.com>

from flask.json import dumps
from flask import request

import module_build_service


def jsonify(*args, **kwargs):
    # This is `flask.jsonify` version which supports Python list as an input.
    # We cannot use real `jsonify`, because it can handle Python lists as
    # input only since 0.11, but RHEL7 contains 0.10.1.
    # https://github.com/pallets/flask/commit/daceb3e3a028b4b408c4bbdbdef0047f1de3a7c9
    indent = None
    separators = (",", ":")

    if module_build_service.app.config["JSONIFY_PRETTYPRINT_REGULAR"] and not request.is_xhr:
        indent = 2
        separators = (", ", ": ")

    if args and kwargs:
        raise TypeError("jsonify() behavior undefined when passed both args and kwargs")
    elif len(args) == 1:  # single args are passed directly to dumps()
        data = args[0]
    elif args:  # convert multiple args into an array
        data = list(args)
    else:  # convert kwargs to a dict
        data = dict(kwargs)

    # Note that we add '\n' to end of response
    # (see https://github.com/mitsuhiko/flask/pull/1262)
    rv = module_build_service.app.response_class(
        (dumps(data, indent=indent, separators=separators), "\n"), mimetype="application/json")
    return rv
