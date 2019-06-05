from rs4 import siesta
from . import local
from rs4 import logger
import time

class ReponseError (Exception):
    pass
    
def make_api (point):
    if not isinstance (point, str):
        return point
    else:
        return siesta.API (point, reraise_http_error = False)
    
def assert_or_raise (r, expect):
    if r.status_code != expect:
        raise ReponseError (r)
    return r
    
class Documents (local.Documents):
    def __init__ (self, name, addr, logger):
        self.addr = addr
        self.logger = logger
        self.api = make_api (self.addr)
        self.name = name
        self.counts = [0, 0]
    
    def __enter__ (self):
        return self
    
    def __exit__ (self, type, value, tb):
        pass
            
    def add (self, doc):
        if doc._id:
            return self.update (doc)
        #self.logger ("#{} add document".format (self.counts [0]), "info", self.name)
        self.counts [0] += 1
        r = self.api.cols (self.name).documents.post (doc.as_dict ())
        return assert_or_raise (r, 202)        
    
    def update (self, doc):
        assert doc._id, "_id required"
        #self.logger ("#{} upsert document ({})".format (self.counts [0], doc._id), "info", self.name)
        self.counts [0] += 1
        r = self.api.cols (self.name).documents (doc._id).put (doc.as_dict ())
        return assert_or_raise (r, 202)        
    
    def delete (self, id):
        #self.logger ("#{} delete document ({})".format (self.counts [1], id), "info", self.name)
        self.counts [1] += 1
        r = self.api.cols (self.name).documents (id).delete ()
        return assert_or_raise (r, 202)
    
    def qdelete (self, q, lang = "en", analyze = 1):
        r = self.api.cols (self.name).documents.delete (q = q, lang = lang, analyze = analyze)
        return assert_or_raise (r, 202)        
    
    def truncate (self, name):
        r = self.api.cols (self.name).documents.delete (truncate_confirm = name)
        return assert_or_raise (r, 202)
    
    def search (self, q, **karg):
        r = self.api.cols (self.name).documents.get (q = q, **karg)
        return assert_or_raise (r, 200).data
    
    def get (self, id, **karg):
        r = self.api.cols (self.name).documents.get (q = "_id:{}".format (id), **karg)
        return assert_or_raise (r, 200).data
    
    
class Collection (local.Collection):
    def __init__ (self, name, config, addr, logger = None):
        self.addr = addr
        self.logger = logger
        self.api = make_api (self.addr)
        self.name = name
        self.config = config
        self.documents = Documents (self.name, self.addr, logger)
    
    def _wait (self, flag = True):
        for i in range (60):
            if self.is_active () is flag:
                return True
            else:
                time.sleep (1)
        return False        
    
    def close (self):
        pass
            
    def is_active (self):
        return self.name in self.api.cols.get_ ().data ["collections"]
    
    def save (self):
        r = self.api.cols (self.name).put (self.config)        
        return assert_or_raise (r, 200)
            
    def commit (self):
        r = self.api.cols (self.name).commit.post ({})
        return assert_or_raise (r, 205)
    
    def rollback (self):
        r = self.api.cols (self.name).rollback.post ({})
        return assert_or_raise (r, 205)
            
    def drop (self, include_date = False):
        if not self.is_active ():
            return
        if include_date:
            r = self.api.cols (self.name).delete (side_effect = 'data')
        else:
            r = self.api.cols (self.name).delete ()
        assert_or_raise (r, 202)
        self._wait (False)
        return r
    
    
class Delune:
    def __init__ (self, addr):
        self.addr = addr
        self.logger = logger.screen_logger ()
        self.api = make_api (self.addr)
                 
    def lscol (self):
        r = self.api.cols.get_ ()
        assert_or_raise (r, 200)
        return r.data ["collections"]
    
    def load (self, name):
        if name not in self.lscol ():
            raise NameError ("collection not found")
        r = self.api.cols (name).config.get ()
        assert_or_raise (r, 200)
        config = r.data            
        return Collection (name, config, self.addr, self.logger)
    
    def create (self, name, data_dirs, version = 1, **kargs):
        if name in self.lscol ():
            raise NameError ("collection exists") 
        config = local.make_config (name, data_dirs, version, **kargs)
        r = self.api.cols (name).post (config)
        assert_or_raise (r, 202)        
        col = Collection (name, config, self.addr, self.logger)
        assert col._wait (), "Collection creating timeout"
        return col
        
    