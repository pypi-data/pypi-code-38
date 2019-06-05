import delune
import os
from . import api
import codecs
import json
 
def __mount__ (app):    
    @app.route ("/", methods = ["GET"])
    @app.permission_required (["replica", "index"])
    def collections (was, alias = None, side_effect = ""):
        return was.response.API (collections = list (delune.status ().keys ()))

    @app.route ("/<alias>", methods = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
    @app.permission_required (["replica", "index"])
    def collections2 (was, alias, side_effect = ""):
        fn = api.getdir ("config", alias)
        if was.request.method == "GET":        
            if not delune.get (alias):
                return was.response.Fault ("404 Not Found", 40401, "resource %s not exist" % alias)                
            status = delune.status (alias)
            conf = api.getdir ("config", alias)
            with codecs.open (conf, "r", "utf8") as f:
                colopt = json.loads (f.read ())        
                status ['colopt'] = {
                    'data': colopt,
                    'mtime':     os.path.getmtime (conf),
                    'size':     os.path.getsize (conf),
                    'path': conf
                }
            return was.response.API (status)

        if was.request.method == "DELETE":
            if not os.path.isfile (fn):
                return was.response.Fault ("404 Not Found", 40401, "resource not exist")
            
            a, b = os.path.split (fn)
            if side_effect.find ("data") != -1:
                newfn = os.path.join (a, "-" + b)
            else:
                newfn = os.path.join (a, "#" + b)        
            if os.path.isfile (newfn):
                os.remoive (newfn)
            os.rename (fn, newfn)
            
            was.setlu (delune.SIG_UPD)
            if side_effect.find ("now") != -1:
                delune.close (alias)
                return was.response.API ("204 No Content")
            return was.response.API ("202 Accepted")            
        
        if was.request.method == "POST" and delune.get (alias):
            return was.response.Fault ("406 Conflict", 40601, "resource already exists")
        elif was.request.method in ("PUT", "PATCH") and not delune.get (alias):
            return was.response.Fault ("404 Not Found", 40401, "resource not exist")
    
        if was.request.method == "PATCH":
            with open (fn) as f:
                config = json.load (f)
            data = was.request.JSON
            section = data ["section"]            
            for k, v in data ["data"].items ():
                if k not in config [section]:
                    return was.response.Fault ("400 Bad Request", 40001, "{} is not propety of {}".format (k, section))
                config [section][k] = v                
        else:
            config = was.request.JSON
        
        with open (fn, "w") as f:
            json.dump (config, f)
                                    
        was.setlu (delune.SIG_UPD)        
        if was.request.method == "POST":
            if side_effect == "now":
                api.load_data (alias, app.config.numthreads, was.plock)
                return was.response.API ("201 Created", **config)
            return was.response.API ("202 Accepted", **config)
        return was.response.API (**config)

    