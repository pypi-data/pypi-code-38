#encoding: utf8
import re
from . import typeinfo
from .. import querylexer
import delune
from delune.fields import *

class Field:
	methology = "Term"
	def __init__ (self, mem, segment, type, term, lang, name, qstr, num, analyzer = None, loadnorm = False, ngram_opts = ""):
		self.mem = mem
		self.segment = segment
		self.type = type
		self.term = term
		self.lang = lang
		self.name = name
		self.qstr = qstr
		self.num = num
		self.analyzer = analyzer
		self.loadnorm = loadnorm
		self.ngram_opts = ngram_opts
		
		self.value = None
		self.readprox = 0
		self.stopword = 0
		self.near = 0
		self.loose = 0
		self.weight = 1.0
		self.ngram = 0
		self.ti = None
		self.sp = None
		self.df = 0
		
		if self.term: self.process ()
	
	def get_ngram_opts (self, qstr):
		ngram_opts = ""
		if qstr [-1] == "|":
			ngram_opts += "R"
			qstr = qstr [:-1]
		if qstr [0] == "|":
			ngram_opts += "L"
			qstr = qstr [1:]
		return qstr, ngram_opts
		
	def loadTi (self):
		if not self.type: return
		self.ti = self.segment.getTermInfo (self.mem, self.value, self.num)
		if self.ti:
			self.df = self.ti [0]
		
	def loadSm (self):
		self.sp = self.segment.getSortMapPointer (self.num)
	
	def setTi (self, ti, sp = None):
		self.ti = ti
		self.df = ti [0]
		self.sm = sp
					
	def __str__ (self):
		return self.term
	
	def __repr__ (self):
		return "<%s %s analyzed: %s (fdtype: %s, fdno: %s) [readprox:%d, near:%d, loose:%d]>" % (
			self.__class__.__name__, 
			self.term, 
			self.qstr,			
			self.type, self.num, self.readprox, self.near, self.loose
		)
	
	def __cmp__ (self, other):
		return self.segment == other.segment and self.num == other.num and self.value == other.value
		
	def process (self):
		self.value = self.qstr
		self.loadTi ()
		
		
class Coord (Field):
	methology = "Coord"
	def process (self):
		self.loadSm ()
		if not self.sp: return
		
		coord, meter = self.qstr.split ("~")
		meter = int (meter) # convert from km to m
				
		precision = 10 ** (typeinfo.typemap.getsize (self.type)-2)	
		lat, lon = [int ((float (x) + 180) * precision) for x in coord.split ("/")]
		
		self.value = (lat, lon, meter)

class Digit (Field):
	methology = "Digit"
	def process (self):
		self.loadSm ()
		if not self.sp: return
		if self.qstr == "all":
			a = -1
			b = -1
		
		else:
			try: 
				a, b = self.qstr.split ("/")
			except ValueError:
				try:
					a, b = self.qstr.split ("~")
				except ValueError:
					try: 
						a = int (self.qstr)
					except:
						return 0
					else:
						if typeinfo.typemap.isbit (self.type):
							a = str (self.qstr)
							b = "all"
						else:
							a = int (self.qstr)
							b = a + 1
		
		if b in ("all", "any", "none"):
			try: a = int (a, 2)
			except: return
			self.smfunc = 0
			
		else:
			if a == "":
				a = -1
			else:	
				try: a = int (a)
				except: return
			
			if b == "":
				b = -1		
			try: b = int (b)
			except: return
								
			self.smfunc = 1
		
		self.value = (a, b)


class Term (Field):
	methology = "Term"
	def process (self):
		if (self.analyzer and self.qstr != "it") or type (self.qstr) is type ([]):
			# ngram check
			if type (self.qstr) is type ([]):
				value = self.qstr # maybe recieved from WildCard
				ngram_opts = self.ngram_opts
								
			else: # string type
				qstr, ngram_opts = self.get_ngram_opts (self.qstr)
				value = self.analyzer.analyze (qstr, self.lang, "query")
				if not value:
					self.stopword = 1
					return
			
			if len (value) > 1:
				self.ngram = 1
				
			if self.ngram and len (value) > 2: # ngram but 1 char is not applied
				if "R" not in ngram_opts:
					value = value [:-1] # right wildcard search, if has r, right exactly matching serach
				if "L" not in ngram_opts:
					value = value [1:] # left wildcard
			
			# ngram handle
			if self.ngram:
				self.df = 1 # dummy true value
				self.value = []
				for ngram in value: # for right wildcard search					
					termTi = Term (self.mem, self.segment, self.type, self.name+":"+ngram, self.lang, self.name, ngram, self.num, None, self.loadnorm)
					if not termTi.df:
						self.df = 0
						self.value = []
						return
											
					termTi.readprox = 1
					termTi.near = 1
					termTi.loose = 1
					self.value.append (termTi)

				return # value is list, do not handle any more
			
			# not ngram: should be ascii or ONE char ngram
			self.value = value [0] # first stemmed term
				
		else:
			# needn't analyzing, already analyzed.
			self.value = self.qstr
		
		self.loadTi ()
		if self.loadnorm: self.loadSm ()
	
											
class WildCard (Term):
	methology = "WildCard"
	def process (self):
		qstr, ngram_opts = self.get_ngram_opts (self.qstr)
		test_value = self.analyzer.analyze (qstr, self.lang, "query") # check ngram		
		if len (test_value) > 1: # Ngram is already based on wildcard search
			termTi = Term (self.mem, self.segment, self.type, self.name+":"+self.qstr, self.lang, self.name, test_value, self.num, None, self.loadnorm, ngram_opts)
			self.value = termTi.value
			self.methology = "TermList"
			return
		
		self.ti = self.segment.getTermInfos (self.mem, self.qstr, self.num)		
		if not self.ti: return
		
		if self.loadnorm: self.loadSm ()				
		self.value = []
		for ti in self.ti:
			f = Term (self.mem, self.segment, self.type, None, self.lang, self.name, None, self.num, None, 0)
			f.setTi (ti, self.sp)
			self.value.append (f)

		
class FieldWildCard (Term):
	methology = "WildCard"
	def process (self):
		self.value = self.qstr
		self.ti = self.segment.getTermInfos (self.mem, self.value, self.num)
		if not self.ti: 
			return
		
		self.value = []
		for ti in self.ti:
			f = Field (self.mem, self.segment, self.type, None, self.lang, self.name, None, self.num, None, 0)
			f.setTi (ti)
			self.value.append (f)

class FieldRange (Term):
	methology = "WildCard"
	def process (self):
		self.value = self.qstr
		
		a, b = self.value.split ("~")
		if self.type.startswith ("Fnum"):
			value = (typeinfo.zfill (self.type, a), typeinfo.zfill (self.type, b))		
		else:
			value = (a, b)
		self.ti = self.segment.getTermInfos2 (self.mem, value, self.num)
		if not self.ti: 
			return
		
		self.value = []
		for ti in self.ti:
			f = Field (self.mem, self.segment, self.type, None, self.lang, self.name, None, self.num, None, 0)
			f.setTi (ti)
			self.value.append (f)
					
class TermList (Term):
	methology = "TermList"
	def process (self):
		self.value = []
		optimize = True
		terms = querylexer.TermLexer (self.qstr).tokenize ()
		
		if not terms:
			self.stopword = 1
			return
		
		for term in terms:			
			if term.find ("^") == 0:
				continue
				
			else:
				termTi = Term (self.mem, self.segment, self.type, self.name+":"+term, self.lang, self.name, term, self.num, self.analyzer, self.loadnorm)
				if termTi.stopword:
					continue
				if not termTi.value:
					self.df = 0
					self.value = []
					return
					
				if termTi.ngram:
					optimize = False # ngram is phrase, no sorting
					self.methology = "TermList"
					self.value += termTi.value
				else:
					self.value.append (termTi) # termTi.value is String
		
		if not self.value: 
			self.stopword = 1			
		elif len (self.value) > 1 and optimize:			
			self.value.sort (key = lambda x: x.df)
		
class Phrase (Term):
	methology = "TermList"
	def process (self):		
		self.value = []
		readprox = 0
		if self.type == TEXT:
			readprox = 1
		
		# relexing for analyzer
		terms = querylexer.TermLexer (self.qstr).tokenize ()
		if not terms:
			self.stopword = 1
			return
			
		nextnear = 1
		nextloose = 0		
		for term in terms:
			if not term: 
				continue			
			if term.find ("^") == 0:
				if self.type == TEXT:
					if not self.value: continue
					nextnear = int (term [1:])
					if nextnear > 1: nextloose = 1					
				continue
							
			termTi = Term (self.mem, self.segment, self.type, self.name+":"+term, self.lang, self.name, term, self.num, self.analyzer, self.loadnorm)
			if termTi.stopword: 
				continue
			
			if not termTi.value:
				self.value = []
				self.df = 0
				return
			
			if termTi.ngram:
				termTi.value[0].readprox = readprox
				# to skip '지>' and '<창'
				termTi.value[0].near = 2
				termTi.value[0].loose = 1
				self.value += termTi.value
			else:  # termTi.value is String
				termTi.readprox = readprox
				termTi.near = nextnear
				termTi.loose = nextloose	
				self.value.append (termTi)
			
			nextnear = 1
			nextloose = 0
		
		if not self.value: 
			self.stopword = 1		
					
class FieldReader:
	def __init__ (self, mem, segment, analyzer, loadnorm):
		self.mem = mem
		self.segment = segment
		self.analyzer = analyzer		
		self.loadnorm = loadnorm
		
	def __call__ (self, type, term, lang, name, qstr, num):
		if not type:
			return Field (self.mem, self.segment, type, term, lang, name, qstr, num)
		
		if typeinfo.typemap.iscoord (type):
			return Coord (self.mem, self.segment, type, term, lang, name, qstr, num)
		
		elif typeinfo.typemap.isint (type) or typeinfo.typemap.isbit (type):
			return Digit (self.mem, self.segment, type, term, lang, name, qstr, num)
		
		elif typeinfo.typemap.hasnorm (type):
			if qstr [0] == "`":
				qstr = qstr [1:]
				return Phrase (self.mem, self.segment, type, term, lang, name, qstr, num, self.analyzer, self.loadnorm)			
			elif qstr.find ("-") != -1 or qstr.find ("/") != -1 or qstr.find ("^") != -1:
				return Phrase (self.mem, self.segment, type, term, lang, name, qstr, num, self.analyzer, self.loadnorm)			
			elif qstr [-1] == "*":
				qstr = qstr [:-1]				
				return WildCard (self.mem, self.segment, type, term, lang, name, qstr, num, self.analyzer, self.loadnorm)
			else:	
				return TermList (self.mem, self.segment, type, term, lang, name, qstr, num, self.analyzer, self.loadnorm)
				
		else:
			if qstr [0] == "`":
				qstr = qstr [1:]					
			if qstr.count ("~") == 1:
				return FieldRange (self.mem, self.segment, type, term, lang, name, qstr, num, self.analyzer, self.loadnorm)
			elif qstr [-1] == "*": # wildcard is not perform analysis
				qstr = qstr [:-1]
				return FieldWildCard (self.mem, self.segment, type, term, lang, name, qstr, num)			
			else:	
				return Field (self.mem, self.segment, type, term, lang, name, qstr, num)
		
		
if __name__ == "__main__":
	from delune.analyzer import porterstemAnalyzer
	
	f = porterstemAnalyzer.Analyzer ()
	x = FieldReader (None, None, f, 1)
	ti = x ("index", 'asdasda', "default", 'asdadads', 0)
	print(ti.value)
	
	
	