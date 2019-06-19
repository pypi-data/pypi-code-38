__doc__=f"""mrldb by Rémi "Mr e-RL" LANGDORPH
Copyright (c) 2019 Rémi LANGDORPH - mrerl@warlegend.net
under MIT License (https://github.com/merlleu/mrldb/blob/master/LICENSE)"""
__all__=["MrlDBCluster", "mdbcl"]

_cluster={"main": None}
class MrlDBCluster:
    def __init__(self):
        self.dbs={}
        self.aliases={}
        _cluster["main"]=self
    def get(self, name):
        return self.dbs[self.aliases[name]]
    def add(self, name, db, aliases=[]):
        self.dbs[name]=db
        self.aliases[name]=name
        for alias in aliases: self.aliases[alias]=name
        return name
    def addalias(self, name, aliases):
        if isinstance(aliases, str):
            self.aliases[aliases]=name
        else:
            for alias in aliases: self.aliases[alias]=name
        return name
    def get_cluster_infos(self):
        return {
        name: db._getinfos() for name, db in self.dbs.items()
        }
    def __iter__(self):
        return self.dbs.items().__iter__()
    def __getitem__(self, key):
        return self.dbs[self.aliases[key]]
    def __str__(self):
        return f"<mrldb.MrlDBCluster at {id(self)} - {len(self.dbs)} connection(s)>"
    def __repr__(self):
        return f"<mrldb.MrlDBCluster at {id(self)} - {len(self.dbs)} connection(s)>"
mdbcl=None
try:
    from werkzeug.local import LocalProxy
    mdbcl=LocalProxy(lambda: _cluster["main"])
except: pass
