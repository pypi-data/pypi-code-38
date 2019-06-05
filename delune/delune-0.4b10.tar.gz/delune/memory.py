import threading
import os
from delune import _delune

class Memory:
	def __init__ (self, threads, buffer, limit, scope = "disk", logger = None):
		self.mpool = _delune.MemoryPool (threads, buffer, int (limit / float (threads)))
		self.limit = limit * (1024 << 10)
		self.threads = threads
		self.scope = scope
		self.logger = logger
		self.mutexes = {}
		self.lock = threading.Lock ()
		self.thread_id_map = {}
		self.got_main_thread = 0
	
	def usage (self):
		u = []
		for i in range (self.threads):
			bytes = self.mpool.usage (i)
			u.append ((i, bytes))
		return u	
	
	def maintern (self):
		# maintern memory
		if self.mpool.usage () > self.limit:
			ousage = self.mpool.usage ()
			self.mpool.maintern (self.__gettid ())
			self.logger ("memory reduced %d -> %d" % (ousage, self.mpool.usage ()), "info", "")		

	def recover (self):
		self.mpool.recover (self.__gettid ())

	def close (self):
		self.mpool.close ()

	def __getscope (self, path):
		if self.scope == "disk":
			return os.path.split (os.path.split (os.path.normpath (path)) [0]) [0]
		elif self.scope == "index":
			os.path.split (os.path.normpath (path)) [0]
		else:
			return os.path.normpath (path)

	def __gettid (self):
		tid = id (threading.currentThread ())
		try: 
			return self.thread_id_map [tid]
		except KeyError:
			if (threading.currentThread ().getName() == "MainThread"):
				self.thread_id_map [tid] = 0
				self.got_main_thread = 1
				return 0
			tids_count = len (self.thread_id_map) - self.got_main_thread			
			if tids_count == self.threads:
				raise SystemError("Too Many Threads")				
		self.thread_id_map [tid] = tids_count
		return tids_count

	def set (self, segment):
		if self.scope == "global": return -1

		scope = self.__getscope (os.path.join (segment.home, str (segment.seg)))
		self.lock.acquire ()
		try:
			mutex_id = self.mutexes [scope]
		except KeyError:
			mutex_id = self.mpool.newmutex ()
			self.mutexes [scope] = mutex_id

		self.lock.release ()
		return mutex_id

	def get (self, segment = None):
		if segment is None:
			return self.mpool.get (self.__gettid (), -1)
		return self.mpool.get (self.__gettid (), segment.mutex_id)

	def remove (self, segment):
		if self.scope != "segment": return 0

		mutex_id = segment.mutex_id
		if mutex_id == -1: return 0

		self.lock.acquire ()
		for scope, _mutex_id in list(self.mutexes.items ()):
			if _mutex_id == mutex_id:
				del self.mutexes [scope]
				self.mpool.delmutex (mutex_id)
		self.lock.release ()
		return 1

memory = None

def isInitialized ():
	return memory
	
def initialize (threads, buffer, limit, mutexscope = "disk", logger = None):
	global memory
	memory = Memory (threads, buffer, limit, mutexscope, logger)
	
def set (segment):
	global memory
	if memory:
		return memory.set (segment)	

def get (segment = None):
	global memory
	if memory:
		return memory.get (segment)	

def remove (segment):
	global memory
	if memory:
		memory.remove (segment)
	
def destroy ():
	global memory
	if memory:
		memory.close ()
		memory = None
	
def recover ():
	global memory
	if memory:
		memory.recover ()
	
def get_buffer_size ():
	global memory
	if memory:
		return memory.mpool.buffer_size	

def maintern ():
	global memory
	memory.maintern ()

def usage ():
	global memory
	return memory.usage ()
	