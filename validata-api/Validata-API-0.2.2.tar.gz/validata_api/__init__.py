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
Application definition.
"""


import http.client
import logging

import pkg_resources
import requests
import toml
from flasgger import Swagger
from flask import Flask
from flask_cors import CORS

from . import config
from .json_errors import JsonErrors

log = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

if config.DEBUG_PYTHON_HTTP_CLIENT:
    http.client.HTTPConnection.debuglevel = 1

# Set Werkzeug's `strict_slashes` option for all routes instead of defining it for each route individually.
# From https://stackoverflow.com/a/33285603
app.url_map.strict_slashes = False

JsonErrors(app)

CORS(app)

matomo = None
if config.MATOMO_AUTH_TOKEN and config.MATOMO_BASE_URL and config.MATOMO_SITE_ID:
    from flask_matomo import Matomo
    matomo = Matomo(app, matomo_url=config.MATOMO_BASE_URL,
                    id_site=config.MATOMO_SITE_ID, token_auth=config.MATOMO_AUTH_TOKEN)


app.config['SWAGGER'] = {
    'title': 'Validata API',
    'description': ("This is the documentation of [Validata Web API](https://git.opendatafrance.net/validata/validata-api). "
                    "Each endpoint is listed below, and if you click on it you will see its parameters. "
                    "It's also possible to try these endpoints directly from this page by setting parameters values "
                    "in a web form."),
    "basePath": config.SCRIPT_NAME,
    'version': pkg_resources.get_distribution("validata-api").version,
    'uiversion': 3,
    'termsOfService': None,  # TODO Replace by URL once terms-of-service page will be created.
}
Swagger(app)


# Keep this import after app initialisation (to avoid cyclic imports)
from . import route_handlers  # noqa isort:skip
