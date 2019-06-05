import os
from . import multipart_collector, cookie, session, grpc_collector, ws_executor
from . import wsgi_executor, xmlrpc_executor, grpc_executor, jsonrpc_executor
from aquests.protocols.grpc import discover
from sqlphile import Template, DB_PGSQL
from skitai.wsgi_apps import Config
import skitai
import sys
from .app import mixin

class Atila (mixin.MixIn):
    PRESERVES_ON_RELOAD = ["reloadables", "service_roots"]
    
    def __init__ (self, app_name):
        mixin.MixIn.__init__ (self)
        self.app_name = app_name
        self.home = None
        self.sqlphile = None
        # for bus, set by wsgi_executor
        self.config = Config (preset = True)
        self._aliases = []        
        self._sqlmap_dir = None
                
    def alias (self, *args, **karg):
        name, args = skitai.alias (*args, **karg)
        skitai.dconf ["clusters"].pop (name)
        ctype, members, policy, ssl, max_conns = args        
        self._aliases.append ((ctype, "{}:{}".format (name, self.app_name), members, ssl, policy, max_conns))
        
    def test_client (self, point = "/", approot = ".", numthreads = 1):
        from skitai import testutil
        from skitai.testutil import client    
        
        class Client (client.Client):        
            def make_request (self, *args, **karg):
                request = client.Client.make_request (self, *args, **karg)
                return self.handle_request (request)
                
            def __enter__ (self):
                return self
                
            def __exit__ (self, type, value, tb):
                pass
                     
        testutil.activate ()
        testutil.install_vhost_handler ()        
        testutil.mount (point, (self, approot))
        return Client ()
    
    # directory management ----------------------------------------------------------    
    def set_home (self, path, module = None):
        self.home = path
        
        # for backward competable
        if self.authenticate is True:            
            try:
                self.authenticate = self.authorization
            except AttributeError:     
                self.authenticate = "digest"
        
        self.setup_template_engines (path)
        self.initialize_sqlphile (path)
        
        # vaild packages --------------------------------------
        for d in self.PACKAGE_DIRS:            
            maybe_dir = os.path.join (path, d)
            if os.path.isdir (maybe_dir):
                self.add_package_dir (maybe_dir)
            if d in sys.modules:
                # print ('~~~~~~', d, sys.modules [d])
                self.service_roots.append (sys.modules [d])                

        if module:
            self.find_mountables (module)
        self.mount_externals () # these're not auto reloadad
        self.load_jinja_filters ()
        
    def setup_sqlphile (self, engine, template_dir = "sqlmaps"):
        self.config.sql_engine = engine
        self.config.sqlmap_dir = template_dir
    
    def initialize_sqlphile (self, path):
        self._sqlmap_dir = os.path.join(path, self.config.get ("sqlmap_dir", "sqlmaps"))
        if not os.path.isdir (self._sqlmap_dir):
            self._sqlmap_dir = None
            return
        # If only use sqlmaps, or was default
        self.sqlphile = Template (self.config.get ("sql_engine", DB_PGSQL), self._sqlmap_dir, self.use_reloader)
    
    def get_sql_template (self):
        return self.sqlphile
    
    def get_collector (self, request):
        ct = request.get_header ("content-type")
        if not ct: return
        if ct.startswith ("multipart/form-data"):
            return multipart_collector.MultipartCollector
            
        if ct.startswith ("application/grpc"):
            try:
                i, o = discover.find_type (request.uri [1:])
            except KeyError:
                raise NotImplementedError            
            return grpc_collector.grpc_collector            
    
    # method search -------------------------------------------
    def get_method (self, path_info, request):
        command = request.command.upper ()
        content_type = request.get_header_noparam ('content-type')
        current_app, method, kargs = self, None, {}
        
        if self.use_reloader:
            with self.lock:
                self.maybe_reload ()
                current_app, method, kargs, options, status_code = self.find_method (path_info, command)
        else:
            current_app, method, kargs, options, status_code = self.find_method (path_info, command)
        
        if status_code:
            return current_app, method, kargs, options, status_code

        status_code = 0
        if options:
            allowed_types = options.get ("content_types", [])
            if allowed_types and content_type not in allowed_types:
                return current_app, None, None, options, 415 # unsupported media type
            
            if command == "OPTIONS":								
                allowed_methods = options.get ("methods", [])
                request_method = request.get_header ("Access-Control-Request-Method")
                if request_method and request_method not in allowed_methods:
                    return current_app, None, None, options, 405 # method not allowed
            
                response = request.response
                response.set_header ("Access-Control-Allow-Methods", ", ".join (allowed_methods))
                access_control_max_age = options.get ("access_control_max_age", self.access_control_max_age)    
                if access_control_max_age:
                    response.set_header ("Access-Control-Max-Age", str (access_control_max_age))
                
                requeste_headers = request.get_header ("Access-Control-Request-Headers", "")        
                if requeste_headers:
                    response.set_header ("Access-Control-Allow-Headers", requeste_headers)                    
                status_code = 200
            
            else:
                if not self.is_allowed_origin (request, options.get ("access_control_allow_origin", self.access_control_allow_origin)):
                    status_code =  403
                elif not self.is_authorized (request, options.get ("authenticate", self.authenticate)):
                    status_code =  401
        
        if status_code in (401, 200):
            authenticate = options.get ("authenticate", self.authenticate)
            if authenticate:
                request.response.set_header ("Access-Control-Allow-Credentials", "true")
                            
        access_control_allow_origin = options.get ("access_control_allow_origin", self.access_control_allow_origin)
        if access_control_allow_origin and access_control_allow_origin != 'same':
            request.response.set_header ("Access-Control-Allow-Origin", ", ".join (access_control_allow_origin))
        
        return current_app, method, kargs, options, status_code
    
    #------------------------------------------------------
    def create_on_demand (self, was, name):
        class G: 
            pass
        
        # create just in time objects
        if name == "cookie":
            return cookie.Cookie (was.request, self.securekey, self.basepath [:-1], self.session_timeout)
            
        elif name in ("session", "mbox"):
            if not was.in__dict__ ("cookie"):
                was.cookie = cookie.Cookie (was.request, self.securekey, self.basepath [:-1], self.session_timeout)            
            if name == "session":
                return was.cookie.get_session ()
            if name == "mbox":
                return was.cookie.get_notices ()
                
        elif name == "g":
            return G ()
        
    def cleanup_on_demands (self, was):
        if was.in__dict__ ("g"):
            del was.g
        if not was.in__dict__ ("cookie"):
            return
        for j in ("session", "mbox"):
            if was.in__dict__ (j):        
                delattr (was, j)
        del was.cookie
                                        
    def __call__ (self, env, start_response):
        was = env ["skitai.was"]        
        was.app = self        
        was.response = was.request.response
        
        content_type = env.get ("CONTENT_TYPE", "")
        if content_type.startswith ("text/xml") or content_type.startswith ("application/xml"):
            result = xmlrpc_executor.Executor (env, self.get_method) ()
        elif content_type.startswith ("application/grpc"):
            result = grpc_executor.Executor (env, self.get_method) ()            
        elif content_type.startswith ("application/json-rpc"):
            result = jsonrpc_executor.Executor (env, self.get_method) ()    
        elif env.get ("websocket.params"):
            result = ws_executor.Executor (env, None) ()
        else:    
            result = wsgi_executor.Executor (env, self.get_method) ()
            
        self.cleanup_on_demands (was) # del session, mbox, cookie, g
        del was.response        
        was.app = None        
        return result
        