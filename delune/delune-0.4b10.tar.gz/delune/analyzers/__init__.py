from hashlib import md5

class AnalyzerFactory:
	def __init__ (self, numthread, logger = None):
		self.numthread = numthread
		self.logger = logger
		self.rooms = {}
	
	def close (self):	
		for a in list(self.rooms.values ()):
			a.close ()
		
	def checkIn (self, analyzer):
		l = []		
		for n in dir (analyzer):
			if n.startswith ("__"): continue
			v = str (getattr (analyzer, n))
			if v.find ("<") != -1: continue # skip instances
			l.append ("%s=%s" % (n, v))
		l.sort ()
		l.insert (0, "class=%s" % analyzer.__class__)
		sl = "&".join (l)		
		dd = md5 (sl.encode ("utf8"))
		idkey = dd.hexdigest()
		if idkey in self.rooms:
			return self.rooms [idkey]
		else:
			if len (analyzer) != self.numthread:
				analyzer.close ()
				analyzer.createTSAnalyzers (self.numthread)
			self.rooms [idkey] = analyzer
		return analyzer
		

factory = None
	
def buildFactory (numthread, logger):
	global factory
	factory = AnalyzerFactory (numthread, logger)

def checkIn (analyzer):
	global factory
	return factory.checkIn (analyzer)

def close ():	
	global factory
	factory.close ()
	factory = None