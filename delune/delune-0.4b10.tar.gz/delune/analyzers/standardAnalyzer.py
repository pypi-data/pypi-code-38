from delune import _delune
import copy
from .util import htmlstrip
from . import abstractAnalyzer
import re

RX_DIGIT = re.compile ("(\s|^)[^a-zA-Z]+(\s|$)")
	
class Analyzer (abstractAnalyzer.Analyzer):
	defaults = {
		"biword": 0,
		"ngram": 1,
		"stem_level": 1,
		"stopwords": [],
		"endwords": [],
		"stopwords_case_sensitive": 1,
		"ngram_no_space": 0,	
		"strip_html": 0,
		"make_lower_case": 0,
		"contains_alpha_only": 0	
	}
	
	def __init__ (self, max_term = 8, numthread = 1, **karg):
		self.hstriper = htmlstrip.build_parser ()
		self._strip_html = False # for fast detect
		self._make_lower_case = False
		self._contains_alpha_only = False
		self.karg = karg
		self.options = copy.copy (self.defaults)
		abstractAnalyzer.Analyzer.__init__ (self, max_term, numthread)		
		self.setopt (**karg)
	
	def createTSAnalyzers (self, num):
		for i in range (num):
			# stem-level=weak, ngram=bi, default stopwords list
			f = _delune.Analyzer (self.max_term, self.karg.get ("stem_level", 1), self.karg.get ("ngram", 2), self.karg.get ("biword", 0))
			f.set_stopwords ()
			self.ats.append (f)
	
	#------------------------------------------------
	# set options 
	#------------------------------------------------
	def getopt (self, **karg):
		for k, v in list(karg.items ()):	
			return self.options.get (k, v)
						
	def setopt (self, **karg):
		for k, v in list(karg.items ()):
			self.apply_option (k, v)
			
	def apply_option (self, name, value):
		try:
			setfunc = getattr (self, "set_" + name)
		except AttributeError:
			raise NameError("Unknown Option `%s`" % name)
		
		self.options [name] = value
		setfunc (value)
			
	#------------------------------------------------
	# exported methods
	#------------------------------------------------			
	def strip_html (self, document):
		try:
			return self.hstriper.parse (document)
		except UnicodeDecodeError:
			return self.hstriper.parse (self.to_ascii (document))
		except UnicodeEncodeError:
			return self.hstriper.parse (self.remove_surrogate_escaping (document))	
			
	def preprocess (self, document):
		if self._strip_html:
			document = self.strip_html (document)
		if self._make_lower_case:
			document = document.lower ()	
		if self._contains_alpha_only:
			document = RX_DIGIT.sub (" ", document)
		return document
		
	def to_ascii (self, document):
		return document.encode ("ascii", "ignore").decode ("utf8")
		
	def remove_surrogate_escaping (self, document):
		return document.encode ("utf8", "ignore").decode ("utf8")
		
	def formalize (self, document):
		try:
			return self.ats [self.get_tid ()].formalize (document)
		except UnicodeDecodeError:	
			return self.ats [self.get_tid ()].formalize (self.to_ascii (document))
		except UnicodeEncodeError:	
			return self.ats [self.get_tid ()].formalize (self.remove_surrogate_escaping (document))
				
	def index	(self, document, lang = "en"):
		document = self.preprocess (document)
		return self.ats [self.get_tid ()].analyze (document, lang)
	
	def freq (self, document, lang = "en"):		
		k = self.index (document, lang)
		if k:
			return [(x [0], len (x [1])) for x in list(k.items ())]		
		return []	
	term = freq
	
	def tokenize (self, document, lang = "en"):
		if self.options.get ("make_lower_case"):
			document = document.lower ()			
		try:
			return self.ats [self.get_tid ()].stem (document, lang)
		except UnicodeDecodeError:	
			return self.ats [self.get_tid ()].stem (self.to_ascii (document), lang)
		except UnicodeEncodeError:	
			return self.ats [self.get_tid ()].stem (self.remove_surrogate_escaping (document))	
	query = tokenize
	
	def stem (self, document, lang = "en"):
		document = self.preprocess (document)
		return self.tokenize (document)
	
	def count_stopwords (self, document, lang = "en"):
		document = self.preprocess (document)
		try:
			return self.ats [self.get_tid ()].count_stopwords (document, lang)
		except UnicodeDecodeError:	
			return self.ats [self.get_tid ()].count_stopwords (self.to_ascii (document), lang)
		except UnicodeEncodeError:	
			return self.ats [self.get_tid ()].formalize (self.remove_surrogate_escaping (document))	
		
	#------------------------------------------------
	# handle options 
	#------------------------------------------------	
	def set_contains_alpha_only (self, flag):
		self._contains_alpha_only = flag
		
	def set_strip_html (self, flag):
		self._strip_html = flag
	
	def set_make_lower_case (self, flag):
		self._make_lower_case = flag
		
	def set_stopwords (self, wordlist):
		for an in self.ats:
			an.set_stopwords (wordlist)
			
	def set_endwords (self, wordlist):
		for an in self.ats:
			an.set_endwords (wordlist)		
	
	def set_stem_level (self, stem_level):
		for an in self.ats:
			an.set_stem_level (stem_level)
		
	def set_ngram_no_space (self, flag):
		for an in self.ats:
			an.set_ngram_ignore_space (flag)	
	
	def set_stopwords_case_sensitive (self, flag):
		for an in self.ats:
			an.set_stopwords_case_sensitive (flag)	
				
	def set_ngram (self, ngram):
		for an in self.ats:
			an.set_ngram (ngram)	
	
	def set_biword (self, flag):
		for an in self.ats:
			an.set_biword (flag)
		