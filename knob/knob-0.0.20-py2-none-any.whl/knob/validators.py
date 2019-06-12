# -*- coding:utf-8 -*-

from django.core.exceptions import ValidationError
import json


def validate_json(value):
    try:
        json.loads(value, strict=False)
    except ValueError as e:
        raise ValidationError(u"It's not a valid json string.")


