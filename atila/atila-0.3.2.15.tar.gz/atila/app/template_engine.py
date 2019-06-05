import os
from functools import wraps

class TemplateEngine:  
    templates_dirs = []

    def __init__ (self):
        self.jinja_env = None        
        self.chameleon = None
        self._jinja2_patch_options = None
        self._jinja2_filters = {}
        self._template_globals = {}
        self._template_home = None

    def setup_template_engines (self, path):
        self._template_home = path

        # configure jinja --------------------------------------------
        if self._jinja2_patch_options:
            self._jinja_overlay ()
                        
        try:
            from jinja2 import Environment
        except ImportError:
            pass        
        else:    
            loader = self.get_template_loader ()        
            if self.jinja_env:
                # activated skito_jinja
                self.jinja_env.loader = loader
            else:                
                self.jinja_env = Environment (loader = loader)
        
        # chameleon -------------------------------------
        try: 
            from chameleon import PageTemplateLoader
        except ImportError: 
            pass        
        else:
            self.chameleon = PageTemplateLoader (
                os.path.join (path, "templates"),
                auto_reload = self.use_reloader,
                restricted_namespace = False
            )

    def load_jinja_filters (self):    
        if not self._jinja2_filters:
            return
        for k, v in self._jinja2_filters.items ():
            self.jinja_env.filters [k] = v
        self._jinja2_filters = {}

    # decorators --------------------------------------------------
    def template_global (self, name):    
        def decorator(f):
            self.save_function_spec (f)
            @wraps(f)
            def wrapper (*args, **kwargs):                
                return f (the_was._get (), *args, **kwargs)
            self._template_globals [name] = wrapper
            return wrapper
        return decorator
    
    def template_filter (self, name):    
        def decorator(f):
            self._jinja2_filters [name] = f
            @wraps(f)
            def wrapper (*args, **kwargs):                
                return f (*args, **kwargs)            
            return wrapper
        return decorator

    # template engine -----------------------------------------------        
    def skito_jinja (self, option = 0):
        if option == 0:    
            self.jinja_overlay ("${", "}", "<%", "%>", "<!---", "--->")
        elif option == 1:
            self.jinja_overlay ("${", "}", "{%", "%}", "{#", "#}")
        elif option == 2:
            self.jinja_overlay ("{*", "*}", "{%", "%}", "{#", "#}")    
        elif option == 3:
            self.jinja_overlay ("{#", "#}", "{%", "%}", "<!---", "--->")        
        elif option == 4:
            self.jinja_overlay ("##", "##", "{%", "%}", "<!---", "--->")            
        elif option == 5:
            self.jinja_overlay ("{:", ":}", "{%", "%}", "<!---", "--->")                
        elif option == 6:
            self.jinja_overlay ("<%", "%>", "{%", "%}", "<!---", "--->")                    
        elif option == 7:
            self.jinja_overlay ("{%", "%}", "<%", "%>", "<!---", "--->")
        
    def jinja_overlay (
        self, 
        variable_start_string = "{{",
        variable_end_string = "}}", 
        block_start_string = "{%", 
        block_end_string = "%}", 
        comment_start_string = "{#",
        comment_end_string = "#}",
        line_statement_prefix = "%", 
        line_comment_prefix = "%%",
        **karg
    ):
        # delay before app is actual imported
        self._jinja2_patch_options = (
            variable_start_string, variable_end_string, block_start_string, block_end_string, 
            comment_start_string, comment_end_string, line_statement_prefix, line_comment_prefix, 
            karg
        )
    
    def _jinja_overlay (self):    
        from ..patches import jinjapatch
        
        self.jinja_env = jinjapatch.overlay (
            self.app_name, 
            *self._jinja2_patch_options [:-1], 
            **self._jinja2_patch_options [-1]
        )
        
    def render (self, was, template_file, _do_not_use_this_variable_name_ = {}, **karg):
        while template_file and template_file [0] == "/":
            template_file = template_file [1:]    

        if _do_not_use_this_variable_name_: 
            assert not karg, "Can't Use Dictionary and Keyword Args Both"
            karg = _do_not_use_this_variable_name_

        karg ["was"] = was
        karg.update (self._template_globals)
        
        template = self.get_template (template_file)
        rendered = template.render (**karg)        
        return rendered
                    
    def get_template (self, name):
        if name.endswith ('.pt') or name.endswith (".ptal"):
            if self.chameleon is None:
                raise ImportError ('Chameleon template engine is not installed')
            return self.chameleon [name]        
        if self.jinja_env is None:
            raise ImportError ("Jinja2 template engine is not installed")        
        return self.jinja_env.get_template (name)        
    
    def get_template_loader (self):
        from jinja2 import FileSystemLoader, ChoiceLoader
        
        templates = [FileSystemLoader (os.path.join (self._template_home, "templates"))]
        for tdir in self.templates_dirs:
            templates.append (FileSystemLoader (tdir))
        templates.append (FileSystemLoader(os.path.join (os.path.dirname (__file__), 'contrib', 'templates')))                
        return ChoiceLoader (templates)
    