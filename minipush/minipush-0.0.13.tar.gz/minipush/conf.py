from .default_config import default_config
import json
class config(dict):
    def __init__(self, *args, **kwargs):
        self.change_self(default_config)
        self.edit(*args, **kwargs)
    def edit(self, origin_folders=None,
                    destination_folder=None, destination_exts=None, destination_type=None, destination_bfl=None,
                    export_enabled=None, export_rules=None,
                    anchors=None,
                    formats=None,
                    cache_folder=None, cache_enabled=None,
                    file=None, dic=None,
                    app=None, #For flask support (not usefull yet :/)
                    *args, **kwargs
                    ):
        if origin_folders!=None: self["origin"]["folders"]=list(origin_folders)
        if destination_folder!=None: self["destination"]["folder"]=str(destination_folder)
        if destination_exts!=None: self["destination"]["exts"]=list(destination_exts)
        if destination_type!=None: self["destination"]["type"]=str(destination_type)
        if destination_bfl!=None: self["destination"]["basefolderlink"]=str(destination_bfl)
        if export_enabled!=None: self["export"]["enabled"]=export_enabled
        if export_rules!=None: self["export"]["rules"]=dict(export_rules)
        if anchors!=None: self["anchors"]=dict(anchors)
        if formats!=None: self["formats"]=dict(formats)
        if cache_folder!=None: self["cache"]["folder"]=str(cache_folder)
        if cache_enabled!=None: self["cache"]["enabled"]=cache_enabled
        if file!=None:
            if isinstance(file, str): self.change_self(json.loads(open(file).read()))
            else: self.change_self(json.loads(file.read()))
        if dic!=None:
            if isinstance(dic, str): self.change_self(json.loads(dic))
            elif isinstance(dic, dict): self.change_self(dic)
            else: self.change_self(json.loads(dic))
    def __str__(self):
        return f"<Minipush Config: {dict(self)}>"
    def __repr__(self):
        return f"<Minipush Config: {dict(self)}>"
    def change_self(self, dic):
        for k, v in dic.items():
            self[k]=v
