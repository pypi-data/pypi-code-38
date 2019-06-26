__all__ = ['register_views']

from .api_v1 import register_views as register_v1_views


def register_views(app):
    app.logger.debug('Initializing v1 endpoints')
    register_v1_views(app)
