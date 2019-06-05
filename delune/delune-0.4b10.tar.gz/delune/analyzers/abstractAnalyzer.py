import delune
from delune import _delune
import threading
from delune.fields import *

class Analyzer:
	def __init__ (self, max_term = 8, numthread = 1):
		self.max_term = max_term
		self.numthread = numthread
		self.ats = []
		self.createTSAnalyzers (numthread)
		self.closed = False
		
	def __len__ (self):
		return len (self.ats)
		
	def get_tid (self):
		try: return threading.currentThread ().getId ()
		except AttributeError: return -1
	
	def createTSAnalyzers (self, num):
		pass
	
	def close (self):
		if self.closed: return
		for each in self.ats:
			each.close ()
		self.closed = True
		self.ats = []

	def generalize (self, t):
		return t.replace ("\x00", "")
	
	def transform (self, document):
		return document

	def analyze (self, document, lang, fdtype):		
		if fdtype == TEXT:
			return self.index (document, lang)
		elif fdtype == TERMSET:
			return self.freq (document, lang)
		else:
			return self.tokenize (document, lang)

	def index	(self, document, lang = "en"):
		raise NotImplementedError

	def freq (self, document, lang = "en"):
		raise NotImplementedError

	def tokenize (self, document, lang = "en"):
		raise NotImplementedError
