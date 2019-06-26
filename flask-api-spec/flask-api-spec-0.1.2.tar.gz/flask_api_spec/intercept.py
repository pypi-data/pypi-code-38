import re
import sys
from functools import wraps

import marshmallow
import schema as pyschema
from flask import abort, jsonify, make_response, request
from marshmallow import Schema as MSchema
from marshmallow import fields
from schema import Optional, Schema, SchemaError

from .__base__ import apispecs
from .exceptions import ValidationError
from .request import Request

RE_URL_WITH_PARAM = re.compile(r"<.*?:(.*?)>")
app = None


def _validate(schema_obj, obj):
    schema = Schema(schema_obj)
    try:
        schema.validate(obj)
    except (pyschema.SchemaMissingKeyError, pyschema.SchemaError) as e:
        raise ValidationError('%s, request %s' % (e.args, obj))


def validate_querystring(schema_obj, args):
    n = {}
    for k, v in schema_obj.items():
        if v.optional:
            n[Optional(k)] = v
        else:
            n[k] = v
    query = {}
    for k, v in args.items():
        query[k] = v[0]
    _validate(n, query)


def validate_parameter(schema_obj, kwargs):
    """
    parameters are not optional.
    """
    _validate(schema_obj, kwargs)


def validate_body(schema_obj, json):
    s = schema_obj
    if isinstance(schema_obj, Request):
        s = schema_obj.toSchema()
        _validate(s, json)
    elif isinstance(schema_obj, dict):
        for k, v in schema_obj.items():
            try:
                validate_body(schema_obj[k], json[k])
            except KeyError as e:  # key existing validating
                raise ValidationError('("Missing key: %s",)' % e)


def populate(definition, response):
    new_response = dict()
    if isinstance(definition, MSchema):  # MSchema
        try:
            definition.load(response)
        except marshmallow.exceptions.ValidationError as e:
            raise ValidationError(
                '%s, response: "%s"' % (e.messages, response))
        return definition.dump(response)
    for k, v in definition.items():
        try:
            rv = response[k]
        except:
            rv = getattr(response, k)
        if type(v) == dict:  # dictionary
            new_response[k] = populate(v, rv)
        elif isinstance(v, MSchema):  # MSchema
            new_response[k] = populate(v, rv)
        else:
            new_response[k] = rv
    return new_response


def apispec(schema_obj):
    def deco(f):
        apispecs.append(schema_obj)
        @wraps(f)
        def inner(*args, **kwargs):
            response_as_html = 'text/html' in request.headers.get('accept')
            try:
                if 'query' in schema_obj.keys():
                    validate_querystring(
                        schema_obj['query'], dict(request.args))
                if 'param' in schema_obj.keys():
                    validate_parameter(schema_obj['param'], kwargs)
                if 'body' in schema_obj.keys():
                    validate_body(schema_obj['body'], request.json)
            except SchemaError as e:
                if response_as_html:
                    raise ValidationError(e)
                else:
                    # validation failed. raise 406 error.
                    resp = app.make_response(jsonify(dict(
                        error='validation error', message=str(e))))
                    resp.status_code = 406
                    abort(resp)
            response = f(*args, **kwargs)
            # try:
            #     return make_response(response)
            # except:
            if 'response' in schema_obj.keys():
                response = populate(schema_obj['response'], response)
            return jsonify(response)
        return inner
    return deco


def route(rule, **kwargs):
    if 'apispec' in kwargs:
        spec = kwargs['apispec']
        spec['description'] = ''
        spec['summary'] = spec.get('summary', '')
        if 'methods' in kwargs:
            spec['methods'] = kwargs['methods']
        else:
            spec['methods'] = ['GET']

        del kwargs['apispec']

    def decorator(f):
        endpoint = kwargs.pop('endpoint', None)
        spec['url'] = re.sub(RE_URL_WITH_PARAM, '{\\1}', rule)
        spec['description'] = normalize_doc(f.__doc__) or ''
        f = apispec(spec)(f)
        app.add_url_rule(rule, endpoint, f, **kwargs)
        return f
    return decorator


# https://www.python.org/dev/peps/pep-0257/
def normalize_doc(docstring):
    if not docstring:
        return ''
    # Convert tabs to spaces (following the normal Python rules)
    # and split into a list of lines:
    lines = docstring.expandtabs().splitlines()
    # Determine minimum indentation (first line doesn't count):
    indent = sys.maxsize
    for line in lines[1:]:
        stripped = line.lstrip()
        if stripped:
            indent = min(indent, len(line) - len(stripped))
    # Remove indentation (first line is special):
    trimmed = [lines[0].strip()]
    if indent < sys.maxsize:
        for line in lines[1:]:
            trimmed.append(line[indent:].rstrip())
    # Strip off trailing and leading blank lines:
    while trimmed and not trimmed[-1]:
        trimmed.pop()
    while trimmed and not trimmed[0]:
        trimmed.pop(0)
    # Return a single string:
    return '\n'.join(trimmed)


def init_app(_app):
    global app
    app = _app
    app.route = route
