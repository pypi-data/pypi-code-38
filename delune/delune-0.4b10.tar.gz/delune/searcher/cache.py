import threading
import time

class Cache:
	def __init__ (self, max = 30):
		self.max = max
		self.cache = {}
		self.timeused = {}
		self.mutex = threading.Lock ()

	def clear (self):
		self.mutex.acquire ()
		self.cache.clear ()
		self.timeused.clear ()
		self.mutex.release ()

	def set (self, key, value):
		if self.max <= 0: return
		self.mutex.acquire ()
		if len (self.cache) > self.max:
			self.drop ()

		self.cache [key] = value
		self.timeused [key] = [0, int (time.time ())]
		self.mutex.release ()

	def get (self, key):
		self.mutex.acquire ()
		try:
			value = self.cache [key]
			t, u = self.timeused [key]
		except KeyError:
			self.mutex.release ()
			return None

		self.timeused [key] = [u + 1, int (time.time ())]
		self.mutex.release ()
		return value

	def remove (self, key):
		try: del self.cache [key]
		except KeyError: pass
		try: del self.timeused [key]
		except KeyError: pass

	def drop (self):
		minkey = None
		lasttu = None
		for key, tu in list(self.timeused.items ()):
			if minkey is None:
				minkey = key
				lasttu = tu
			elif tu < lasttu:
				minkey = key
				lasttu = tu

		self.remove (minkey)
