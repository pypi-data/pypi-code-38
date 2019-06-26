from flask import Flask, jsonify
from flask.json import JSONEncoder
from urllib.parse import urlparse
import traceback
import datetime
import logging

logger = logging.getLogger(__name__)

from algonaut.utils import RegexConverter
from algonaut.api.v1.routes import routes

def handle_exception(e):
    response = jsonify({'message' : 'Sorry, an unexpected exception occured.'})
    if hasattr(e,'status_code'):
        response.status_code = e.status_code
    else:
        response.status_code = 500
    logger.error(traceback.format_exc())
    return response

def register_routes(routes, app, prefix):
    for route in routes:
        for route_url, (resource_class, options) in route.items():
            resource = resource_class()
            app.add_url_rule(
                prefix+route_url,
                view_func=resource.as_view(route_url),
                methods=options.get('methods', ['GET']) + ['OPTIONS']
            )

def configure(app, settings, routes, prefix):
    for version, version_routes in routes:
        register_routes(version_routes, app, '{}/{}'.format(prefix, version))
    for name, api_config in settings.get_plugin_apis().items():
        if not api_config:
            continue
        if not isinstance(api_config, (list, tuple)):
            api_config = [api_config]
        for config in api_config:
            plugin_prefix = '{}/{}/{}'.format(prefix, config['version'], name)
            register_routes(config['routes'], app, plugin_prefix)

def page_not_found(e):
    response = jsonify({'message' : 'not found'})
    response.status_code = 404
    return response

def method_not_allowed(e):
    response = jsonify({'message' : 'not allowed'})
    response.status_code = 405
    return response

def get_app(settings, routes=routes):
    o = urlparse(settings.get('url'))
    app = Flask(__name__)
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(405, method_not_allowed)
    app.url_map.converters['regex'] = RegexConverter
    configure(app, settings, (('v1', routes),), o.path)
    app.handle_exception = handle_exception
    app.json_encoder = CustomJSONEncoder
    return app

class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            if obj.utcoffset() is not None:
                raise ValueError("Expected a UTC datetime!")
            return obj.isoformat('T')+'Z'
        return JSONEncoder.default(self, obj)
