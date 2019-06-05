import json
import os
import shutil
import delune
from delune import docqueue
import copy
import threading
from rs4 import logger, pathtool
from . import indexer
from rs4.psutil import plock as _plock
        
OPT_TEMPLATE = {
  "version": 1,
  'name': None,
  'data_dir': [],
  "permission": [],
  'analyzer': {
    "max_terms": 3000,
    "stem_level": 1,
    "strip_html": 0,
    "make_lower_case": 1,
    "ngram": 1,
    "biword": 0,
    "stopwords_case_sensitive": 1,
    "ngram_no_space": 0,    
    "contains_alpha_only": 0,
    "stopwords": [],
    "endwords": [],    
  },
  'indexer': {
    'optimize': 1,
    'force_merge': 0,
    'max_memory': 10000000,
    'max_segments': 10,
    'lazy_merge': (0.3, 0.5),
  },
  'searcher': {
    'max_result': 2000,
    'num_query_cache': 1000
  }
}

def make_config (name, data_dirs = [], version = 1, **kargs):
    config = copy.copy (OPT_TEMPLATE)
    config ["name"] = name
    config ["version"] = version
    if not data_dirs:
        config ["data_dir"] = [name]
    else:
        config ["data_dir"] = []
        if isinstance (data_dirs, str):
            data_dirs = [data_dirs]
        for each in data_dirs:
            config ["data_dir"].append (each)

    for k, v in kargs.items ():
        gotit = False
        for sect in ("analyzer", "indexer", "searcher"):
            if k in config [sect]:
                config [sect][k] = v
                gotit = True
        if not gotit:
            raise NameError ("option `{} = {}` is not recognized".format (k, v))
    return config
      
      
class Documents:
    def __init__ (self, queue, config, model_root, logger):
        self.queue = queue
        self.config = config
        self.logger = logger
        self.model_root = model_root
        self.searcher = None
        self.lock = threading.RLock ()
        
    def __enter__ (self):
        return self
    
    def __exit__ (self, type, value, tb):
        self.close_searcher ()
        
    def close_searcher (self):
         if self.searcher:
            self.searcher.close ()
            self.searcher = None
                   
    def create_searcher (self):
        with self.lock:
            if self.searcher:
                return
            self.queue.si.read ()                
            self.config ["searcher"]["num_query_cache"] = 0 # disable caching
            self.searcher = self.queue.si.get_searcher (**self.config ["searcher"])        
         
    def new (self, id = None, analyzer = None):
        return delune.document (id, analyzer)
    
    def add (self, doc):
        if doc._id:
            self.update (doc)
        else:
            self.queue (0, doc.as_json ())
        
    def update (self, doc):
        assert doc._id, "_id required"
        self.delete (doc._id)
        self.queue (0, doc.as_json ())
    
    def delete (self, id):
        self.queue (1, json.dumps ({"query": {'qs': "_id:" + id}}))
    
    def qdelete (self, qs, lang = "en", analyze = 1):
        self.queue (1, json.dumps ({"query": {'qs': qs, 'lang': lang, 'analyze': analyze}}))
    
    def truncate (self, name):
        if self.searcher:
            self.searcher.close ()    
            self.searcher = None
        self.queue.truncate ()
    
    def get (self, id, snippet = 30, partial = "", nth_content = 0, lang = "en", analyze = 1, data = 1, qlimit = 1, *arg, **karg):
        return self.search ("_id:{}".format (id), 0, 1, "", snippet, partial, nth_content, lang, analyze, data, qlimit, *arg, **karg)
    
    def search (self, q, offset = 0, limit = 10, sort = "", snippet = 30, partial = "", nth_content = 0, lang = "en", analyze = 1, data = 1, qlimit = 1, *arg, **karg):
        self.create_searcher ()
        return self.searcher.query (q, offset, limit, sort, snippet, partial, nth_content, lang, analyze, data, qlimit, *arg, **karg)
        

class Collection:
    def __init__ (self, name, config, model_root, logger = None):
        self.name = name
        self.config = config
        self.model_root = model_root        
        self.logger = logger   
        self.__create_queue ()
        self.documents = Documents (self.queue, self.config, self.model_root, self.logger)     
    
    @property
    def config_file (self):
        return os.path.join (self.model_root, "delune", "config", self.name)
    
    @property
    def data_dir (self):
        return [os.path.join (self.model_root, "delune", "collections", each) for each in self.config ['data_dir']]
    
    def __create_queue (self):
        opts = copy.copy (self.config ['analyzer'])
        max_terms = opts.pop ("max_terms")
        self.si = delune.collection (
          indexdir = self.data_dir,
          mode = delune.READ,
          analyzer = delune.standard_analyzer (max_terms, 1, **opts),
          version = self.config ['version']
        )        
        self.queue = docqueue.DocQueue (self.si)
    
    def setopt (self, sect, **kargs):
        for k, v in kargs.items ():
            self.config [sect][k] = v
        self.save ()
    
    def save (self):
        with open (self.config_file, "w") as f:
            f.write (json.dumps (self.config))
        
    def close (self):
        if  self.queue is None:
            return
        if self.documents.searcher:
            self.documents.searcher.close ()
            self.documents.searcher = None
        self.queue.close (1)
        self.queue = None
        self.si.close ()
    
    def is_active (self):
        return os.path.isfile (self.config_file)
    
    def commit (self):
        self.queue.commit ()
        self.documents.close_searcher ()
        
    def rollback (self):
        self.queue.rollback ()
    
    def drop (self, include_data = False):
        self.close ()
        if os.path.isfile (self.config_file):
            os.remove (self.config_file)
            
        if include_data:
            for d in self.data_dir:
                shutil.rmtree (d)
    

class Delune:
    def __init__ (self, model_root):
        self.model_root = model_root
        self.logger = logger.screen_logger ()
        delune.configure (1, self.logger)
        pathtool.mkdir (self.getdir ("config"))
        pathtool.mkdir (self.getdir ("collections"))
    
    def getdir (self, *d):
        return os.path.join (self.model_root, "delune", *d)
        
    def lscol (self):
        cols = []
        for each in os.listdir (self.getdir ("config")):
            cols.append (each)
        return cols
        
    def load (self, name):
        if name not in self.lscol ():
            raise NameError ("collection not found")        
        with open (os.path.join (self.getdir ("config", name))) as f:
            config = json.loads (f.read ())            
        return Collection (name, config, self.model_root, self.logger)
    
    def create (self, name, data_dirs = [], version = 1, **kargs):
        if name in self.lscol ():
             raise NameError ("collection exists")
        config = make_config (name, data_dirs, version, **kargs)        
        return Collection (name, config, self.model_root, self.logger)

    def index (self):
        indexer.index (self.model_root)        
        