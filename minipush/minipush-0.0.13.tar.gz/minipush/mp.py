from .push import *
from .conf import config
class Minipush:
    def __init__(self, *args, **kwargs):
        self.cssmin=cssmin
        self.jsmin=jsmin
        self.config=config(*args, **kwargs)
    def run(self):
        log("Running Minipush...")
        t0=time.time()
        scripts={"js": {}, "css": {}}
        cfiles={}
        cpath=None
        o=get_origins(self.config["origin"]["folders"], ["js", "css"])
        osize=len(o)
        if cache_status(self.config):
            cfiles=get_cached_files(self.config["cache"]["folder"])
            cpath=self.config["cache"]["folder"]
        l=[]
        n=1
        for _ in o:
            m=min(_, cfiles, cpath, f"[{n}/{osize}]\t")
            n+=1
            l.append(m)
            if m["status"]=="success":
                if m["type"]=="js":
                    scripts["js"][_]=m["result"]
                if m["type"]=="css":
                    scripts["css"][_]=m["result"]
        templates_list=edit_templates(self.config["destination"]["folder"], self.config["destination"]["exts"], scripts, self.config)
        if export_status(self.config): export(scripts, self.config["export"]["rules"], self.config["format"]["export"])
        if cache_status(self.config): export_cache(l, self.config)
        log(f"Minipush ended in {round(time.time()-t0, 3)}seconds.")
        return {
            "stats": {
                "origins": lenext(o),
                "templates": len(templates_list),
                "dur": round(time.time()-t0, 3)
            },
            "origins": o,
            "templates": templates_list
        }
    def clear(self):
        edit_templates(self.config["destination"]["folder"], self.config["destination"]["exts"], {"js": {}, "css": {}}, self.config)
    def __str__(self):
        return f"<Minipush>"
    def __repr__(self):
        return f"<Minipush>"
