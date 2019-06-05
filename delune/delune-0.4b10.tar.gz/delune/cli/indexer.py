import delune
from delune import binfile
import queue
from delune.searcher.indexer import ExitNow
from rs4 import pathtool
import os, glob, json
import getopt, sys, time
from rs4.psutil import service, daemon_class
import threading
import shutil
from delune.fields import *

class	Indexer (daemon_class.DaemonClass):
	NAME = "indexer"

	def __init__ (self, logpath, varpath, consol, config):
		self.config = config
		self.lock = threading.RLock ()
		self.enter_shutdown = False
		self.q = queue.Queue ()
		self.working = {}
		self.ts = []
		daemon_class.DaemonClass.__init__ (self, logpath, varpath, consol)
	
	def add_document (self, indexer, doc):
		if self.enter_shutdown:
			raise daemon_class.ExitNow
				
		document = delune.document ()	
		document.set_contents (doc ['contents'])
		if 'snippet' in doc and doc ['snippet']:		
			document.set_snippet (*tuple (doc ['snippet']))
	
		for name, opt in doc ['fields'].items ():
			if name == "_id":			
				data = str (opt)
				lang = 'un'
				ftype = STRING
				option = []
				
			else:	
				data = opt.get ('data')
				if type (data) is str and data.startswith ("$content"):
					tree = data.split (".")
					if tree [0][9:] == "":
						index = 0
					else:	
						try: index = int (tree [0][9:])
						except ValueError: 
							raise TypeError ("Content index is wrong")
							
					val = doc ['contents'][index]
					for dep in tree [1:]:
						if type (val) is dict:
							val = val.get (dep)
						else:
							try: val = val [int (dep)]
							except IndexError: val = None															
						if not val:
							break
					data = val
										
				ftype = opt.get ('type')
				if not ftype:
					raise TypeError ('Type of field is required')
				option = opt.get ('option', [])				
				lang = opt.get ('lang', 'un')
				
			document.add_field (name, data, ftype, lang, option = option)
		indexer.add_document (document)
	
	def getdir (self, *d):
		return os.path.join (self.config ["resource_dir"], "delune", *d)
	
	def delete (self, alias, col, opt, deletables):
		opt ['searcher']['remove_segment'] = 0
		searcher = col.get_deletable_searcher (**opt ['searcher'])
		if searcher.si.getN () == 0:
			searcher.close ()
			return 0
		
		deleted = 0
		for qs in deletables:
			deleted += searcher.delete (**qs)
			
		searcher.commit ()	
		searcher.close ()	
		self.log ('deleted %d documents' % deleted, "info", alias)	
		return deleted
			
	def index_collection (self, alias, colopt, col):
		queue_dir = colopt ['data_dir']
		if type (queue_dir) is list:
			queue_dir = queue_dir [0]
		
		queue_dir = os.path.join (queue_dir, ".que")
		queues = [(os.path.basename (q), os.path.getmtime (q)) for q in glob.glob (os.path.join (queue_dir, 'que.*')) if not q.endswith (".lock")]
		
		if not queues:
			return
				
		self.log ("indexing start", "echo", alias)
		# reverse sort for trucate
		queues.sort (key = lambda x: x [-1], reverse = True)
		index = 0
		for gfile, mtime in queues:
			if gfile == "que.truncate":
				break
			index += 1
		
		if index < len (queues):
			self.log ("found trcuate request", "info", alias)
			for qfile, mtime in queues [index:]:
				os.remove (os.path.join (queue_dir, qfile))
			queues = queues [:index]
			indexer = col.get_indexer (**colopt ['indexer'])
			indexer.truncate ()	
			indexer.close ()
		
		deleted = 0
		deletables = []
		ensure_latest = {}
		deleted_qss = set ()
		# resort from old one
		for qfile, mtime in queues:
			ensure_latest_ = {}
			bf = binfile.BinFile (os.path.join (queue_dir, qfile), "r")
			idx = -1
			while 1:
				idx += 1
				try: 
					cmd = bf.readVInt ()
				except OSError:
					bf.close ()
					break
				try:
					doc = json.loads (bf.readZBytes ().decode ("utf8"))
				except (OSError, MemoryError):
					bf.close ()
					break
				
				if cmd == 1:
					qs = doc.get ("query")
					if qs ["qs"] in deleted_qss:
						continue
					deleted_qss.add (qs ["qs"])
					
					deletables.append (qs)	
					if len (deletables)	== 10000:
						# too many, commit forcely
						deleted += self.delete (alias, col, colopt, deletables)
						deletables = []
				else:
					_id = doc ["fields"].get ("_id")					
					if _id:
						ensure_latest_ [_id] = (qfile, idx)										
							
			for _id in ensure_latest_:
				if _id in ensure_latest:
					continue
				ensure_latest [_id] = ensure_latest_ [_id]
		
		queues.reverse () # IMP: resort by origin
		if deletables:
			deleted += self.delete (alias, col, colopt, deletables)
			
		if deleted:	
			self.log ('deleted total %d documents' % deleted, "info", alias)
			colopt ['indexer']["optimize"] = 1
			colopt ['indexer']["force_merge"] = 1			
		indexer = col.get_indexer (**colopt ['indexer'])	
		# mannual commit mode, ignore memory usage
		indexer.set_autocommit (False)
		
		total_indexed_docs = 0
		indexed_docs = 0
		indexed_ques = []
		for qfile, mtime in queues:
			bf = binfile.BinFile (os.path.join (queue_dir, qfile), "r")
			ndoc = 0
			idx = -1
			while 1:
				idx += 1
				try: cmd = bf.readVInt ()				
				except OSError:
					bf.close ()
					break
				
				if cmd == 1:	 # just delete
					bf.readZBytes ()
					continue
				
				try:
					doc = json.loads (bf.readZBytes ().decode ("utf8"))				
				except (OSError, MemoryError):
					bf.close ()
					break
				
				_id = doc ["fields"].get ("_id")
				if _id and ensure_latest [_id] != (qfile, idx):
					# IMP: not recent document, skip
					continue
					
				self.add_document (indexer, doc)
				indexed_docs += 1
				ndoc += 1
				
			self.log ('added %d documents from %s' % (ndoc, qfile), "info", alias)
			indexed_ques.append (os.path.join (queue_dir, qfile))
			if self.maybe_commit (alias, indexer, indexed_ques, indexed_docs):
				total_indexed_docs += indexed_docs
				indexed_docs = 0
				indexed_ques = []
	
		self.maybe_commit (alias, indexer, indexed_ques, indexed_docs, force = True)
		if indexed_docs:
			total_indexed_docs += indexed_docs 
			self.log ('added total %d documents added' % total_indexed_docs, "info", alias)	
		indexer.close (optimize = deleted > 100)
	
	def maybe_commit (self, alias, indexer, indexed_ques, indexed_docs, force = False):
		if force or indexer.is_memory_over ():
			# commit and delete queue for preventing duplication		
			if indexed_docs:
				indexer.commit ()
			for qpath in indexed_ques:
				self.log ('remove indexed que %s' % os.path.basename (qpath), "info", alias)
				os.remove (qpath)
			return 1
		return 0
	
	def index (self):
		while 1:
			alias = self.q.get ()
			if not alias: return
			if self.enter_shutdown: return	
			with self.lock: self.working [alias] = None
			self.log ("checking...", "echo", alias)
			col = None
			try:
				path = self.getdir ("config", alias)
				if alias [0] in "#-":
					continue
				with open (path, "r") as f:
					colopt = json.loads (f.read ())				
				if colopt.get ("version", 1) == 0 or "ro" in colopt.get ("permission", []):
					self.log ("read only collection, skip", "info", alias)
					continue
						
				colopt ['data_dir'] = [self.getdir ("collections", os.path.normpath(d)) for d in colopt ['data_dir']]
				
				max_terms = colopt ['analyzer'].pop ("max_terms")
				col = delune.collection (
				  indexdir = colopt ['data_dir'],
				  mode = delune.APPEND,
				  analyzer = delune.standard_analyzer (max_terms, 1, **colopt ['analyzer']),
				  version = colopt.get ("version", 1)
				)				
				if col.lock.isplocked ("replicate"):
					self.log ("on replicating, maybe next", "warn", alias)
					continue
				self.index_collection (alias, colopt, col)
				col.removeDeletables ()
				
			except Exception as why:				
				if not isinstance (why, daemon_class.ExitNow):
					self.trace ()
			
			with self.lock: del self.working [alias]
			if self.enter_shutdown: return
	
	def shutdown (self, signum):
		self.log ("got signal {}, entering shutdown process...".format (signum), "echo")		 	
		self.enter_shutdown = True
		for i in range (self.config.get ("threads", 1) * 3):
			self.q.put (None)
					
	def setup (self):		
		delune.configure (self.config.get ("threads", 1), self.logger)
		
	def wait_for_interval (self):
		interval = self.config.get ("interval", 0)		
		if interval == 0:
			return False
		for i in range (interval):
			if self.enter_shutdown:
				return False
			time.sleep (1)
		return True
	
	def maintern (self, config_dir):
		collections_dir = os.path.join (os.path.dirname (config_dir), "collections")
		for alias in os.listdir (config_dir):
			if alias [0] not in "-":
				continue
			self.log ("removing local collection", 'warn', alias)
			config_path = self.getdir ("config", alias)
			with open (config_path) as f:
				colopt = json.loads (f.read ())
			for each in [os.path.join (collections_dir, os.path.normpath(d)) for d in colopt ['data_dir']]:
				if os.path.isdir (each):
					shutil.rmtree (each)
			os.remove (config_path)	
			self.log ("local collection has been removed", 'warn', alias)
					
	def threading (self, func):
		self.ts = []
		for i in range (self.config.get ("threads", 1)):	
			t = threading.Thread (target = func)
			self.ts.append (t)
			t.start ()
		
	def reque (self, aliases):		
		if not self.q.empty ():
			return
		for alias in aliases:
			if [ex for ex in self.config.get ("exclude", []) if alias.startswith (ex)]:
				continue
			with self.lock:
				if alias in self.working:
					continue
			self.q.put (alias)
		
		if self.config.get ("interval", 0) == 0:
			for t in self.ts:
				self.q.put (None)
				t.join ()
	
	def run (self):
		pathtool.mkdir (self.getdir ("config"))
		if self.config.get ("threads", 1) == 0:
			self.reque (os.listdir (self.getdir ("config")))
			self.q.put (None)
			return self.index ()
		
		self.threading (self.index)
		while 1:	
			self.maintern (self.getdir ("config")) 
			self.reque (os.listdir (self.getdir ("config")))		
			if not self.wait_for_interval ():
				break
				

def usage ():
	print ("""usage: 
  delune index [options] [start|stop|status|restart]

options:
  -d: daemonize
  -e, --exclude: <alias,...>
  -v, --resource-dir: <resource-dir>
  -i, --interval: <int> interval seconds 
  -t, --threads: <int> 
      --help 

example:
  delune index -i 300 -vs /home/ubuntu/deluned/resource
	""")
	sys.exit ()

def remove_end_slash (url):
	while url:
		if url [-1] != "/":
			return url
		url = url [:-1]	
		
def parse_argv (sopts, lopts, usage_): 
	argopt = getopt.getopt(sys.argv[1:], sopts, lopts)
	
	config = {}
	try: cmd = argopt [1][0]
	except: cmd = None
	for k, v in argopt [0]:
		if k == "-o" or k == "--origin":
			config ["origin"] = remove_end_slash (v)
		elif k == "-v" or k == "--resource-dir":
			config ["resource_dir"] = v
		elif k == "--help":
			usage_ ()	
		elif k == "-t" or k == "--threads":
			config ["threads"] = int (v)
		elif k == "-e" or k == "--exclude":
			config ["exclude"] = [each.strip () for each in v.split (",")]	
		elif k == "-i" or k == "--interval":
			config ["interval"] = int (v)
		elif k == "-d":
			cmd = "start"
	return cmd, config, not cmd	

VARPATH = "/var/tmp/delune/indexer"
LOGPATH = "/var/log/delune/indexer"

def index (model_root):
	f = Indexer (os.path.isdir (LOGPATH) and LOGPATH or None, VARPATH, True, {"threads": 0, "resource_dir": model_root})
	f.start ()	

def main ():
	cmd, config, console = parse_argv ("dv:o:t:i:e:", ["exclude=", "origin=", "threads=", "interval=", "resource-dir", "help"], usage)
	if not cmd or cmd in ("start", "restart"):
		assert "resource_dir" in config, "resource root required"
	assert "origin" not in config, "invalid option: origin"
		
	pathtool.mkdir (VARPATH)
	servicer = service.Service ("delune/{}".format (Indexer.NAME), VARPATH)
	if cmd and not servicer.execute (cmd):
		return
	if console and servicer.status (False):
		raise SystemError ("daemon is running")
	
	s = Indexer (LOGPATH, VARPATH, console, config)
	s.start ()	
	
if __name__ == "__main__":
	main ()

