from datetime import timedelta

from django.utils import timezone

import yaml
from dateutil import parser

from .common.errors import ConfigurationError
from populator import loader as app_loader # noqa


def datetime_constructor(loader, node):
    item = loader.construct_scalar(node)
    if not isinstance(item, str) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as date range'.format(item))
    return parser.parse(item)


def timedelta_constructor(loader, node):
    item = loader.construct_scalar(node)

    if not isinstance(item, str) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as date range'.format(item))
    num, typ = item[:-1], item[-1].lower()
    if not num.lstrip('-').isdigit():
        raise ConfigurationError(
            'value {} cannot be interpreted as date range'.format(item))

    num = int(num)
    tmdt = None
    if typ == 'd':
        tmdt = timedelta(days=num)
    elif typ == 'h':
        tmdt = timedelta(seconds=num * 3600)
    elif typ == 'w':
        tmdt = timedelta(days=num * 7)
    elif typ == 'm':
        tmdt = timedelta(seconds=num * 60)
    elif typ == 's':
        tmdt = timedelta(seconds=num)
    return timezone.now() + tmdt


# Global constructors
yaml.Loader.add_constructor('!datetime', datetime_constructor)
yaml.Loader.add_constructor('!timedelta', timedelta_constructor)
