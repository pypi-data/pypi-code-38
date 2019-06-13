# -*- coding: utf-8 -*-
# vim: set et sts=2:
#pylint: disable-all

import json

from flask import Response


def as_json(f):
  def inner(*args, **kwargs):
    return Response(json.dumps(f(*args, **kwargs)), mimetype='application/json')
  return inner
