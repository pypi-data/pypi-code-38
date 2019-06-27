"""
"""

import sys
from datetime import datetime
from io import StringIO

import yaml
from flask import jsonify
from marshmallow import Schema as MSchema
from marshmallow import fields

from .__base__ import apispecs
from .request import Request
from .response import Response
from .value import NestedValue, Value

PATHS = {}
COMPONENTS = {}


def generate_type_format_from_schema(ty):
    if ty == int:
        return 'integer', None
    elif ty == str:
        return 'string', None
    elif ty == datetime:
        return 'string', 'date-time'


def parse_paths_spec(apispec):
    global PATHS
    data = {
        'parameters': [],
        'tags': apispec.get('tags', []),
        'summary': apispec.get('summary', ''),
        'description': apispec.get('description', ''),
    }
    if 'query' in apispec:
        for k, v in apispec['query'].items():
            for ty in v.types:
                if ty in (int, str, datetime):
                    gtype, gformat = generate_type_format_from_schema(ty)
                    d = {
                        'in': 'query',
                        'name': k,
                        'required': not v.optional,
                        'schema': {
                            'type': gtype,
                        },
                    }
                    if gformat:
                        d['format'] = gformat
                    data['parameters'].append(d)
                    break
    if 'param' in apispec:
        for k, v in apispec['param'].items():
            for ty in v.types:
                if ty in (int, str, datetime):
                    gtype, gformat = generate_type_format_from_schema(ty)
                    d = {
                        'in': 'path',
                        'name': k,
                        'required': not v.optional,
                        'schema': {
                            'type': gtype,
                        },
                    }
                    if gformat:
                        d['format'] = gformat
                    data['parameters'].append(d)
                    break
    if 'body' in apispec:
        d, s = parse_request_spec(apispec['body'])
        data['requestBody'] = {
            'description': '',
            'required': True,
            'content': {
                'application/json': {
                    'schema': s
                },
            },
        }
    if 'response' in apispec:
        d, s = parse_request_spec(apispec['response'])
        data['responses'] = {}
        for k, v in d.items():
            if k == '200':
                data['responses'][k] = {
                    'description': '',
                    'content': {
                        'application/json': {
                            'schema': d['200']
                        }
                    }
                }
            else:
                data['responses'][k] = v
    PATHS[apispec['url']] = {
        apispec['methods'][0].lower(): data,
    }


def stype_string(): return dict(schema=dict(type='string'))


def stype_integer(): return dict(schema=dict(type='integer'))


def stype_boolean(): return dict(schema=dict(type='boolean'))


def stype_datetime(): return dict(schema=dict(type='string', format='date-time'))


def parse_request_spec(request):
    global COMPONENTS
    nr = {}
    if isinstance(request, Value):
        if request.types[0] == str:
            return stype_string(), None
        elif request.types[0] == int:
            return stype_integer(), None
        elif request.types[0] == bool:
            return stype_boolean(), None
        elif request.types[0] == datetime:
            return stype_datetime(), None
    elif isinstance(request, fields.Field):
        if isinstance(request, fields.String):
            return stype_string(), None
        elif isinstance(request, fields.Int):
            return stype_integer(), None
        elif isinstance(request, fields.Boolean):
            return stype_boolean(), None
        elif isinstance(request, fields.DateTime):
            return stype_datetime(), None
        elif isinstance(request, fields.Nested):
            return parse_request_spec(request.schema), {'$ref': '#/components/schemas/%s' % request.schema.__class__.__name__}
    elif isinstance(request, Response):
        if request.__class__ and request.__class__.__dict__:
            for k, v in request.__class__.__dict__.get('_declared_fields').items():
                if k.startswith('__') or callable(v):
                    continue
                t, r = parse_request_spec(v)
                if r:
                    nr[k] = r
                else:
                    nr[k] = t

            nnr = {}
            for j, n in nr.items():
                nnr[j] = n.get('schema', n)  # strip schema key for components

            COMPONENTS[request.__class__.__name__] = {
                'type': 'object',
                'properties': nnr,
            }
            return nr, {'$ref': '#/components/schemas/%s' % request.__class__.__name__}
    elif isinstance(request, NestedValue):
        return parse_request_spec(request.nested_class()), {'$ref': '#/components/schemas/%s' % request.nested_class.__name__}
    elif isinstance(request, Request):
        if request.__class__ and request.__class__.__dict__:
            for k, v in request.__class__.__dict__.items():
                if k.startswith('__') or callable(v):
                    continue
                t, r = parse_request_spec(v)
                if r:
                    nr[k] = r
                else:
                    nr[k] = t

            nnr = {}
            for j, n in nr.items():
                nnr[j] = n.get('schema', n)  # strip schema key for components

            COMPONENTS[request.__class__.__name__] = {
                'type': 'object',
                'properties': nnr,
            }
            return nr, {'$ref': '#/components/schemas/%s' % request.__class__.__name__}
    elif isinstance(request, dict):
        for k, v in request.items():
            t, r = parse_request_spec(v)
            if r:
                nr[k] = r
            else:
                nr[k] = t
        return nr, None
    else:
        return request, None


def parse_response_spec(response):
    global COMPONENTS
    nr = {}
    if isinstance(response, fields.Field):
        if isinstance(response, fields.String):
            return stype_string(), None
        elif isinstance(response, fields.Int):
            return stype_integer(), None
        elif isinstance(response, fields.Boolean):
            return stype_boolean(), None
        elif isinstance(response, fields.DateTime):
            return stype_datetime(), None
        elif isinstance(response, fields.Nested):
            return parse_response_spec(response.schema), {'$ref': '#/components/schemas/%s' % response.schema.__class__.__name__}
    elif isinstance(response, MSchema):
        if response.__class__ and response.__class__.__dict__:
            for k, v in response.__class__.__dict__.get('_declared_fields').items():
                t, r = parse_response_spec(v)
                if r:
                    nr[k] = r
                else:
                    nr[k] = t

            nnr = {}
            for j, n in nr.items():
                nnr[j] = n.get('schema', n)  # strip schema key for components

            COMPONENTS[response.__class__.__name__] = {
                'type': 'object',
                'properties': nnr,
            }
            return nr, {'$ref': '#/components/schemas/%s' % response.__class__.__name__}
    elif isinstance(response, dict):
        for k, v in response.items():
            t, r = parse_response_spec(v)
            if r:
                nr[k] = r
            else:
                nr[k] = t
        return nr, None
    else:
        return response, None


information_default = {
    "openapi": "3.0.1",
    "info": {
        "title": "__TITLE__",
        "description": "__DESCRIPTION__",
        # "termsOfService": "http://swagger.io/terms/",
        "contact": {
            "email": "__EMAIL__"
        },
        "license": {
            "name": "Apache 2.0",
            "url": "http://www.apache.org/licenses/LICENSE-2.0.html"
        },
        "version": "__VERSION"
    },
    "tags": [
        {
            "name": "default",
            "description": "default apis",
            "externalDocs": {
                "description": "Find out more",
                "url": "http://swagger.io"
            }
        },
    ]
}


def generate():
    for spec in apispecs:
        try:
            parse_paths_spec(spec)
            if 'response' in spec.keys():
                v, _ = parse_response_spec(spec['response'])
        except Exception as e:
            import traceback
            print('++++++++++++++++++++++++++++++++++++++++++', e)
            traceback.print_tb(sys.exc_info()[2])

    information = {
        'schemes': ['https', 'http'],
        'swagger': '2.0',
        'info': {
            'termsOfService': 'http://swagger.io/terms/',
            'title': 'Swagger Petstore',
            'contact': {'email': 'apiteam@swagger.io'},
            'version': '1.0.0',
            'description': 'This is a sample server Petstore server.  You can find out more about     Swagger at [http://swagger.io](http://swagger.io) or on [irc.freenode.net, #swagger](http://swagger.io/irc/).      For this sample, you can use the api key `special-key` to test the authorization     filters.',
            'license': {
                'url': 'http://www.apache.org/licenses/LICENSE-2.0.html',
                'name': 'Apache 2.0'
            }},
        'tags': [
            {'externalDocs': {
                'description': 'Find out more',
                'url': 'http://swagger.io'},
             'description':
             'Everything about your Pets', 'name': 'pet'}, {'description': 'Access to Petstore orders', 'name': 'store'}, {'externalDocs': {'description': 'Find out more about our store', 'url': 'http://swagger.io'}, 'description': 'Operations about user', 'name': 'user'}], 'host': 'petstore.swagger.io', 'basePath': '/v2'}

    stream = StringIO()
    s = information_default
    s['paths'] = PATHS
    s['components'] = {
        'schemas': COMPONENTS
    }
    return jsonify(s)
    # information
    yaml.dump(information_default, stream)
    # paths
    try:
        yaml.dump({'paths': PATHS}, stream)
    except Exception as e:
        print(e)
    try:
        yaml.dump({
            'components': {
                'schemas': COMPONENTS
            }}, stream)
    except Exception as e:
        print(e)
    return stream.getvalue()
