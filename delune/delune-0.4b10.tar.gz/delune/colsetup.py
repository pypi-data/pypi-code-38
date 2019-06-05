import delune
from delune import memory
import os
import shutil
import time
import pickle as pickle
from . import filesystem
from rs4 import logger as logs
from rs4.psutil import plock as _plock
from rs4.psutil import flock
from rs4.psutil import processutil
import socket
from functools import reduce
import threading
if os.name == "nt":
	import win32process

class SwapError (Exception):
	pass

class Options:
	pass
	
class Segments:
	def __init__ (self, alias = "", version = None):
		self.alias = alias
		self.version = version
		self.N = 0
		self.segmentInfo = {}


class CollectionSetup:
	exts = []
	segment_class = Segments
	
	def __init__ (self, indexdir, mode = 'r', analyzer = None, logger = None, plock = None, ident = None, version = 1):
		self.indexdir = indexdir
		self.mode = mode
		self.analyzer = analyzer
		self.logger = logger
		self.ident = ident
		self.fs = filesystem.FileSystem (self.indexdir)
		self.master = self.fs.getmaster ()		
		self.lock = flock.Lock (self.master)		
		self.version = version
	
		self.plock = plock # inter process lock
		if self.plock is None:			
			self.plock = threading.RLock ()
		
		self.rebuild = False
		if mode == "c":
			self.rebuild = True
			self.mode = "w"
		
		self.initial_newseg = 0
		self.options = Options ()

		if self.hasSegmentsFile ():
			self.read ()
			if self.rebuild:
				self.createSegments ()
		else:
			self.createSegments ()
		
		self._logger_created = False
		self._analyzer_created = False
		self._delune_init = False		
		
		if not self.logger:
			self.logger = delune.logger
			if not self.logger:
				self.logger = logs.screen_logger ()
				self.log ("logger is not provided, screen logger created", "warn")
				self._logger_created = True
		
		if self.mode == "r" and memory.memory is None: 
			self.log ("delune not inited, forcely init for single thread", "warn")
			delune.configure (1, self.logger)
			self._delune_init = True
		
		if self.analyzer is None:
			self.analyzer = delune.standard_analyzer (self.mode == delune.READ and 32 or 3000)			
			if self.mode == delune.READ:
				self.analyzer.setopt (ngram_no_space = 0)			
			self._analyzer_created = True
		
		if self.mode == delune.READ: # for multi-thread
			self.analyzer = delune.qualify_analyzer (self.analyzer)
	
	def set_ident (self, ident):
		self.ident = ident
		
	def close (self):
		self.lock.unlock ("using-%s" % (delune.PID or os.getpid ()))			
		if self._delune_init:
			self.log ("shutdown delune...", "info")
			delune.shutdown ()
			self._delune_init = False
						
		if self._analyzer_created:
			self.log ("close analyzer...", "info")
			self.analyzer.close ()
			self._analyzer_created = False
			
		if self._logger_created:			
			self.log ("close logger...", "info")
			self.logger.close ()
			self._logger_created = False		
			
	def gtVersion (self):
		return self.segments.version
	
	def getMajorVersion (self):
		return int (self.segments.version.split (".") [0])
		
	def notify (self):
		ll = list(self.segments.segmentInfo.keys ())
		ll.sort ()
		self.log ("segments updated... %s" % ll)	
					
	def write (self, fn = "segments"):
		self.segments.N = reduce (lambda x, y: x + y, list(self.segments.segmentInfo.values ()))				
		self.segments.alias = self.alias
		t = open (os.path.join (self.master, fn), "wb")
		pickle.dump (self.segments, t)
		os.fsync(t.fileno ())
		t.close ()
		self.log ("total indexed docuemts are %d" % self.segments.N)
			
	def read (self, fn = "segments"):	
		t = open (os.path.join (self.master, fn), "rb")
		self.segments = pickle.load (t)		
		t.close ()
		self.alias = self.segments.alias
		
		if type (self.segments.version) is str:
			self.version = 0
		
		if self.ident is None:
			self.ident = self.alias
		
		if self.mode == "r":
			self.setReadingSegments ()
		elif self.version == 0:
			raise SystemError ("version 0 had been deprecated, you can only read collection")
		self.initial_newseg = max (self.segments.segmentInfo.keys ()) + 1			
		
	def flush (self, new = 1):		
		if new:			
			segment = self.write ("segments.new")
		else:
			segment = self.write ()

		if new:
			self.log ("replace segments.new...")
			try:
				self.replaceFile ("segments")
			except:
				self.trace ()		
			self.notify ()
					
		if self.mode == "w":			
			self.removeDeletables ()

	def riaseSwapError (self, msg):
		raise SwapError("%s %s" % (self.alias, msg))

	def replaceFile (self, name):
		backup = os.path.join (self.master, name + ".bak")
		newone = os.path.join (self.master, name + ".new")
		replacement = os.path.join (self.master, name)

		try:
			try:
				os.remove (backup)
			except OSError as why:
				if why.errno != 2:
					self.riaseSwapError ("backup file cannot deleted")

			try:
				os.rename (replacement, backup)
			except OSError as why:
				if why.errno != 2:
					self.riaseSwapError ("backup failed")

			try:
				os.rename (newone, replacement)
			except:
				self.trace ()
				os.rename (backup, replacement)
				self.riaseSwapError ("replace failed. rollbacked")

			else:
				try: os.remove (backup)
				except: pass

		except:
			self.trace ()
			raise

		else:
			self.read ()
	
	def removeDeletables (self):
		if self.lock.isplocked ("duplicate"):
			return
		all = self.fs.segments ()
		used = self.getReadingSegmentsAllProcesses () + self.getSegmentList ()
		for seg in all:
			if seg not in used:
				self.removeSegmentFile (seg)

	def removeSegment (self, seg):
		try:
			del self.segments.segmentInfo [int (seg)]
		except KeyError:
			pass
	
	def removeSegmentFile (self, seg):
		try:
			self.fs.remove (seg)
		except:
			self.log ("segment %s remove failed" % seg, "fail")
			return 0

		self.log ("segment %s removed" % seg)		
		return 1
	
	def getSegmentsPath (self):
		return os.path.join (self.master, "segments")
		
	def getModfiedTime (self):
		try:			
			return os.stat (self.getSegmentsPath ()).st_mtime
		except (IOError, OSError): # no index yet
			return -1

	def createSegments (self):
		alias = os.path.split (self.master) [-1]
		self.segments = self.segment_class (alias, self.version)
		self.alias = self.segments.alias
		if self.ident is None:
			self.ident = self.alias

	def log (self, msg, type = "info"):
		self.logger (msg, type, self.ident)

	def trace (self):
		return self.logger.trace (self.ident)

	def getSegmentList (self):
		return list(self.segments.segmentInfo.keys ())

	def getLastSegment (self):
		segs = list(self.segments.segmentInfo.keys ())
		segs.sort ()
		return segs [-1]
		
	def getSegmentInfo (self):
		return self.segments.segmentInfo

	def getSegmentNumDoc (self, seg):
		try:
			return self.segments.segmentInfo [int (seg)]
		except KeyError:
			return 0

	def getNewSegment (self):
		if not self.segments.segmentInfo:
			return self.initial_newseg
		return max (self.segments.segmentInfo.keys ()) + 1

	def getSegmentInfo (self):
		return self.segments.segmentInfo

	def addSegment (self, seg, numDoc = 0):
		self.segments.segmentInfo [int (seg)] = numDoc

	def setReadingSegments (self):
		segs = self.getSegmentList ()
		if not segs: return
		segs = [str (x) for x in segs]
		self.lock.lock ("using-%s" % (delune.PID or os.getpid ()), ",".join (segs))		
	
	def getReadingSegments (self):
		segs = self.lock.lockread ("using-%s" % (delune.PID or os.getpid ()))
		if not segs: return []
		return [int (x) for x in segs.split (",")]
	
	def getReadingSegmentsAllProcesses (self):
		locks, errmsg = self.lock.locks ("using")
		d = {}
		for lname, ltime in locks:
			pid = int (lname.split ("-")[-1])
			isDeLuneServer = processutil.is_running (pid)
			if not isDeLuneServer:
				self.lock.unlock (lname)
				continue
					
			segs = self.lock.lockread (lname)
			if not segs: continue
			for seg in segs.split (","):
				d [int(seg)] = None
				
		return list(d.keys ())
		
	def isDeLuneServer (self, pid):
		proc = "/proc/%d/cmdline" % pid
		if os.path.isfile (proc):
			f = open (proc)
			exefilename = f.read ()
			f.close ()
			if exefilename.find ("python") != -1:
				return True
								
	def getN (self):
		return self.segments.N
		
	def getAlias (self):
		return self.alias
				
	def move (self, source, target, seg):
		self.copy (source, target, seg, True)
		
	def copy (self, source, target, seg, remove = False):
		for ext in self.exts:
			try:
				shutil.copyfile (os.path.join (source, str(seg) + "." + ext), os.path.join (target, str(seg) + "." + ext))
				if remove:
					os.remove (os.path.join (source, str(seg) + "." + ext))
			except IOError as why:
				if why [0] != 2:
					raise
	
	def clone (self, seg):
		current = self.fs.getsegmentpath (seg)
		newseg = self.getNewSegment ()
		newpath = self.fs.new (newseg)
		for ext in self.exts:
			src = os.path.join (current, "%d.%s" % (seg, ext))
			dest = os.path.join (newpath, "%d.%s" % (newseg, ext))
			if not os.path.isfile (src):
				continue
			if os.path.isfile (dest):
				os.remove (dest)
			shutil.copyfile (
				os.path.join (current, "%d.%s" % (seg, ext)),
				os.path.join (newpath, "%d.%s" % (newseg, ext))
			)
		return newpath, newseg
	
	def hasSegmentsFile (self):
		return os.path.isfile (os.path.join (self.master, "segments"))
	
	def removeSegmentsFile (self):
		os.remove (os.path.join (self.master, "segments"))
						
	def getopt (self, name = None, default = None, **karg):
		if name:
			try: return getattr (self.options, name)
			except AttributeError: return default
		
		for k, v in list(karg.items ()):
			try: return getattr (self.options, k)
			except AttributeError: return v
						
	def setopt (self, name = "", value = "", **karg):	
		if name:
			setattr (self.options, name, value)
		for k, v in list(karg.items ()):
			setattr (self.options, k, v)
		