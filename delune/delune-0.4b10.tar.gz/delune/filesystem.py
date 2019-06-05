from rs4 import pathtool
from delune import _delune
import os
import glob

class FileSystem:
	def __init__ (self, paths):
		self.paths = []
		if type (paths) is type (""):
			paths = [paths]
		for path in paths:
			path = os.path.normpath (path)
			self.paths.append (path)
			pathtool.mkdir (path)
				
		self.dirs = {}
		
		self.master = self.paths [0]		
		self.__cache = {}
		self.__cacheDir ()
		self.__dirty = 0

	def getpathes (self):
		pathes = {}
		i = 0
		for path in self.paths:
			pathes [i] = path
			i += 1
		return pathes

	def notify (self):		
		self.__dirty = 1

	def getmaster (self):
		return self.master

	def __cacheDir (self):
		self.__cache = {}		
		for path in self.paths:
			self.dirs [path] = 0
			segs = {}
			for file in os.listdir (path):
				try: segs [int (file [:-4])] = None
				except ValueError: pass	
			
			for seg in segs:
				size = 0
				for segfile in glob.glob (os.path.join (path, str (seg) + ".*")):
					size += os.stat (segfile).st_size
				
				self.__cache [seg] = (path, size)
				self.dirs [path] += size
		
		self.__dirty = 0
		
	def dirty (self):
		self.__dirty = 1

	def get (self, seg):
		if self.__dirty:
			self.__cacheDir ()

		try:
			return self.__cache [int (seg)][0]
		except KeyError:
			self.__cacheDir ()
			try: return self.__cache [int (seg)][0]
			except: return None

	def new (self, seg):
		prev = self.get (seg) #previously failed file
		if prev: return prev
		
		if self.__dirty:
			self.__cacheDir ()
		
		filesizes = list(self.dirs.items ())
		filesizes.sort (key = lambda x: x[1])
		
		freespaces = {}		
		for path in list(self.dirs.keys ()):
			freespaces [path] = _delune.getdiskspace (path)
		
		for path, size in filesizes:
			if freespaces [path] > 2000:
				return path
		
		diskspaces = list(self.dirs.items ())
		diskspaces.sort (key = lambda x: x[1], reverse = True)		
		
		return diskspaces [0][0]

	def getpathindex (self, seg):
		return self.paths.index (self.get (int (seg)))
	
	def getsegmentpath (self, seg):
		return self.paths [self.getpathindex (seg)]
	
	def hasDeleted (self, seg):
		return os.path.isfile (os.path.join (self.getsegmentpath (seg), "%s.del" % seg))
			
	def getsegmentsize (self, seg):
		path = self.getsegmentpath (seg)
		info = {}
		for file in glob.glob (os.path.join (path, str (seg) + ".*")):
			info [os.path.split (file) [-1][-3:]] = os.stat (file).st_size
		return info
		
	def dirinfo (self):
		if self.__dirty:
			self.__cacheDir ()		
		n = {}
		for k, v in list(self.__cache.items ()):
			n [str (k)] = v
		return n
		
	def all (self):
		if self.__dirty:
			self.__cacheDir ()

		return list(self.__cache.keys ())
	
	def segments (self):
		return self.all ()
		
	def remove (self, seg):
		if self.__dirty:
			self.__cacheDir ()

		for file in glob.glob (os.path.join (self.get (seg), str (seg) + ".*")):
			try:
				os.remove (file)
			except OSError as why:
				if why [0] != 2:
					raise
			
		self.__dirty = 1


def get_segment_files (paths):
	files = {}
	for path in paths:
		segs = {}
		for file in os.listdir (path):
			try: segs [int (file [:-4])] = None
			except ValueError: pass
								
		for seg in segs:
			files [seg] = []
			for segfile in glob.glob (os.path.join (path, str (seg) + ".*")):
				files [seg].append ((segfile, os.stat (segfile).st_size, os.stat (segfile).st_mtime))
		
		segments = os.path.join (path, "segments")
		if os.path.isfile (segments):
			files ['segments'] = (segments, os.stat (segments).st_size, os.stat (segments).st_mtime)
		
	return files


if __name__ == "__main__":
	f = FileSystem (
		[
			"d:/bladedb/0/bladeindex/ontowns",
			"d:/bladedb/1/bladeindex/ontowns",
			"d:/bladedb/2/bladeindex/ontowns",
		],
		None
	)
	
	
	print(f.getsegmentpath (1514))
	print(f.getsegmentsize (1514))
	
	