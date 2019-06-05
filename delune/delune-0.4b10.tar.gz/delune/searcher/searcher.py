import os
import threading
import time
import types
import sys
from .. import _delune, memory
from .segment import segmentreaders
from . import query, cache, fetcher
import delune
from delune import binfile, docqueue
from rs4 import unistr
from delune import filesystem

class Searcher:
	MAINTERN_INTERVAL = 60
	
	def __init__ (self, si, do_init = True):
		self.si = si
		
		# default opt
		self.maxResult = self.si.getopt (max_result = 2000)
		self.numQueryCache = self.si.getopt (num_query_cache = 200)		
		self.estTotal = 0		
		self.numquery = 0
		self.segments = segmentreaders.SegmentReaders (self.si)
		
		self.references = 0
		self.shutdown_level = 0
		self.maintern_time = -1
		self.closed = 1
		self.clean = 0
		self.cond = threading.Condition ()
		self.mutex = threading.Lock ()
		self.cache = cache.Cache (self.numQueryCache)
		self.mod_time = self.si.getModfiedTime ()
		self.queue = None
		self._initiallized = False		
		
		if do_init: 
			self.init ()
	
	def create_queue (self):		
		self.queue = docqueue.DocQueue (self.si)
		
	def init (self):
		self.si.log ("initializing `%s'" % self.si.getAlias ())				
		success = self.do_refresh ()
		if not success:
			self.si.log ("initializing failed `%s'" % self.si.getAlias (), "fail")
		else:	
			self.si.log ("initialized `%s' %s" % (self.si.getAlias (), self.si.getSegmentList ()))
		self._initiallized = True
		return success

	#-----------------------------------------------------------------------------------------
	# maintern functions
	#-----------------------------------------------------------------------------------------
	def ismainternable (self):
		if self.si.lock.islocked ("merge"):
			return 0
		if self.si.lock.isplocked ("duplicate"):
			return 0			
		return 1

	def maintern (self):
		if time.time () - self.maintern_time > self.MAINTERN_INTERVAL and self.ismainternable ():
			self.maintern_time = time.time ()
			if self.need_refresh ():
				self.si.log ("refreshing `%s'" % self.si.getAlias ())				
				self.do_refresh ()
			else:				
				self.segments.reload_deleted ()

	def increference (self):
		self.cond.acquire ()
		while self.shutdown_level == 1: self.cond.wait () #single job working, wait...

		# already shutdowned
		if self.shutdown_level == 2:
			self.cond.release ()
			return 0

		if not self.references:			
			try:				
				self.maintern ()
			except MemoryError:
				raise
			except:
				self.si.trace ()

		self.references += 1
		self.cond.release ()
		return 1

	def decreference (self):
		self.cond.acquire ()
		self.references -= 1
		self.numquery += 1
		self.cond.notifyAll ()
		self.cond.release ()
	
	def need_refresh (self):
		mod_time = self.si.getModfiedTime ()		
		if mod_time == -1: # maybe renaming or no segments
			self.clean = 0
			return 0
		
		if self.clean and mod_time == self.mod_time:
			return 0 # not changed
		
		self.si.read () # refreshing new segment infos
		return 1
			
	#-----------------------------------------------------------------------------------------
	# job frameowork
	#-----------------------------------------------------------------------------------------
	def single_job (self, func, levelto, *arg, **karg):
		self.cond.acquire ()
		self.shutdown_level = 1
		while self.references: self.cond.wait () #under using, wait...

		retval = 0
		if self.shutdown_level == 2:
			self.cond.notifyAll ()
			self.cond.release ()
			return 0

		try:
			try: retval = func (*arg, **karg)
			finally: self.shutdown_level = levelto

		except MemoryError:
			self.si.trace ()
			self.cond.notifyAll ()
			self.cond.release ()
			raise

		except:
			self.si.trace ()

		self.cond.notifyAll ()
		self.cond.release ()

		return retval

	def multi_job (self, func, default, *arg, **karg):
		if not self.increference ():
			return [510, 0, 0, []]  #shutdown step or MemroyError

		try:
			try:
				res = func (*arg, **karg)
			finally:
				self.decreference ()

		except MemoryError:
			raise

		except:
			self.si.trace ()
			return default

		else:
			return res

	#-----------------------------------------------------------------------------------------
	# real functions
	#-----------------------------------------------------------------------------------------
	def do_status (self, *arg, **karg):
		segmentinfos = [(x.seg, x.getNumDoc (), x.getDeletedCount (), x.ti.numterm, x.get_delfile_modtime ()) for x in self.segments]
		locks, note = self.si.lock.locks ()
		
		return {
			"version": self.si.version,			
			"lastupdated": max (self.mod_time, segmentinfos and max ([x [-1] for x in segmentinfos]) or 0.),
			"indexdirs": self.si.indexdir,
			"segmentfiles": {"primary": filesystem.get_segment_files (self.si.indexdir)},
			"numquery": self.numquery,
			"N": self.si.getN (),
			"segmentinfos": segmentinfos,
			"segmentsizes": self.si.fs.dirinfo (),
			"locks": locks,
			"note": note,
			# IMP: replicator need current segments modtime
			"segments": (self.si.getSegmentsPath (), self.mod_time)
		}

	def do_remove (self, segs):
		self.segments.remove (segs)
		
	def do_refresh (self, *arg, **karg):
		self.clean = 1
		if self.si.getModfiedTime () == -1:			
			self.clean = 0
			return 1
			
		try:
			self.segments.load ()

		except:
			# if failed, loading next time
			self.si.trace ()
			self.clean = 0
			return 0
		
		self.cache.clear ()
		self.closed = 0
		self.mod_time = self.si.getModfiedTime ()

		return 1

	def do_close (self, *arg, **karg):
		if self.closed: return 1		
		self.segments.close ()
		self.si.close ()
		self.si = None
		self.closed = 1
		return 1
		
	def do_query (self, qs, offset = 0, fetch = 10, sort = "", summary = 30, returns = "", nthdoc = 0, lang = "en", analyze = 1, data = 1, limit = 1, *arg, **karg):
		try:
			offset = int (offset)
			fetch = int (fetch)
			summary = int (summary)
			analyze = int (analyze)
			data = int (data)
			limit = int (limit)
			nthdoc = int (nthdoc)
			qs = unistr.makes (qs)
			
		except:
			#return [505, 0, 0, ""]
			return {"code": 501, "err": "Arguments Error", "total": 0}
		
		if not qs.strip ():
			return {"code": 502, "err": "No Keyword", "total": 0}
			#return [210, 0, 0, ""]
		if limit and self.maxResult and offset + fetch > self.maxResult: 
			return {"code": 503, "err": "Exceed Limit", "total": 0}

		#print ("#############", qs)
		#if isinstance (qs, str): 
		#	qs = qs.encode ("utf8")

		cachekey = (qs, lang, sort)
		cached = self.cache.get (cachekey)
		
		result = {"code": 200, "time": 0, "total": 0}
		if cached and (len (cached [-1]) >= offset + fetch or len (cached [-1]) == cached [0]):
			totalcount, sortindex, sortorder, highlights, bucket = cached
			result ["msg"] = "Hit Cache"
			result ["total"] = totalcount
			result ["regex"] = query.makeHighLightRE (highlights)
			result ["sorted"] = [sortindex, sortorder]
			result ["time"] = 0.0
			if data:
				result ["result"] = self.do_fetch (bucket  [offset:offset + fetch], summary, highlights, returns, nthdoc)								
			else:
				result ["result"] = bucket  [offset:offset + fetch]
			return result			
		
		q = query.Query (self.segments, qs, lang, offset, fetch, sort, analyze and self.si.analyzer or None, self.estTotal)
		try:
			q.query ()			
			result ["total"] = q.totalcount		
			result ["regex"] = query.makeHighLightRE (q.highlights)
			result ["time"] = q.duration
			result ["sorted"] = [q.sortindex, q.sortorder]
									
			if data:
				result ["result"] = self.do_fetch (q.bucket  [offset:offset + fetch], summary, list(q.highlights.keys ()), returns, nthdoc)
				#result = [200, q.duration, q.totalcount, query.makeHighLightRE (q.highlights)] + fetched
			else:
				result ["result"] = q.bucket  [offset:offset + fetch]				
				#result = [200, [q.sortindex, q.sortorder], q.totalcount, query.makeHighLightRE (q.highlights)] + fetched

			if offset == 0:
				self.cache.set (cachekey, (q.totalcount, q.sortindex, q.sortorder, list(q.highlights.keys ()), q.bucket [:100]))

			if q.esegments:
				self.do_remove (q.esegments)

		finally:
			q.close ()
			del q

		return result

	def do_fetch (self, bucket, summary, highlights, returns, nthdoc, *arg, **karg):
		f = fetcher.Fetcher (self.segments, bucket, summary, highlights, returns, nthdoc)		
		try:
			result = f.fetchall ()
		finally:			
			f.searcher = None			
			f.close ()		
		return result

	#-----------------------------------------------------------------------------------------
	# interface functions
	#-----------------------------------------------------------------------------------------
	def close (self, *arg, **karg):
		return self.single_job (self.do_close, 2, *arg, **karg)
		
	def refresh (self, *arg, **karg):
		self.si.read () # force refresh
		return self.single_job (self.do_refresh, 0, *arg, **karg)
	
	def status (self, *arg, **karg):
		default = {}
		return self.multi_job (self.do_status, default, *arg, **karg)

	def query (self, *arg, **karg):		
		default = {"code": 500, "err": "Default Error", "total": 0}
		return self.multi_job (self.do_query, default, *arg, **karg)

	def fetch (self, *arg, **karg):
		default = []
		return self.multi_job (self.do_fetch, default, *arg, **karg)
	
	def stem (self, q, lang = "en"):
		return self.si.analyzer.stem (q, lang)
	
	def analyze (self, q, lang = "en"):
		return self.si.analyzer.index (q, lang)


class DeletableSearcher (Searcher):	
	# make sure with single threads	
	def commit (self):
		try:			
			self.segments.commit ()
			self.cache.clear ()
		finally:
			self.si.fs.dirty ()
			
	def delete (self, qs, lang = "en", analyze = 1):
		# called by indexer, make sure it is in single thread
		try:
			result = self.do_query (qs, 0, 2000000000, "", 0, lang = lang, analyze = analyze, data = 0, limit = 0)
			if "result" in result:
				for record in result ["result"]:
					seg, docid, extra, score = record
					self.segments [seg].delete (int (docid))				
		except:
			self.si.trace ()
			raise
		return result ["total"]
	
	def close (self, *arg, **karg):
		return self.do_close ()


if __name__ == "__main__":
	from delune import indexinfo
	from rs4 import confparse, logger
	#from delune.searcher import memory
	import memory
	
	memory.create (1, 32768, 1024000, "segment", logger.screen_logger ())
	inf = indexinfo.IndexInfo (confparse.ConfParse (r"d:\bladepub\proto\etc\col\mailservice"))
	s = Searcher (inf)
	try:
		s.init ()
		print(s.query ("computer", 0, 0))

	finally:
		s.close ()
		

