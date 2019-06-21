"""
Bottle took kit will be used by backend api projects
"""
import importlib
import inspect
import json
import logging
import pkgutil
from datetime import datetime
from decimal import Decimal
from typing import List, Any, Optional
from uuid import UUID

from apispec import APISpec
from apispec.ext.bottle import BottlePlugin
from apispec.ext.marshmallow import MarshmallowPlugin
from bottle import HTTPError, response, JSONPlugin, Bottle, request
from bson import Binary
from marshmallow import Schema

log = logging.getLogger(__name__)


############################################################
# Bottle application Exceptions and handlers
############################################################
class BaseError(HTTPError):
    def __init__(self, body=None, status=None, exception=None, traceback=None, **options):
        super().__init__(status=status or self.default_status, body=body, exception=exception, traceback=traceback,
                         **options)


class ValidationError(BaseError):
    """
    Used in endpoint view method to raise any Validation Error
    """
    default_status = 422


class BadRequestError(BaseError):
    """
    Used in endpoint view method for Bad Request data Error 
    """
    default_status = 400


class UnAuthenticatedError(BaseError):
    """
    Used when request is not pass authentication
    """
    default_status = 401


class UnAuthorizedError(BaseError):
    """
    Used when request is not pass authorization
    """
    default_status = 403


def error_handler(error):
    response.headers['Content-type'] = 'application/json'
    if not isinstance(error, HTTPError):
        return json.dumps({'status': 500, 'errors': str(error)})

    try:
        errors = json.loads(error.body)
        return json.dumps({'status': error.status_code, 'errors': errors})
    except json.JSONDecodeError:
        return json.dumps({'status': error.status_code, 'errors': error.body})


APP_ERROR_HANDLER = {
    400: error_handler,
    404: error_handler,
    422: error_handler,
    500: error_handler,
}


############################################################
# application utils
############################################################
def register_routes(app, routes: list = None):
    routes = routes or []
    for route in routes:
        app.route(*route)


############################################################
# bottle plugins
############################################################

# **************************************************
# FlexibleJsonPlugin
# **************************************************
class FlexibleJSONEncoder(json.JSONEncoder):

    # pylint: disable=method-hidden
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, UUID):
            return str(o)
        if isinstance(o, Binary):
            return str(UUID(bytes=o))
        return super().default(o)


class FlexibleJsonPlugin(JSONPlugin):
    """
    Plugin to enable bottle handle more complex python object
    """

    def __init__(self):
        super().__init__(lambda obj: json.dumps(obj, cls=FlexibleJSONEncoder))


# **************************************************
# APISpecPlugin
# **************************************************
IGNORED_TYPES = ['Schema']


def disable_swagger(callback):
    """
    Decorator for removing endpoint from OpenAPI Swagger JSON
    """
    callback.enable_swagger = False
    return callback


class APISpecPlugin:
    """
    APISpec plugin for bottle
    """
    name = 'apispec'
    api = 2

    def __init__(self, *args, path: str = '/schema.json', scan_package: str = None, **kwargs):
        default_plugins = [BottlePlugin()]
        if scan_package:
            default_plugins.append(MarshmallowPlugin())
        kwargs['plugins'] = kwargs.get('plugins', ()) + tuple(default_plugins)

        self.apispec = APISpec(*args, **kwargs)
        self.scan_package = scan_package
        self.path = path

    def setup(self, app: Bottle = None):
        if not app.routes:
            raise Exception(
                'No routes found. Please be sure to install APISpecPlugin after declaring *all* your routes!  ')
        if self.scan_package:
            self._scan_marshmallow_models(self.scan_package)

        for route in app.routes:
            if hasattr(route.callback, 'enable_swagger') and not route.callback.enble_swagger:
                continue
            self.apispec.add_path(view=route.callback, app=app)

        @app.get(self.path)
        # pylint: disable=unused-variable
        def api_doc():
            return self.apispec.to_dict()

    def apply(self, callback, route):
        return callback

    def _scan_marshmallow_models(self, base_package):
        base_module = importlib.import_module(base_package)
        if '__path__' in dir(base_module):  # package
            for _, name, _ in pkgutil.iter_modules(base_module.__path__):
                self._scan_marshmallow_models('%s.%s' % (base_package, name))
        else:  # module
            for name, obj in inspect.getmembers(base_module):
                if name not in IGNORED_TYPES and inspect.isclass(obj) and issubclass(obj, Schema):
                    self.apispec.definition(name, schema=obj)


# **************************************************
# CorsPlugin
# **************************************************

def enable_cors(callback):
    callback.enable_cors = True
    return callback


class CorsPlugin:
    name = 'cors'
    api = 2

    def __init__(self, origins: List[str] = None, headers: List[str] = None, credentials: bool = False):
        self.allow_credentials = credentials
        self.allowed_headers = headers
        self.allowed_origins = origins or ['*']
        self.cors_url_rules = {}

    def setup(self, app):
        if not app.routes:
            raise Exception(
                'No routes found. Please be sure to install CorsPlugin after declaring *all* your routes!')

        for route in app.routes:
            if not self._is_cors_enabled(route.callback):
                continue
            if route.rule not in self.cors_url_rules:
                self.cors_url_rules[route.rule] = set()
            self.cors_url_rules[route.rule].add(str(route.method).upper())
        if not self.cors_url_rules:
            return  # no CORS-enabled routes defined

        @enable_cors
        def cors_options_route(*args, **kwargs):
            """
            Endpoint view function for CORs 'OPTIONS' request
            """
            return None

        for rule, methods in self.cors_url_rules.items():
            if 'OPTIONS' not in methods:
                methods.add('OPTIONS')
                app.route(rule, 'OPTIONS', cors_options_route)

    def apply(self, callback, context):
        if not self._is_cors_enabled(callback):
            return callback  # do not even touch

        def wrapper(*args, **kwargs):
            origin = request.get_header('origin')

            if origin and not ('*' in self.allowed_origins or origin in self.allowed_origins):
                return ''

            if origin:
                headers = ','.join(self.allowed_headers) if self.allowed_headers else '*'
                methods = ','.join(self.cors_url_rules.get(context.rule, [context.method, 'OPTIONS']))
                response.add_header('Access-Control-Allow-Origin', origin)
                response.add_header('Access-Control-Allow-Headers', headers)
                response.add_header('Access-Control-Allow-Methods', methods)
                response.add_header('Access-Control-Allow-Credentials', str(self.allow_credentials).lower())

            return callback(*args, **kwargs) if context.method != 'OPTIONS' else ''

        return wrapper

    @staticmethod
    def _is_cors_enabled(callback):
        return hasattr(callback, 'enable_cors') and callback.enable_cors


# **************************************************
# API Resource plugin
# **************************************************


def route_mark(path_rule, method: str = 'GET', name=None, apply=None, skip=None, auth: bool = False, **config):
    def view_decorator(callback):
        callback._auth = auth  # add auth mark to endpoint view method
        callback._route_marker = {'path': path_rule, 'method': method, 'name': name, 'apply': apply, 'skip': skip,
                                  **config}
        return callback

    return view_decorator


class Authentication:
    """
    Base authentication class
    """

    def extract_credential(self, *args, **kwargs) -> Optional[Any]:
        """
        Extract credential data from current request
        **Needed to implement in subclass**
        """
        return None

    def is_authenticated(self, *args, **kwargs):
        """
        The default authentication class is always return **True**
        Customize Authentication subclass need to implement its own logical
        """
        return True


class ResourcePlugin:
    """
    Class base view plugin for bottle
    Example:

    @route_mark('/index', 'GET')
    def index_view(self):
        pass
    """
    name = 'resource'
    api = 2
    authentication = Authentication()

    def _get_plugin_routes(self):
        """
        Return all current class's marked route view
        """
        return [(key, value._route_marker) for key, value in self.__class__.__dict__.items() if
                hasattr(value, '_route_marker')]

    def setup(self, app: Bottle = None):
        """
        Register all marked view route to bottle application object
        """
        for view_name, route in self._get_plugin_routes():
            callback = getattr(self.__class__, view_name)
            callback._instance = self  # attache current resource classes's instance to the endpoint for later usage
            route['callback'] = callback
            app.route(**route)

    def apply(self, callback, context=None):
        """
        When bottle application invoke a bottle route's callback,
        if the call back has plugin route marker, do an extra wrapper
        """

        def check_authentication(func, *args, **kwargs):
            if getattr(func, '_auth', False) and not func._instance.authentication.is_authenticated(*args, **kwargs):
                raise HTTPError(401)

        def wrapper(func):
            def func_view(*args, **kwargs):
                if hasattr(func, '_route_marker'):
                    check_authentication(func, *args, **kwargs)
                    return func(func._instance, *args, **kwargs)
                return func(*args, **kwargs)

            return func_view

        return wrapper(callback)


############################################################
# doc template for apispec to generate Bottle api view function's __doc__
############################################################
CREATE_VIEW_FUNCTION_DOC_TEMPLATE = """Create {0} document
            ---
            post:
                description: Create {0} document
                parameters:
                    - in: body
                      name: body
                      required: true
                      schema: {0}
                      description: Request body
                responses:
                    200:
                        description: Success
                    400:
                        description: Bad request
                    422:
                        description: Error
            """

QUERY_VIEW_FUNCTION_DOC_TEMPLATE = """Query {0} document
            ---
            get:
                description: Query {0} document
                responses:
                    200:
                        description: Success
                    400:
                        description: Bad request
                    422:
                        description: Error
            """

DELETE_VIEW_FUNCTION_DOC_TEMPLATE = """Delete {0} document
            ---
            delete:
                description: Delete {0} document
                responses:
                    200:
                        description: Success
                    400:
                        description: Bad request
                    422:
                        description: Error
            """
