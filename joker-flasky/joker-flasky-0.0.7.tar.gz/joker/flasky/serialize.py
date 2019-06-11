#!/usr/bin/env python3
# coding: utf-8

from __future__ import unicode_literals

import codecs
import datetime
import decimal
import json

import flask


def jsonp(resp, callback):
    return flask.current_app.response_class(
        callback + '(' + flask.json.dumps(resp) + ');\n',
        mimetype='application/javascript'
    )


class JSONEncoderPlus(flask.json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'as_json_serializable'):
            return o.as_json_serializable()
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, datetime.timedelta):
            return o.total_seconds()
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        return super(JSONEncoderPlus, self).default(o)


def indented_json_dumps(obj, **kwargs):
    kwargs.setdefault('indent', 4)
    kwargs.setdefault('ensure_ascii', False)
    kwargs.setdefault('cls', JSONEncoderPlus)
    return json.dumps(obj, **kwargs)


def indented_json_print(obj, **kwargs):
    print_kwargs = {}
    for k in ['sep', 'end', 'file', 'flush']:
        if k in kwargs:
            print_kwargs[k] = kwargs.pop(k)
    s = indented_json_dumps(obj, **kwargs)
    print(s, **print_kwargs)


# might be useless
def indented_json_print_legacy(obj, **kwargs):
    # https://stackoverflow.com/a/12888081/2925169
    decoder = codecs.getdecoder('unicode_escape')
    print_kwargs = {}
    for k in ['sep', 'end', 'file', 'flush']:
        if k in kwargs:
            print_kwargs[k] = kwargs.pop(k)
    kwargs.setdefault('indent', 4)
    s = json.dumps(obj, **kwargs)
    print(decoder(s)[0], **print_kwargs)
