"""
"""
__all__ = ['BaseView', 'register_views']

import importlib
import inspect
import sys

from flask_classful import FlaskView

from .base import BaseView


def _view_classes(module):
    """Generator for accessing imported FlaskView classes

    :param module: Name of the module to search
    :type module: str
    :return: Yields FlaskView classes
    :rtype: [FlaskView]
    """
    importlib.import_module(module)
    for cls in inspect.getmembers(sys.modules[module], inspect.isclass):
        if issubclass(cls[1], FlaskView) and cls[0] != 'FlaskView':
            yield cls[1]


def register_views(app, view_module, version, prefix='api'):
    """Registers FlaskView classes to the Flask app passed as argument

    :param app: Flask app instance
    :type app: flask.Flask
    :param version: API version string
    :type version: str
    :param prefix: String to prepend to API path
    :type prefix: str or None
    :return:
    """

    if prefix is not None:
        route_prefix = f'{prefix}/{version}'
    else:
        route_prefix = version
    for view in _view_classes(view_module):
        view.register(app, route_prefix=route_prefix)
