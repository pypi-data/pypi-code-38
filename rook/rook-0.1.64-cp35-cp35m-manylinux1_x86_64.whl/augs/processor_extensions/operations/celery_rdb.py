from rook.logger import logger

from rook.processor.paths.arithmetic_path import ArithmeticPath
from rook.processor.namespaces.python_object_namespace import PythonObjectNamespace

_rdb = None
_kwargs = {}


def _get_rdb(**kwargs):
    global _rdb
    global _kwargs

    from . import rdb

    if kwargs and _kwargs != kwargs:
        if _rdb:
            _rdb._close_session()
            _rdb = None
            _kwargs = {}

        _rdb = rdb.Rdb(**kwargs)
        _kwargs = kwargs
    else:
        if not _rdb:
            _rdb = rdb.Rdb()

    return _rdb


class CeleryRdbGetPort(object):

    NAME = 'celery_bind'

    def __init__(self, arguments, factory):
        self.path = ArithmeticPath(arguments['path'])

        try:
            self._kwargs = arguments['rdb']
        except KeyError:
            self._kwargs = {}

    def execute(self, namespace):
        try:
            my_rdb = _get_rdb(**self._kwargs)
            self.path.write_to(namespace, PythonObjectNamespace(my_rdb.port))
        except Exception as exc:
            logger.exception("Failed to execute celery Rdb")


class CeleryRdb(object):

    NAME = 'celery_rdb'

    def __init__(self, arguments, factory):
        try:
            self._kwargs = arguments['rdb']
        except KeyError:
            self._kwargs = {}

    def execute(self, namespace):
        try:
            my_rdb = _get_rdb(**self._kwargs)
            my_rdb.connect()
            my_rdb.set_trace()
        except Exception as exc:
            logger.exception("Failed to execute celery Rdb")
