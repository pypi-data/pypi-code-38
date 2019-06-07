from __future__ import absolute_import
from __future__ import unicode_literals
import cgi
import logging

from webob import exc
from paste import fileapp

from .core import widget_context, WidgetContext
from .resource import ResourceManager
from .render import TemplateEngine

log = logging.getLogger(__name__)

def paste_filter_factory(global_conf, **local_conf):
    config = dict(global_conf)
    config.update(local_conf)
    def filter(app):
        return WidgetMiddleware(app, **config)
    return filter

class WidgetMiddleware(object):

    def __init__(self, app,
                 compress=False,
                 script_name='/_ew_resources/',
                 url_base=None,
                 cache_max_age=60*60*24*365,
                 register_resources=True,
                 use_jsmin=False,
                 use_cssmin=False,
                 extra_headers=None,
                 use_cache=True,
                 **extra_config):
        self.app = app
        self.script_name = script_name
        self.script_name_slim_js = script_name + '_slim/js'
        self.script_name_slim_css = script_name + '_slim/css'
        self.compress = compress
        if url_base is None:
            url_base = self.script_name
        self.url_base = url_base
        self.cache_max_age = cache_max_age
        self.register_resources = register_resources
        self.use_jsmin = use_jsmin
        self.use_cssmin = use_cssmin
        self.extra_headers = extra_headers or []
        self.use_cache = use_cache
        if self.register_resources:
            ResourceManager.register_all_resources()
        TemplateEngine.initialize(extra_config)

    def __call__(self, environ, start_response):
        registry = environ['paste.registry']
        mgr = ResourceManager(
            compress=self.compress,
            script_name=self.script_name,
            url_base=self.url_base,
            cache_max_age=self.cache_max_age,
            use_jsmin=self.use_jsmin,
            use_cssmin=self.use_cssmin,
            use_cache=self.use_cache,
            )
        registry.register(
            widget_context,
            WidgetContext(
                scheme=environ['wsgi.url_scheme'],
                resource_manager=mgr))
        if not environ['PATH_INFO'].startswith(self.script_name):
            result = self.app(environ, start_response)
        elif environ['PATH_INFO'].startswith(self.script_name_slim_js):
            result = self.serve_slim_js(
                mgr, cgi.parse_qs(environ['QUERY_STRING']).get('href', [''])[0],
                environ, start_response)
        elif environ['PATH_INFO'].startswith(self.script_name_slim_css):
            result = self.serve_slim_css(
                mgr, cgi.parse_qs(environ['QUERY_STRING']).get('href', [''])[0],
                environ, start_response)
        else:
            result = self.serve_resource(mgr, environ['PATH_INFO'][len(self.script_name):], environ, start_response)
        return result

    def serve_resource(self, mgr, res_path, environ, start_response):
        fs_path = mgr.get_filename(res_path)
        if fs_path is None:
            log.warning('Could not map %s', res_path)
            log.info('Mapped directories: %r', mgr.paths)
            return exc.HTTPNotFound(res_path)(environ, start_response)
        app = fileapp.FileApp(fs_path, headers=self.extra_headers[:])
        app.cache_control(public=True, max_age=mgr.cache_max_age)
        try:
            return app(environ, start_response)
        except OSError:
            return exc.HTTPNotFound(res_path)(environ, start_response)

    def serve_slim_js(self, mgr, res_path, environ, start_response):
        data = mgr.serve_slim('js', res_path)
        data = data.encode('utf-8')
        app = fileapp.DataApp(data, [(str('Content-Type'), str('text/javascript'))])
        app.cache_control(public=True, max_age=mgr.cache_max_age)
        return app(environ, start_response)
            
    def serve_slim_css(self, mgr, res_path, environ, start_response):
        data = mgr.serve_slim('css', res_path)
        data = data.encode('utf-8')
        app = fileapp.DataApp(data, [(str('Content-Type'), str('text/css'))])
        app.cache_control(public=True, max_age=mgr.cache_max_age)
        return app(environ, start_response)

