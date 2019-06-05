from delune import _delune
import os, glob
import pickle as pk
import zlib

class BinFile:
	def __init__ (self, path, mode = "r"):
		self.path = path
		self.mode = mode		
		
		if mode == "r":
			flag = os.O_RDONLY
		else:
			flag = os.O_WRONLY | os.O_CREAT			
		if os.name == "nt":
			flag |= os.O_BINARY
		
		oldmask = os.umask (0o113)
		self.fdno = os.open (self.path, flag)
		os.umask (oldmask)
		self.bf = _delune.BinFile (self.fdno, self.mode)		
	
	def __enter__ (self):
		return self
	
	def __exit__ (self, type, value, tb):
		self.close ()
			
	def __getattr__ (self, attr):
		return getattr (self.bf, attr)
		
	def close (self):
		self.bf.close ()
		os.close (self.fdno)


class ZPickled:
	def __init__ (self, filename, mode="r", size = 1000000000):
		self.filename = filename
		self.mode = mode
		self.size = size
		self.colname = os.path.basename (filename)
		self.fileindex = 0
		self.reopens = 0
		self.count = 0
		self.pos = 0
		self.open ()
	
	def __enter__ (self):
		return self
	
	def __exit__ (self, type, value, tb):
		self.close ()
			
	def __len__ (self):
		g = glob.glob (self.filename + "*")
		g.sort ()
		db = BinFile (g [-1], "r")
		c = db.readInt4 ()
		return c		
		
	def open (self):
		if self.mode == "a":
			for i in range (1000):
				if os.path.isfile ("%s.%d" % (self.filename, i)):
					self.fileindex = i
					self.reopens = 1
					break					
			if self.reopens:
				fn = "%s.%d" % (self.filename, self.fileindex)
				self.fileindex += 1
			else:
				fn =  self.filename
			self.db = BinFile (fn, "r")
			self.count = self.db.readInt4 ()
			self.close ()
			self.db = BinFile (fn, "a")
		
		else:
			self.db = BinFile (self.filename, self.mode)
			if self.mode == "w": 
				self.db.writeInt4 (0)
			elif self.mode == "r": 
				self.count = self.db.readInt4 ()			
	
	def reopen (self):
		self.close ()
		if self.mode == "r":
			if os.path.isfile ("%s.%d" % (self.filename, self.fileindex)):
				self.db = BinFile ("%s.%d" % (self.filename, self.fileindex), "r")
				self.count = self.db.readInt4 ()
		else:
			self.db = BinFile ("%s.%d" % (self.filename, self.fileindex), "w")
			if self.mode in "wa": self.db.writeInt4 (0)							
		self.fileindex += 1
		self.reopens += 1
	
	def __iter__ (self):
		return self
	
	def __next__ (self):
		d = self.get ()
		if not d:
			raise StopIteration
		return d	
		
	def deserialize (self, d):
		return pk.loads (zlib.decompress (d))
		
	def serialize (self, d):
		return zlib.compress (pk.dumps (d, 1), 9)
	
	def close (self):
		if self.mode in "wa":
			self.db.seek (0)
			self.db.writeInt4 (self.count)
		
		if self.db:
			self.db.close ()
			self.db = None

	def truncate (self):
		if self.mode == "w" and os.path.isfile (self.filename):
			self.close ()
			os.remove (self.filename)
			self.open ()
	
	def write (self, post):		
		self.db.writeBytes (self.serialize (post))
	
	def get (self):	
		if self.pos == self.count:
			self.reopen ()
			if self.pos == self.count: 
				return None
		self.pos += 1
		return self.deserialize (self.db.readBytes ())
	
	def add (self, post):	
		self.addmany ([post])
		
	def addmany (self, posts):
		for post in posts:
			self.write (post)
			self.count += 1
			if self.db.tell () > self.size:
				self.reopen ()

def open (path, mode = "r"):
	return BinFile (path, mode)

def openzp (path, mode = "r", size = 1000000000):
	return ZPickled (path, mode, size)
