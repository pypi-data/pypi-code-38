from urllib.parse import unquote_plus, quote_plus
from types import FunctionType
from functools import wraps
import re
import copy
import inspect

RX_RULE = re.compile ("(/<(.+?)>)")

class Router:
    SPECIALS = ("notme", "me", "new")
    def __init__ (self):        
        self.route_map = {}
        self.route_map_fancy = {}        
        self._route_priority = []
        self._function_names = {}        
        
    # Routing ------------------------------------------------------                            
    def route (self, rule, **k):
        def decorator (f):
            self.save_function_spec (f)
            self.add_route (rule, f, **k)
            @wraps(f)
            def wrapper (*args, **kwargs):
                return f (*args, **kwargs)
            self._function_names [id (wrapper)] = self.get_func_id (f)
            return wrapper
        return decorator
    
    def add_route (self, rule, func, **options):
        if rule and rule [0] != "/":
            raise AssertionError ("Url rule should be starts with '/', {} {}".format (rule))
            
        func_id = self.get_func_id (func)
        is_alter_routing = id (func) in self._function_names
        
        if not is_alter_routing:
            if not self._started and not self._reloading and func_id in self._function_names and "argspec" not in options:
                self.log ("def {} is already defined. use another name or mount (ns = 'myns')".format (func_id), "warn")
            
            if func_id in self._function_names and "argspec" not in options:
                # reloading, remove old func
                deletable = None
                for k, v in self._function_names.items ():
                    if v == func_id:
                        deletable = k
                        break
                if deletable:
                    del self._function_names [deletable]

        mount_prefix = self._mount_option.get ("point")
        if not mount_prefix:            
            mount_prefix = self._mount_option.get ("mount")        
                        
        if mount_prefix:            
            while mount_prefix:
                if mount_prefix [-1] == "/":
                    mount_prefix = mount_prefix [:-1]
                else:
                    break    
            rule = mount_prefix + rule
        
        try:
            fspec = self._function_specs [func_id]
        except KeyError:
            fspec =  inspect.getfullargspec(func)            
            self._function_names [id (func)] = func_id
        
        if not is_alter_routing and fspec.varargs is not None:
            raise ValueError ("var args is not allowed")
                            
        options ["args"] = fspec.args [1:]
        options ["keywords"] = fspec.varkw
        
        if fspec.defaults:
            defaults = {}
            argnames = fspec.args[(len (fspec.args) - len (fspec.defaults)):]
            for i in range (len (fspec.defaults)):
                defaults [argnames [i]] = fspec.defaults[i]
            options ["defaults"] = defaults
        
        if self._mount_option.get ("authenticate"):
            options ["authenticate"] = self._mount_option ["authenticate"]
        if self._need_authenticate:
            if func.__name__ == self._need_authenticate [0]:
                options ["authenticate"] = self._need_authenticate [1]
            self._need_authenticate = None        
        # for backward competable    
        if options.get ("authenticate") in (True, 1):
            options ["authenticate"] = self.authenticate or "digest"
        elif options.get ("authenticate") in (False, 0):
            options ["authenticate"] = None
        assert options.get ("authenticate") in self.AUTH_TYPES
         
        s = rule.find ("/<")
        if s == -1:
            s_rule = rule
            try: 
                self.route_map [rule]["__default__"]
            except KeyError:
                pass
            else:
                # IMP: automatically added, but current has priority
                del self.route_map [rule]["__default__"]
            self._function_names [func_id] = (rule,)
            if rule not in self.route_map:
                self.route_map [rule] = {}
            resource = self.route_map [rule]
            proto = (func, func.__name__, func.__code__.co_varnames [1:func.__code__.co_argcount], None, func.__code__.co_argcount - 1, rule, options)

        else:
            prefix = rule [:s]
            s_rule = rule
            rulenames = []
            urlargs = RX_RULE.findall (rule)
            options ["urlargs"] = len (urlargs)
            for r, n in urlargs:
                if n.startswith ("int:"):
                    rulenames.append ((n[4:], n[:3]))
                    rule = rule.replace (r, "/({}|[0-9]+)".format ("|".join (self.SPECIALS)))
                elif n.startswith ("float:"):
                    rulenames.append ((n[6:], n [:5]))
                    rule = rule.replace (r, "/({}|[.0-9]+)".format ("|".join (self.SPECIALS)))
                elif n.startswith ("path:"):
                    rulenames.append ((n[5:], n [:4]))
                    rule = rule.replace (r, "/(.+)")    
                else:
                    rulenames.append ((n, "string"))
                    rule = rule.replace (r, "/([^/]+)")
            rule = "^" + rule + "$"            
            re_rule = re.compile (rule)
            self._function_names [func_id] = (prefix, re_rule)
            
            if prefix not in self.route_map_fancy:
                self.route_map_fancy [prefix] = {}
            if re_rule not in self.route_map_fancy [prefix]:    
                self.route_map_fancy [prefix][re_rule] = {}
                
            resource = self.route_map_fancy [prefix][re_rule]            
            proto = (func, func.__name__, func.__code__.co_varnames [1:func.__code__.co_argcount], tuple (rulenames), func.__code__.co_argcount - 1, s_rule, options)
            
            if s >= 0 and len (rulenames) == 1 and s_rule [-1] == ">" and rulenames [0][0] in options.get ("defaults", {}):
                # implicit mount if not exist explicit one
                simple_rule = s_rule [:s]
                if not simple_rule:
                    simple_rule = mount_prefix and mount_prefix + "/" or "/"

                if simple_rule not in self.route_map:
                    options_ = copy.copy (options)
                    options_ ["argspec"] = proto [2:5]
                    self.add_route (simple_rule [len (mount_prefix or ''):], func, **options_)
            self._route_priority.append ((prefix, re_rule))
            self._route_priority.sort (key = lambda x: len (x [0]), reverse = True)
        
        if "__proto__" in resource:
            methods = set (resource ["__proto__"][-1].get ("methods", []))
        else:
            methods = set (options.get ("methods", []))
            if not methods:
                methods = {"GET", "POST"}
            
        resource ["__proto__"] = proto
        resource ["__default__"] = proto
        for method in options.get ("methods", methods):
            resource [method] = proto
            methods.add (method)
        
        for proto in resource.values ():
            proto [-1]["methods"] = methods
    
    # URL Building ------------------------------------------------
    def urlfor (self, thing, *args, **kargs):
        if isinstance (thing, FunctionType):
            thing = self._function_names [id (thing)]
        if thing.startswith ("/"):
            return self.basepath [:-1] + self.mount_p [:-1] + thing
        
        script_name_only = "__resource_path_only__" in kargs
        try:
            fpath = self._function_names [thing]
            
            if len (fpath) == 2:
                if not args and not kargs:
                    proto = self.route_map [fpath [0]]['__proto__']
                else:
                    proto = self.route_map_fancy [fpath [0]][fpath [1]]['__proto__']                
            else:    
                proto = self.route_map [fpath [0]]['__proto__']
        except KeyError:
            raise NameError ("{} not found".format (str (thing)))
        func, name, fuvars, favars, numvars, str_rule, options = proto
        
        if script_name_only:
            url = str_rule
            if favars:
                s = url.find ("<")
                if s != -1:
                    url = url [:s]
            return self.urlfor (url)
        
        params = {}
        try:
            currents = kargs.pop ("__defaults__")
        except KeyError:
            currents = {}
        else:
            for k, v in currents.items ():
                if k in fuvars:
                    params [k] = v
        
        if "argspec" in options:
            fuvars, favars, numvars = options ["argspec"]
            if len (args) or favars [0][0] in kargs or favars [0][0] in params:
                n, t = favars[0]
                str_rule += "/<{}{}>".format (t != "string" and (t + ":") or "", favars[0][0])
        
        function_args = options.get ("args", [])
        has_kargs = options.get ("keywords")
        
        for i in range (len (args)):
            try:
                name = function_args [i]
            except IndexError:
                raise ValueError ("too many parameters")
            params [name] = args [i]
        
        for k, v in kargs.items ():
            if not has_kargs and k not in function_args:
                raise ValueError ("parameter {} is not allowed".format (k))
            params [k] = v
        
        url = str_rule
        if favars: #fancy [(name, type),...]. /fancy/<int:cid>/<cname>
            for n, t in favars:
                if n not in params:
                    try:
                        params [n] = currents [n]
                    except KeyError:
                        try:
                            params [n] = options ["defaults"][n]                            
                        except KeyError:
                            raise AssertionError ("Argument '%s' missing" % n)
                     
                value = quote_plus (str (params [n]))
                if t == "string":
                    value = value.replace ("+", "_")
                elif t == "path":
                    value = value.replace ("%2F", "/")
                url = url.replace ("<%s%s>" % (t != "string" and t + ":" or "", n), value)
                del params [n]
        
        if params:
            url = url + "?" + "&".join (["%s=%s" % (k, quote_plus (str(v))) for k, v in params.items ()])
            
        return self.urlfor (url)
    build_url = urlfor
        
    # Routing ------------------------------------------------------                            
    def get_route_map (self):
        return self.route_map
    
    def set_route_map (self, route_map):
        self.route_map = route_map
                    
    def get_routed (self, method_chain):
        if not method_chain: 
            return
        temp = method_chain
        while 1:
            routed = temp [1]
            if type (routed) is not list:
                return routed
            temp = routed
                    
    def find_route (self, path_info, command):
        if not path_info:
            return self.urlfor ("/"), None        
        if path_info in self.route_map:
            #command = command in self.route_map [path_info] and command or "__default__"            
            try: 
                proto = self.route_map [path_info][command]
            except KeyError:
                raise AssertionError            
            return proto [0], proto [-1]
        
        trydir = path_info + "/"
        if trydir in self.route_map:
            return self.urlfor (trydir), None
        raise KeyError
    
    def verify_rule (self, path_info, rule, protos, command):
        arglist = rule.findall (path_info)
        if not arglist:
            return None, None, None
        
        try:
            f, n, l, a, c, s, options = protos [command]
        except KeyError:
            raise AssertionError
        
        arglist = arglist [0]
        if type (arglist) is not tuple:
            arglist = (arglist,)
            
        kargs = {}
        for i in range (len(arglist)):
            an, at = a [i]
            if at == "int":
                if arglist [i] in self.SPECIALS:
                    kargs [an] = arglist [i]                  
                else:
                    kargs [an] = int (arglist [i])
            elif at == "float":
                if arglist [i] in self.SPECIALS:
                    kargs [an] = arglist [i]
                else:
                    kargs [an] = float (arglist [i])
            elif at == "path":
                kargs [an] = unquote_plus (arglist [i])
            else:
                # why?? I don't know, either, use hypen
                kargs [an] = unquote_plus (arglist [i]).replace ("_", " ")
                
        return f, options, kargs

    def find_method (self, path_info, command):
        if not (path_info.startswith (self.mount_p) or (path_info + "/").startswith (self.mount_p)):
            return self, None, None, None, 404
        
        path_info = path_info [self.path_suffix_len:]
        method, kargs = None, {}
        
        try:
            try:
                method, options = self.find_route (path_info, command)                
            except KeyError:
                for prefix, rule in self._route_priority:
                    if not path_info.startswith (prefix):
                        continue                    
                    protos = self.route_map_fancy [prefix][rule]
                    try:
                        method, options, kargs = self.verify_rule (path_info, rule, protos, command)
                    except ValueError:
                        return self, None, None, None, 400
                    if method:
                        break
        except AssertionError:
            return self, None, None, None, 405 # method not allowed     

        if method is None:
            return self, None, None, None, 404
        if isinstance (method, str):
            return self, method, None, None, 301
          
        return (
            self, 
            [self._binds_request [0], method] + self._binds_request [1:4], 
            kargs, 
            options, 
            None
        ) 
            