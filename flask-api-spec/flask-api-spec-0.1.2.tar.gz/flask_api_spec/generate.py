"""
"""

import sys
from datetime import datetime

import yaml
from marshmallow import Schema as MSchema
from marshmallow import fields

from .value import NestedValue, Value
from .request import Request
from .__base__ import apispecs

PATHS = {}
DEFINITIONS = {}


def generate_type_format_from_schema(ty):
    if ty == int:
        return 'integer', None
    elif ty == str:
        return 'string', None
    elif ty == datetime:
        return 'string', 'date-time'


def parse_paths_spec(apispec):
    global PATHS
    pet = {
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
                        'type': gtype,
                    }
                    if gformat:
                        d['format'] = gformat
                    pet['parameters'].append(d)
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
                        'type': gtype,
                    }
                    if gformat:
                        d['format'] = gformat
                    pet['parameters'].append(d)
                    break
    if 'body' in apispec:
        d, s = parse_request_spec(apispec['body'])
        pet['parameters'].append({
            'in': 'body',
            'name': 'body',
            'required': True,
            'schema': s,
        })
    PATHS[apispec['url']] = {
        apispec['methods'][0].lower(): pet,
    }


def parse_request_spec(request):
    global DEFINITIONS
    nr = {}
    if isinstance(request, Value):
        if request.types[0] == str:
            return {'type': 'string'}, None
        elif request.types[0] == int:
            return {'type': 'integer'}, None
        elif request.types[0] == datetime:
            return {'type': 'string', 'format': 'date-time'}, None
    elif isinstance(request, NestedValue):
        return parse_request_spec(request.nested_class()), {'$ref': '#/definitions/%s' % request.nested_class.__name__}
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
            DEFINITIONS[request.__class__.__name__] = {
                'type': 'object',
                'properties': nr,
            }
            return nr, {'$ref': '#/definitions/%s' % request.__class__.__name__}
    elif isinstance(request, dict):
        for k, v in request.items():
            t, r = parse_request_spec(v)
            if r:
                nr[k] = r
            else:
                nr[k] = t
        return nr, None


def parse_response_spec(response):
    global DEFINITIONS
    nr = {}
    if isinstance(response, fields.String):
        return {'type': 'string'}, None
    elif isinstance(response, fields.Int):
        return {'type': 'integer'}, None
    elif isinstance(response, fields.DateTime):
        return {'type': 'string', 'format': 'date-time'}, None
    elif isinstance(response, fields.Nested):
        return parse_response_spec(response.schema), {'$ref': '#/definitions/%s' % response.schema.__class__.__name__}
    elif isinstance(response, MSchema):
        if response.__class__ and response.__class__.__dict__:
            for k, v in response.__class__.__dict__.get('_declared_fields').items():
                t, r = parse_response_spec(v)
                if r:
                    nr[k] = r
                else:
                    nr[k] = t
            DEFINITIONS[response.__class__.__name__] = {
                'type': 'object',
                'properties': nr,
            }
            return nr, {'$ref': '#/definitions/%s' % response.__class__.__name__}
    elif isinstance(response, dict):
        for k, v in response.items():
            t, r = parse_response_spec(v)
            if r:
                nr[k] = r
            else:
                nr[k] = t
        return nr, None


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

    try:
        yaml.dump({'paths': PATHS}, sys.stdout)
    except Exception as e:
        print(e)
    # print(DEFINITIONS)
    try:
        yaml.dump({'definitions': DEFINITIONS}, sys.stdout)
    except Exception as e:
        print(e)
