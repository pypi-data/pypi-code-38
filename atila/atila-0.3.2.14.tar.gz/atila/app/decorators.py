from functools import wraps
import os
import time, threading
import re
import inspect

class Decorators:    
    def __init__ (self):        
        self.handlers = {}        
        self._ws_channels = {}
        self._maintern_funcs = {}        
        self._mount_option = {}        
        self._decos = {
            "bearer_handler": self.default_bearer_handler
        }
        self._reloading = False
        self._function_specs = {}
        self._current_function_specs = {}        
        self._conditions = {}        
        self._cond_check_lock = threading.RLock ()                
        self._binds_server = [None] * 7
        self._binds_request = [None] * 4        

    # function param saver ------------------------------------------
    def get_func_id (self,  func):
        return ("ns" in self._mount_option and self._mount_option ["ns"] + "." or "") + func.__name__
    
    def save_function_spec (self, func):
        # save original function spec for preventing distortion by decorating wrapper
        # all wrapper has *args and **karg but we want to keep original function spec for auto parametering call
        func_id = self.get_func_id (func)
        if func_id not in self._function_specs or func_id not in self._current_function_specs:
            # save origin spec
            self._function_specs [func_id] = inspect.getfullargspec(func)
            self._current_function_specs [func_id] = None
    
    def get_function_spec (self, func):
        # called by websocet_handler 
        func_id = self.get_func_id (func)        
        return self._function_specs.get (func_id)
        
    # app life cycling -------------------------------------------    
    def before_mount (self, f):
        self._binds_server [0] = f        
        return f
    start_up = before_mount
    startup = before_mount
     
    def mounted (self, f):
        self._binds_server [3] = f
        return f
    
    def mounted_or_reloaded (self, f):
        self._binds_server [6] = f
        return f
    
    def before_reload (self, f):
        self._binds_server [5] = f
        return f    
    onreload = before_reload
    reload = before_reload
    
    def reloaded (self, f):
        self._binds_server [1] = f
        return f
    
    def before_umount (self, f):
        self._binds_server [4] = f
        return f
    
    def umounted (self, f):
        self._binds_server [2] = f
        return f
    shutdown = umounted
    
    # Request chains ----------------------------------------------                
    def before_request (self, f):
        self._binds_request [0] = f
        return f
    
    def finish_request (self, f):
        self._binds_request [1] = f
        return f
    
    def failed_request (self, f):
        self._binds_request [2] = f
        return f
    
    def teardown_request (self, f):
        self._binds_request [3] = f
        return f
    
    def testpass_required (self, testfunc):
        def decorator(f):
            self.save_function_spec (f)            
            @wraps(f)
            def wrapper (was, *args, **kwargs):
                response = testfunc (was)
                if response is False:
                    return was.response ("403 Permission Denied")
                elif response is not True and response is not None:
                    return response
                return f (was, *args, **kwargs)
            return wrapper
        return decorator
    
    # parameter helpers ------------------------------------------------   
    RX_EMAIL = re.compile (r"[a-z0-9][-.a-z0-9]*@[-a-z0-9]+\.[-.a-z0-9]{2,}[a-z]$", re.I)
    RX_UUID = re.compile (r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I)
    def _validate_param (self, params, required, ints, floats, emails, uuids, **kargs):
        params = params or {}
        if required:
            for each in required:
                if not params.get (each):
                    return 'parameter {} required'.format (each)                                                
        if ints:
            for each in ints:
                try: int (params [each])
                except ValueError:
                    return 'parameter {} should be integer'.format (each)                                   
        if floats:
            for each in floats:
                try: float (params [each])
                except ValueError:
                    return 'parameter {} should be float'.format (each)                    
        if emails:
            for fd in emails:
                kargs [fd] = self.RX_EMAIL
        if uuids:
            for fd in uuids:
                kargs [fd] = self.RX_UUID

        for fd_, cond in kargs.items ():
            ops = fd_.split ("__")
            fd = ops [0]
            val = params.get (fd)
            if not val:
                continue
            assert len (ops) <= 3 and fd, "Invalid expression"
            if len (ops) == 1:
                if hasattr (cond, "search"):
                    if not cond.search (val):
                        return 'parameter {} is invalid'.format (fd)
                elif val != cond:
                    return 'parameter {} is invalid'.format (fd)
                continue
            
            if len (ops) == 3:
                if ops [1] == "len":
                    val = len (val)
                    fd = "length of {}".format (fd)
                
            op = ops [-1]
            val = (isinstance (cond, (list, tuple)) and type (cond [0]) or type (cond)) (val)                
            if op == "neq":
                if val == cond:
                    return 'parameter {} should be {}'.format (fd, cond)
            elif op == "in":
                if val not in cond:
                    return 'parameter {} should be one of {}'.format (fd, cond)
            elif op == "notin":
                if val in cond:
                    return 'parameter {} should be not one of {}'.format (fd, cond)
            elif op == "between":
                if not (cond [0] <= val <= cond [1]):
                    return 'parameter {} should be between {} ~ {}'.format (fd, cond [0], cond [1])
            elif op == "lte":
                if val > cond:
                    return 'parameter {} should less or equal than {}'.format (fd, cond)
            elif op == "lt":
                if val >= cond:
                    return 'parameter {} should less than {}'.format (fd, cond)
            elif op == "gte":
                if val < cond:
                    return 'parameter {} should greater or equal than {}'.format (fd, cond)
            elif op == "gt":
                if val <= cond:
                    return 'parameter {} should greater than {}'.format (fd, cond)
            else:
                raise ValueError ("Unknown operator: {}".format (op))

    def test_params (self, scope, required = None, ints = None, floats = None, emails = None, uuids = None, **kargs):
        def decorator(f):
            self.save_function_spec (f)
            @wraps(f)
            def wrapper (was, *args, **kwargs):
                more_info = self._validate_param (getattr (was.request, scope), required, ints, floats, emails, uuids, **kargs)
                if more_info:
                    return was.response.adaptive_error ("400 Bad Request", 'missing or bad parameter'.format (scope), 40050, more_info) 
                return f (was, *args, **kwargs)
            return wrapper
        return decorator
    params_required = test_params
    parameters_required = test_params
    
    # Automation ------------------------------------------------------    
    def run_before (self, *funcs):
        def decorator(f):
            self.save_function_spec (f)
            @wraps(f)
            def wrapper (was, *args, **kwargs):
                for func in funcs:
                    response = func (was)
                    if response is not None:
                        return response
                return f (was, *args, **kwargs)
            return wrapper
        return decorator
    
    def run_after (self, *funcs):
        def decorator(f):
            self.save_function_spec (f)            
            @wraps(f)
            def wrapper (was, *args, **kwargs):
                response = f (was, *args, **kwargs)
                for func in funcs:
                    func (was)
                return response
            return wrapper
        return decorator
    
    # Conditional Automation ------------------------------------------------------    
    def _check_condition (self, was, key, func, interval, mtime_func):
        now = time.time ()
        with self._cond_check_lock:
            oldmtime, last_check = self._conditions [key]
        
        if not interval or not oldmtime or now - last_check > interval:
            mtime = mtime_func (key)
            if mtime > oldmtime:
                response = func (was, key)
                with self._cond_check_lock:
                    self._conditions [key] = [mtime, now]
                if response is not None:
                    return response
                    
            elif interval:
                with self._cond_check_lock:
                    self._conditions [key][1] = now                        
        
    def if_updated (self, key, func, interval = 1):
        def decorator(f):
            self.save_function_spec (f)
            self._conditions [key] = [0, 0]
            @wraps(f)
            def wrapper (was, *args, **kwargs):
                response = self._check_condition (was, key, func, interval, was.getlu)
                if response is not None:
                    return response
                return f (was, *args, **kwargs)
            return wrapper
        return decorator
        
    def if_file_modified (self, path, func, interval = 1):
        def decorator(f):
            self.save_function_spec (f)
            self._conditions [path] = [0, 0]            
            @wraps(f)
            def wrapper (was, *args, **kwargs):
                def _getmtime (path): 
                    return os.path.getmtime (path)
                response = self._check_condition (was, path, func, interval, _getmtime)
                if response is not None:
                    return response
                return f (was, *args, **kwargs)
            return wrapper
        return decorator
    
    # Websocket ------------------------------------------------------
    def websocket (self, spec, timeout = 60, onopen = None, onclose = None, encoding = "text"):
        def decorator(f):
            self.save_function_spec (f)
            @wraps(f)
            def wrapper (was, *args, **kwargs):
                if not was.wshasevent ():
                    return f (was, *args, **kwargs)
                if was.wsinit ():
                    return was.wsconfig (spec, timeout, encoding)
                elif was.wsopened ():
                    return onopen and onopen (was) or ''
                elif was.wsclosed ():                    
                    return onclose and onclose (was) or ''
            return wrapper
        return decorator
    websocket_config = websocket
    
    def register_websocket (self, client_id, send):
        self._ws_channels [client_id] = send
    
    def remove_websocket (self, client_id):
        try: self._ws_channels [client_id]
        except KeyError: pass
    
    def websocket_send (self, client_id, msg):
        try: 
            self._ws_channels [client_id] (msg)
        except KeyError: 
            pass
    
    # Mainterinancing -------------------------------------------------------
    def maintain (self, f):
        if not self._started:
            assert f.__name__ not in self._maintern_funcs, "maintain func {} is already exists".format (f.__name__)
        self._maintern_funcs [f.__name__] = f
        return f
    
    # Error handling ------------------------------------------------------    
    def add_error_handler (self, errcode, f, **k):
        self.handlers [errcode] = (f, k)
        
    def error_handler (self, errcode, **k):
        def decorator(f):
            self.add_error_handler (errcode, f, **k)
            @wraps(f)
            def wrapper (*args, **kwargs):
                return f (*args, **kwargs)
            return wrapper
        return decorator
    
    def default_error_handler (self, f):
        self.add_error_handler (0, f)
        return f
    defaulterrorhandler = default_error_handler
    errorhandler = error_handler
    