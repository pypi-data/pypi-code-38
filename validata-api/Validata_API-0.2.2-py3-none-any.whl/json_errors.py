# validata-api -- Validata Web API
# By: Validata Team <pierre.dittgen@jailbreak.paris>
#
# Copyright (C) 2018 OpenDataFrance
# https://git.opendatafrance.net/validata/validata-api
#
# validata-api is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# validata-api is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""
Respond JSON errors instead of HTML. Useful for HTTP/JSON APIs.
"""

# From https://coderwall.com/p/xq88zg/json-exception-handler-for-flask

import logging

import pkg_resources
import ujson as json
from flask import Response, abort
from toolz import assoc
from werkzeug.exceptions import HTTPException, default_exceptions

from . import config

log = logging.getLogger(__name__)


def abort_json(status_code, args, message=None):
    if message is None:
        exc = default_exceptions.get(status_code)
        if exc is not None:
            message = exc.description
    response = make_json_response({"message": message}, args, status_code=status_code)
    if status_code == 500:
        log.error((message, args, status_code))
    abort(response)


def error_handler(error):
    status_code = error.code if isinstance(error, HTTPException) else 500
    message = str(error) if isinstance(error, HTTPException) else "Internal server error"
    return make_json_response({"message": message}, args=None, status_code=status_code)


def make_json_response(data, args, status_code=None):
    meta = {
        "validata-api-version": pkg_resources.get_distribution("validata-api").version,
        "validata-core-version": pkg_resources.get_distribution("validata-core").version,
    }
    if args:
        meta = assoc(meta, "args", args)
    return Response(json.dumps(assoc(data, "_meta", meta), sort_keys=True),
                    mimetype="application/json", status=status_code)


class JsonErrors:
    """
    Respond JSON errors.
    Register error handlers for all HTTP exceptions.

    Special case: when FLASK_DEBUG=1 render HTTP 500 errors as HTML instead of JSON.
    """

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.register(HTTPException)
        for code in default_exceptions:
            self.register(code)

    def register(self, exception_or_code, handler=None):
        self.app.errorhandler(exception_or_code)(handler or error_handler)
