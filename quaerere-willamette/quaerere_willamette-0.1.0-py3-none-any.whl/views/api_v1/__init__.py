"""Module for version 1 of the API
"""
__all__ = ['register_views']

from quaerere_base_flask.views import register_views as _register_views

from .web_pages import *
from .web_sites import *

API_VERSION = 'v1'


def register_views(app):
    """Registers FlaskView classes to the Flask app passed as argument

    :param app: Flask app instance
    :type app: flask.Flask
    :return:
    """
    _register_views(app, __name__, API_VERSION)
