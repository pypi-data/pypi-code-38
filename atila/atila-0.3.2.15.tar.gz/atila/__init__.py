"""
2015. 12. 10
Hans Roh
"""

__version__ = "0.3.2.15"

version_info = tuple (map (lambda x: not x.isdigit () and x or int (x),  __version__.split (".")))

from .patches import skitaipatch
from .Atila import Atila

# Events
app_starting = "app:starting"
app_started = "app:started"
app_restarting = "app:restarting"
app_restarted = "app:restarted"
app_mounted = "app:mounted"
app_unmounting = "app:umounting"

request_failed = "request:failed"
request_success = "request:success"
request_tearing_down = "request:teardown"
request_starting = "request:started"
request_finished = "request:finished"


def load (target, pref = None):
    from rs4 import importer
    import os, copy

    def init_app (directory, pref):
        modinit = os.path.join (directory, "__init__.py")
        if os.path.isfile (modinit):
            mod = importer.from_file ("temp", modinit)
            hasattr (mod, "bootstrap") and mod.bootstrap (pref)
            
    if hasattr (target, "__file__"):         
        directory = os.path.abspath (os.path.join (os.path.dirname (target.__file__), "export", "skitai"))
        module, abspath = importer.importer (directory, "__export__")
    else:
        directory, script = os.path.split (target)
        module, abspath = importer.importer (directory, script [-3:] == ".py" and script [:-3] or script)
    
    if pref:
        init_app (directory, pref)
        app = module.app
        for k, v in copy.copy (pref).items ():
            if k == "config":
                if not hasattr (app, 'config'):
                    app.config = v
                else:    
                    for k, v in copy.copy (pref.config).items ():
                        app.config [k] = v
            else:
                setattr (app, k, v)
                
    return app


