from delune import binfile
from rs4 import pathtool
import os
import shutil
import random
import threading
import glob
import time

class DocQueue:
	quename = "que"
	def __init__ (self, si):
		self.si = si
		self.que_dir = os.path.join (self.si.fs.getmaster (), '.que')
		pathtool.mkdir (self.que_dir)
		self._tlock = threading.RLock ()
		self._plock = self.si.plock # process lock
		self.writer = None
		self.current = None
		self.commit_all ()
		self.last_written = time.time ()
		self.new_docs = 0
			
	def __detect_max_seq (self):	
		while 1:
			rn = random.randrange (100000, 999999)
			if not os.path.isfile (os.path.join (self.que_dir, "%s.%d.lock" % (self.quename, rn))) and not os.path.isfile (os.path.join (self.que_dir, "%s.%d" % (self.quename, rn))):
				return rn
	
	def __commit (self, temp, remove = False):
		if remove or os.path.getsize (temp) == 0:			
			os.remove (temp)			
		else:	
			shutil.move (temp, temp [:-5])

	def commit_all (self):		
		for uncommit in os.listdir (self.que_dir):
			if uncommit.startswith (self.quename + ".") and uncommit.endswith (".lock"):
				self.__commit (os.path.join (self.que_dir, uncommit))
		
	def __call__ (self, method, doc):
		self.add (method, doc)
	
	def open (self):	
		self.current = self.__detect_max_seq ()
		self.writer = binfile.BinFile (os.path.join (self.que_dir, "%s.%d.lock" % (self.quename, self.current)), "w")
	
	def truncate (self):
		self.close ()
		with open (os.path.join (self.que_dir, "%s.truncate" % self.quename), "w") as f:
			f.write ("DO NOT DELETE")
		
	def close (self, remove = 0):
		if self.writer is None:
			return
		os.fsync (self.writer.fileno ())	
		self.writer.close ()
		self.writer = None
		self.__commit (
			os.path.join (self.que_dir, "%s.%d.lock" % (self.quename, self.current)), 
			remove
		)
			
	def rollback (self):
		with self._tlock:
			if self.new_docs:
				self.close (1)
				self.open ()
			self.new_docs = 0
	
	def commit (self):
		with self._tlock:
			self.close ()
			self.new_docs = 0
			
	def add (self, method, doc):
		with self._tlock:
			self.last_written = time.time ()
			if self.writer is None:			
				self.open ()
			self.writer.writeVInt (method)
			self.writer.writeZBytes (doc)
			self.new_docs += 1
