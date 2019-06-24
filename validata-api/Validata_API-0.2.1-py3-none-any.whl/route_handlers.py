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
Application route handlers.
"""

import logging
import urllib
from io import BytesIO

import cachetools
import pkg_resources
import requests
import tabulator
from flasgger import swag_from
from flask import request
from validata_core import Validator, compute_badge
from validata_core.source_helpers import build_tabulator_params

from . import app, config
from .json_errors import abort_json, make_json_response

# Schema cache size (nb of simultaneously stored schemas)
SCHEMA_CACHE_SIZE = 20
# Schema time to live (in seconds)
SCHEMA_CACHE_TTL = 60


log = logging.getLogger(__name__)

VERSION = pkg_resources.get_distribution("validata-api").version


def bytes_data(f):
    """Gets bytes data from Werkzeug FileStorage instance"""
    iob = BytesIO()
    f.save(iob)
    iob.seek(0)
    return iob.getvalue()


@app.route('/')
def index():
    apidocs_href = "{}/apidocs".format(config.SCRIPT_NAME)
    apidocs_url = urllib.parse.urljoin(request.url, apidocs_href)
    return make_json_response({
        "apidocs_href": apidocs_href,
        "message": "This is the home page of Validata Web API. Its documentation is here: {}".format(apidocs_url)
    }, args=None)


specs_dict = {
    'get': {
        'summary': 'Validate a tabular file from its URL',
        'parameters': [
            {
                'name': 'schema',
                'in': 'query',
                'type': 'string',
                'format': 'url',
                'description': 'URL of schema to use for validation',
                'example': 'https://git.opendatafrance.net/scdl/deliberations/raw/master/schema.json',
                'required': True
            },
            {
                'name': 'url',
                'in': 'query',
                'type': 'string',
                'format': 'url',
                'description': 'URL of tabular file to validate',
                'example': 'https://git.opendatafrance.net/scdl/deliberations/raw/v2.0/examples/Deliberations_ok.csv',
                'required': True
            }
        ],
        'produces': [
            'application/json'
        ]
    },
    'post': {
        'summary': 'Validate an uploaded tabular file',
        'parameters': [
            {
                'name': 'schema',
                'in': 'formData',
                'type': 'string',
                'format': 'url',
                'description': 'URL of schema to use for validation',
                'example': 'https://git.opendatafrance.net/scdl/deliberations/raw/master/schema.json',
                'required': True,
            },
            {
                'name': 'file',
                'in': 'formData',
                'type': 'file',
                'description': 'The file to upload',
                'required': True,
            }
        ],
        'consumes': [
            'multipart/form-data'
        ],
        'produces': [
            'application/json'
        ]
    },
    'responses': {
        '200': {
            'description': 'Validation report',
            'schema': {
                'type': 'object',
                'required': [
                    '_meta',
                    "schema",
                    'report'
                ]
            },
            'examples': [
                {
                    "_meta": {
                        "version": VERSION
                    },
                    "schema": {},
                    "report": {
                        "error-count": 1,
                        "preset": "table",
                        "table-count": 1,
                        "tables": [
                            {
                                "error-count": 2,
                                "errors": [
                                    {
                                        "code": "invalid-column-delimiter",
                                        "column-number": None,
                                        "message": None,
                                        "message-data": {
                                            "detected": ";",
                                            "expected": ","
                                        },
                                        "row-number": None
                                    },
                                    {
                                        "code": "compare-columns-value",
                                        "column-number": 11,
                                        "message": "La valeur de la colonne PREF_DATE [2017-02-03] devrait être supérieure ou égale à la valeur de la colonne DELIB_DATE [2017-10-15]",
                                        "message-data": {
                                            "column1": "PREF_DATE",
                                            "column2": "DELIB_DATE",
                                            "op": "supérieure ou égale",
                                            "value1": "2017-02-03",
                                            "value2": "2017-10-15"
                                        },
                                        "row-number": 2
                                    }
                                ],
                                "format": "inline",
                                "headers": [
                                    "COLL_NOM",
                                    "COLL_SIRET",
                                    "DELIB_ID",
                                    "DELIB_DATE",
                                    "DELIB_MATIERE_CODE",
                                    "DELIB_MATIERE_NOM",
                                    "DELIB_OBJET",
                                    "BUDGET_ANNEE",
                                    "BUDGET_NOM",
                                    "PREF_ID",
                                    "PREF_DATE",
                                    "VOTE_EFFECTIF",
                                    "VOTE_REEL",
                                    "VOTE_POUR",
                                    "VOTE_CONTRE",
                                    "VOTE_ABSTENTION",
                                    "DELIB_URL"
                                ],
                                "row-count": 2,
                                "schema": "table-schema",
                                "source": "inline",
                                "time": 0.006,
                                "valid": False
                            }
                        ],
                        "time": 0.014,
                        "valid": False,
                        "warnings": []
                    }
                }
            ]
        },
        '400': {
            'description': 'Error',
            'schema': {
                'type': 'object',
                'required': [
                    '_meta',
                    'message'
                ]
            },
            'examples': [
                {
                    "_meta": {
                        "version": VERSION
                    },
                    "message": "Unsupported format error"
                }
            ]
        }
    }
}


@cachetools.cached(cachetools.TTLCache(SCHEMA_CACHE_SIZE, SCHEMA_CACHE_TTL))
def download_schema(schema_url):
    """Download schema by its given url"""

    return requests.get(schema_url).json()


@app.route('/validate', methods={"GET", "POST"})
@swag_from(specs_dict)
def validate():
    # Extract parameters

    if request.method == 'GET':
        args = {
            'schema': request.args.get('schema'),
            'url': request.args.get('url'),
        }
    else:
        assert request.method == 'POST', request.method
        args = {
            'schema': request.form.get('schema'),
        }

    if not args['schema']:
        abort_json(400, args, 'Missing or empty "schema" parameter')

    # Download Schema from URL to get control on cache
    # schema json dict is passed to validate function as a dict
    try:
        schema_dict = download_schema(args['schema'])

    except Exception as err:
        abort_json(400, {}, str(err))

    if request.method == 'GET':
        # URL validation
        if not args['url']:
            abort_json(400, args, 'Missing or empty "url" parameter')

        params = build_tabulator_params('url', args['url'], args['url'])

    elif request.method == 'POST':
        # Uploaded file validation
        f = request.files.get('file')
        if f is None:
            abort_json(400, args, 'Missing or empty "file" parameter')

        params = build_tabulator_params('file', f.filename, bytes_data(f))

    try:
        goodtables_report = Validator().validate(
            schema=schema_dict,
            force_strings=True,
            **params,
        )
    except tabulator.exceptions.FormatError as exc:
        log.exception("Error validating %r with %r", args['schema'], params)
        abort_json(400, args, str(exc))

    body = {
        'report': goodtables_report,
    }

    # badge info
    if config.BADGE_CONFIG is not None:
        body["badge"] = compute_badge(goodtables_report, config.BADGE_CONFIG)

    return make_json_response(body, args)
