from datetime import datetime
from . import queryparser
from . import querylexer
import types
import copy
import re
import time
from .segment import fieldreader, typeinfo
from .. import _delune, memory

def makeHighLightRE (highlights):
	highlights = "|".join (highlights)
	new_highlights = ""
	for c in highlights:
		if c in '.?+*[]()\\^${}':
			new_highlights += "\\" + c
		else:
			new_highlights += c
			
	return new_highlights
	

class TermInfos:
	def __init__ (self, segments, analyzer, tfidf):
		self.segments = segments
		self.analyzer = analyzer
		self.tfidf = tfidf
		self.scorable = 0
		self.segTi = {}
		self.termDF = {}
		self.coord = {}
	
	def setTi (self, fdreader, term, lang):		
		try:
			if term [0] == "`": 
				raise ValueError # default field type
			name, value = term.split (":", 1)
		except ValueError:
			name, value = "default", term
		
		type, num = self.segments.si.getFieldInfo (name)
		fdi = fdreader (type, term, lang, name, value, num)
		if fdi.type == "coord":
			self.coord [fdi.name] = fdi
			if len (self.coord) >1: raise ValueError			
		return fdi	
	
	def get_terminfo (self, fdreader, segment, expression, lang, dup):
		if type (expression) is str: # only 1 term
			op, lop, rop = "*", expression, None
		else:
			op, lop, rop = expression
		
		if type (lop) is list:
			lop = self.get_terminfo (fdreader, segment, lop, lang, dup)
			
		if type (rop) is list:
			rop = self.get_terminfo (fdreader, segment, rop, lang, dup)
		
		for each in (lop, rop):
			if not each: 
				continue
				
			if each not in self.segTi [fdreader.segment]:			
				ti = self.setTi (fdreader, each, lang)				
				self.segTi [fdreader.segment][each] = ti				
			else:
				ti = self.segTi [fdreader.segment][each]
			
			if self.tfidf and typeinfo.typemap.isscorable (ti.type):
				self.scorable = 1
				if type (ti.value) is str:
					terms = [ti]
				else:
					terms = ti.value
				
				for each in terms:
					k = (each.value, each.num)
					if k in dup: 
						dup [k] += 1
						continue
												
					try:
						self.termDF [k] += each.df
					except KeyError:
						self.termDF [k] = each.df
						
					dup [k] = 1
				
	def collect (self, expression, lang):
		for segment in self.segments:
			if segment.numDoc == 0:
				continue
			
			try:
				fdreader = fieldreader.FieldReader (memory.get (segment), segment, self.analyzer, self.tfidf)
			except KeyError:
				continue
			
			self.segTi [fdreader.segment] = {}
			dup = {}
			self.get_terminfo (fdreader, segment, expression, lang, dup)			
			
	def isScorable (self):
		return self.scorable
				
	def getTi (self, segment, expression):
		return self.segTi [segment][expression]
	
	def getDF (self, ti):
		try:
			return self.termDF [(ti.value, ti.num)]
		except KeyError:
			return 0		
	
	def getCoord (self):		
		try:
			return list(self.coord.values ()) [0]
		except IndexError:
			return None	
		
	
class Query:
	DEBUG = 0
	CACHEPAGE = 3
	def __init__ (self, segments, qs, lang, offset, fetch, sort, analyzer, estTotal = False):
		self.segments = segments
		self.qs = qs
		self.lang = lang
		self.offset = offset
		self.fetch = fetch
		self.sort = sort
		self.analyzer = analyzer
		
		req_tfidf = (self.sort == "tfidf" or self.sort [1:] == "tfidf")
		self.terminfos = TermInfos (self.segments, self.analyzer, req_tfidf)
		self.estTotal = estTotal
		self.estRatio = None
		
		self.sortorder = 0
		self.sortindex = None
		self.sortfieldtype = None
		
		self.cachedfetch = self.offset + self.fetch
		if self.offset == 0 and self.fetch < 100:
			if len (self.segments) == 0:
				self.cachedfetch = 0
			elif len (self.segments) < self.CACHEPAGE:
				self.cachedfetch = self.fetch * self.CACHEPAGE
				if self.cachedfetch > 100: self.cachedfetch = 100
			else:
				self.cachedfetch = self.fetch * 2
				if self.cachedfetch > 100: self.cachedfetch = 100
		
		self.hits = _delune.Compute (memory.get (), req_tfidf and self.segments.si.getN () or 0)
		self.totalcount = 0
		self.duration = 0
		self.numanalyze = 0
		self.esegments = []
		self.bucket = []
		self.highlights = {}		
			
	def setSort (self):
		if self.sort:
			if self.sort [0] == "-":
				self.sortorder = -1
				self.sort = self.sort [1:]
			elif self.sort [0] == "+":
				self.sortorder = 1
				self.sort = self.sort [1:]		
			else:
				self.sortorder = -1
				
		if self.sort == "tfidf" and not self.terminfos.isScorable ():
			self.sort = None

		elif self.sort:
			type, num = self.segments.si.getFieldInfo (self.sort)
			if (typeinfo.typemap.isbit (type) or typeinfo.typemap.isint (type)) and len (self.segments):
				sp = self.segments.first ().getSortMapPointer (num) # checking sortmap
				if sp:
					self.sortfieldtype = "int"							
					self.sortindex = -1					
				else:
					self.sort = None
					
			elif type == "coord" and self.terminfos.getCoord () and len (self.segments):
				sp = self.segments.first ().getSortMapPointer (num) # checking sortmap
				if sp:
					self.sortfieldtype = "coord"
					self.sortindex = -2
				else:
					self.sort = None
			else:
				self.sort = None
							
	def getBufferSize (self, segment, size):
		hits = self.hits.count ()
		if hits == 0: return 0
		bsize = int ((self.segments.si.getSegmentNumDoc (segment.seg) / float (hits)) * size)
		if bsize > memory.get_buffer_size (): bufsize = 1024
		else: bufsize = 0
		return bufsize

	def close (self):
		del self.terminfos
		self.hits.close ()

	def setResult (self, cached):
		self.totalcount, highlights, self.bucket = cached
		for each in highlights:
			self.highlights [each] = None

	def newSegmentScan (self, segment):
		self.randomscan = 0
		self.numvaildqueryterm = 0
		self.numstopword = 0
		self.numanalyze = 0
		self.mem = memory.get (segment)
		self.hits.newscan ()

	def addHighlight (self, term):
		self.highlights [term] = None
		if len (term) < 3: return
		if ord (term [0]) >= 132: return
		
		# plural
		if term [-1] != 's':
			if term [-1] in "xz":
				self.highlights [term + 'es'] = None				
			elif term [-1] == 'y':
				if term [-2] in "aeiou":
					self.highlights [term + "s"] = None
				else:
					self.highlights [term [:-1] + "ies"] = None
			elif term [-1] == 'f':
				self.highlights [term [:-1] + "ves"] = None
				self.highlights [term + "s"] = None
			elif term [-2:] == 'fe':
				self.highlights [term [:-2] + "ves"] = None
				self.highlights [term + "s"] = None
			else:
				self.highlights [term + 's'] = None		
			
		elif len (term) >= 5 and term [-3:] == 'ies':
			self.highlights [term [:-3] + "y"] = None

		elif len (term) >= 5 and term [-3:] == 'ves':
			self.highlights [term [:-3] + "f"] = None
			self.highlights [term [:-3] + "fe"] = None

		elif len (term) >= 5 and term [-2:] == 'es' and (term [-3] in "sxz" or term [-4:-2] in ("sh", "ch")):
			self.highlights [term [:-2]] = None
			self.highlights [term [:-1]] = None

		elif term [-1] == 's':
			self.highlights [term [:-1]] = None
	
	def get_terminfo (self, segment, term):
		return self.terminfos.getTi (segment, term)
		
	def optimize (self, segment, expression):
		op = expression [0]				
		tis = [
			type (expression [1]) is str and self.get_terminfo (segment, expression [1]) or None, 
			type (expression [2]) is str and self.get_terminfo (segment, expression [2]) or None
		]
				
		#swap between operands
		if op in "*+":
			if tis [1] is None and self.hits.count ():
				tis  = [None, tis [0]] #avoid using stack
				if self.DEBUG: print("SWAP OPERAND TO RIGHT:", tis)

			# swap phrase
			elif tis [0] and tis [1]:
				if not tis [0].methology == "Phrase" and tis [1].methology == "Phrase":
					tis  = [tis [1], tis [0]]
					if self.DEBUG: print("SWAP PHRASE:", tis)

				#swap with df
				elif tis [0].methology == "TermList" and tis [1].methology == "TermList":
					if len (tis [0].value) < len (tis [1].value):
						tis = [tis [1], tis [0]]
						if self.DEBUG: print("SWAP TERMLIST:", tis)
							
					elif len (tis [0].value) and len (tis [1].value):
						if tis [0].value [0].df > tis [1].value [0].df:
							tis = [tis [1], tis [0]]
							if self.DEBUG: print("SWAP DF:", tis)
				
				#swap range
				elif typeinfo.typemap.getsize (tis [0].type) or typeinfo.typemap.getsize (tis [1].type):
					if typeinfo.typemap.getsize (tis [0].type):
						rf = tis [0]
						ff = tis [1]
					else:
						rf = tis [1]
						ff = tis [0]
					
					if not typeinfo.typemap.getsize (ff.type):						
						if ff.value and type (ff.value) is list:
							df = ff.value [0].df
						else:
							df = ff.df
						
						if df > self.segments.si.getN () / 10.0:
							tis = [rf, ff]
							if self.DEBUG: print("FORWARD RANGE:", tis)
						else:
							tis = [ff, rf]				
							if self.DEBUG: print("BACKWARD RANGE:", tis)
						
		return tis

	rx_proxdelta = re.compile ("\s*(?P<delta>\^[0-9]+)\s*")
	
	def computeTermList (self, segment, term, operator):
		if term.stopword: 
			return self.computeTerm (segment, term, operator)
			
		if not term.type: return 0
		if not term.value: return 0
		
		if len (term.value) == 1: # not term list	or phrase		
			term.value [0].readprox = 0
			return self.computeTerm (segment, term.value [0], operator)
		
		dc = 0
		self.randomscan = 0

		pushed = 0
		if self.hits.count ():
			self.hits.push ()
			pushed = 1
			if self.DEBUG: print("L-PUSH:", self.hits.saved ())
		
		if [1 for termTi in term.value if termTi.df == 0]:
			self.hits.abort ()
			dc = 0
		else:	
			for termTi in term.value:
				if term.stopword:
					continue
				self.computeTerm (segment, termTi, "*")
				dc = self.hits.intersect (termTi.near, termTi.loose)			
				if not dc: break

		if pushed:
			self.hits.popleft ()
			if self.DEBUG: print("L-POP:", self.hits.saved ())

		return dc
		
	def computeWildCard (self, segment, term, operator):
		if not term.ti: return 0

		self.randomscan = 0
		pushed = 0
		if self.hits.count ():
			self.hits.push ()
			pushed = 1
			if self.DEBUG: print("P-PUSH:", self.hits.saved ())

		for termTi in term.value:
			self.computeTerm (segment, termTi, operator)
			dc = self.hits.union ()

		if pushed:
			self.hits.popleft ()
			if self.DEBUG: print("P-POP:", self.hits.saved ())

		return dc

	def computeTerm (self, segment, term, operator):		
		if isinstance (term, fieldreader.Term) or isinstance (term, fieldreader.TermList):
			self.numanalyze += 1
			if term.stopword:
				self.numstopword += 1				
				return -1
		
		if (not term.type or not term.df):
			return 0
		
		if self.randomscan:
			if len (self.bucket) >= self.cachedfetch:
				if self.DEBUG: print("SKIP: randomscan")
				self.hits.setcount (term.df)
				return term.df

			elif segment.rd:
				self.randomscan = 0

		df, doff, poff, skip, plen = term.ti
		if (term.sp): segment.sm.read (self.mem, self.getBufferSize (segment, term.sp [1]), *term.sp) # needn't for f type

		if self.randomscan:
			if self.DEBUG: print("RANDOM SCAN")
			segment.readPosting (self.mem, df, doff, poff, skip, plen, 0, self.cachedfetch, term.readprox)
			self.hits.setcount (term.df)

		else:
			if self.DEBUG: print("FULL SCAN")
			segment.readPosting (self.mem, df, doff, poff, skip, plen, -1, -1, term.readprox)
		
		if operator != "-" and typeinfo.typemap.hasnorm (term.type):
			if term.qstr:
				for hk in term.qstr.split ():
					self.addHighlight (hk)
					
		t =  self.hits.set (self.terminfos.getDF (term), self.segments.si.getWeight (term.name))		
		return t

	def computeCoord (self, segment, term, operator):
		if not term.value: return 0
		latitude, longitude, distance = term.value
		
		segment.sm.read (self.mem, self.getBufferSize (segment, term.sp [1]), *term.sp)
		return self.hits.distance (latitude, longitude, distance, operator.encode ("utf8"), 1)

	def computeDigit (self, segment, term, operator):
		if not term.value: return 0

		a, b = term.value
		if b in ("all", "any", "none"):
			smfunc = self.hits.bit
		else:
			smfunc = self.hits.between
		
		segment.sm.read (self.mem, self.getBufferSize (segment, term.sp [1]), *term.sp)

		if not (a == -1 and (b == -1 or b in ("all", "any", "none"))):
			self.randomscan = 0

		if self.randomscan:
			wholes = segment.getNumDoc ()  - segment.getDeletedCount ()
			self.hits.setcount (wholes)

			if len (self.bucket) >= self.cachedfetch:
				return wholes
			
			dc = smfunc (a, b, operator.encode ("utf8"), (b not in ("all", "any", "none") and self.sort == term.name) and 1 or 0, self.cachedfetch + segment.getDeletedCount ())
			return wholes

		else:			
			return smfunc (a, b, operator.encode ("utf8"), (b not in ("all", "any", "none") and self.sort == term.name) and 1 or 0, -1)

	def compute (self, segment, expression):		
		if self.DEBUG: print("EXPRESSION", expression)
		record_count = 0
		got_stopwords = 0
		#---------------------------------------------------------------------------------
		# Single Query Term
		#---------------------------------------------------------------------------------
		if type (expression) is str: # only 1 term
			ti = self.get_terminfo (segment, expression)
			record_count = getattr (self, "compute" + ti.methology) (segment, ti, "*")
			if self.DEBUG: print("SINGLE QUERY:", ti, record_count)
			return None
		
		#---------------------------------------------------------------------------------
		# Optimize inner query for saving stack
		#---------------------------------------------------------------------------------
		if expression [0] != "-" and type (expression [1]) == str and type (expression [2]) == list:
			op, lop, rop = expression [0], expression [2], expression [1]
		else:
			op, lop, rop = expression
		
		#---------------------------------------------------------------------------------
		# Recursive Compute
		#---------------------------------------------------------------------------------
		if type (lop) is list:
			lop = self.compute (segment, lop)
			
			if self.numvaildqueryterm and self.hits.count () == 0 and op in "*-":
				if self.DEBUG: print("ABORT")
				self.hits.abort () # need not proceed
				return None

		if type (rop) is list:
			rop = self.compute (segment, rop)
		
		#---------------------------------------------------------------------------------
		# Optimize
		#---------------------------------------------------------------------------------
		lop, rop = self.optimize (segment, [op, lop, rop])
		
		#---------------------------------------------------------------------------------
		# Left Operand
		#---------------------------------------------------------------------------------
		if lop:
			if self.hits.count ():
				self.hits.push ()
				if self.DEBUG: print("PUSH:", self.hits.saved ())
	
			record_count = getattr (self, "compute" + lop.methology) (segment, lop, "*") # left operator is always "*"
			if record_count != -1: self.numvaildqueryterm += 1
			if self.DEBUG: print("LQUERY:", lop, record_count)
			if not record_count	and op in "-*":
				if self.DEBUG: print("ABORT")
				self.hits.abort () #need not proceed
				return None
			
			elif record_count == -1: #stop word
				if op == "-":
					if self.DEBUG: print("ABORT (- op. but stopword)")
					self.hits.abort ()
					return None
				got_stopwords = 1

		#---------------------------------------------------------------------------------
		# Right Operand
		#---------------------------------------------------------------------------------
		if rop:
			record_count = getattr (self, "compute" + rop.methology) (segment, rop, op)
			if self.DEBUG: print("RQUERY:", rop, record_count, rop.methology)
			if record_count != -1: self.numvaildqueryterm += 1
			if not record_count:
				if op in "*": # + or - is keep hits
					if self.DEBUG: print("ABORT")
					self.hits.abort ()
					return
			
			elif record_count == -1:				
				got_stopwords = 1
			
			if rop.methology in ("Coord", "Digit"): # already quick operated.
				return None
		
		elif self.hits.saved ():
			if lop is None:
				self.hits.popleft ()
				if self.DEBUG: print("POPLEFT:", self.hits.saved ())
		
			else:
				self.hits.popright ()
				if self.DEBUG: print("POPRIGHT:", self.hits.saved ())
		
		#---------------------------------------------------------------------------------
		# Operate
		#---------------------------------------------------------------------------------
		if got_stopwords: # not need operation
			return None
		
		if self.DEBUG:
			print("START OPERATE:", op, lop, rop)
				
		if op == "*":
			record_count = self.hits.intersect ()
		elif op == "+":
			record_count = self.hits.union ()
		elif op == "-":	
			record_count = self.hits.trim ()

		if self.DEBUG: print("OPERATED:", record_count)
		return None
		
	def merge (self):
		if self.sortindex:
			if self.sortorder == 1:
				self.bucket.sort (key = lambda x: x[self.sortindex])				
			elif self.sortorder == -1:				
				self.bucket.sort (key = lambda x: x[self.sortindex], reverse = True)				

		highlights = list(self.highlights.keys ())
		highlights.sort (key = lambda x: len (x), reverse = True)		
		#rx_highlights  = re.compile ("(^| )(?P<match>" + "|".join (highlights) + ")($| )", re.I)

	def query (self):
		s = time.time ()		
		if not len (self.segments): return			
		try:
			tokens = querylexer.QueryLexer (self.qs).tokenize ()			
			expression = queryparser.ArithmeticParser (tokens).parse_expression()			
			# collecting all term infos
			self.terminfos.collect (expression, self.lang)			
		except:
			raise			
		
		# set sorting options
		self.setSort ()
		
		for segment in self.segments:
			if segment.numDoc == 0:
				continue
			try:
				self.newSegmentScan (segment)
				# 1 term and no sort and has freq data
				if not self.sort and type (expression) is str:
					self.randomscan = 1
				self.query_segment (segment, expression)
				
			except IOError:
				#self.esegments.append (segment.seg)
				self.segments.si.trace ()
		
		if self.DEBUG: print("ANALYZED: %d STOPWORD: %d" % (self.numanalyze, self.numstopword))
		if self.numanalyze and self.numstopword == self.numanalyze:
			self.bucket = []
			self.totalcount = 0
			return

		if self.DEBUG: print("Total Result:", self.totalcount)

		self.duration = int ((time.time () - s) * 1000) #ms
		self.merge ()
			
	def query_segment (self, segment, expression):
		#-------------------------------------------------------------------------------
		# skip extra fetching when no sort with estimate-total option
		#-------------------------------------------------------------------------------
		if not self.sort and len (self.bucket) >= self.cachedfetch and self.estRatio is not None:
			self.totalcount += int (segment.getNumDoc () * self.estRatio)
			return
			
		#-------------------------------------------------------------------------------
		# operate
		#-------------------------------------------------------------------------------
		self.compute (segment, expression)
		
		#-------------------------------------------------------------------------------
		# calculating estimate ratio
		#-------------------------------------------------------------------------------
		if self.estTotal:
			if self.estRatio is None:
				self.estRatio = float (self.hits.count ()) / segment.getNumDoc ()
			else:
				self.estRatio = (self.estRatio + (float (self.hits.count ()) / segment.getNumDoc ())) / 2.
		
		#-------------------------------------------------------------------------------
		# skip extra fetching when no sort
		#-------------------------------------------------------------------------------
		if not self.sort and len (self.bucket) >= self.cachedfetch:
			count = self.hits.count ()
			self.totalcount += count
			return
		
		#-------------------------------------------------------------------------------
		# forcely coordination setting
		#-------------------------------------------------------------------------------
		if self.terminfos.getCoord ():
			coord = self.terminfos.getCoord ()			
			type, num = self.segments.si.getFieldInfo (coord.name)
			sp = segment.getSortMapPointer (num) # checking sortmap
			if sp:
				pointer, vsize = sp
				segment.sm.read (self.mem, self.getBufferSize (segment, vsize), pointer, vsize)
				self.hits.sortset_coord (coord.value [0], coord.value [1])
		
		#-------------------------------------------------------------------------------
		# sorting
		#-------------------------------------------------------------------------------
		bysortkey = 0
		byextra = 0
		if self.sort and self.sort != "tfidf":
			if self.sortfieldtype == "int":
				type, num = self.segments.si.getFieldInfo (self.sort)
				sp = segment.getSortMapPointer (num) # checking sortmap			
				if sp:
					pointer, vsize = sp
					segment.sm.read (self.mem, self.getBufferSize (segment, vsize), pointer, vsize)
					self.hits.sortset_key ()
					bysortkey = 1
										
			elif self.sortfieldtype == "coord":				
				byextra = 1
		
		want = self.cachedfetch
		self.hits.sort (want, self.sortorder, bysortkey, byextra)

		#-------------------------------------------------------------------------------
		# select from hit docs
		#-------------------------------------------------------------------------------
		bucket = self.hits.hitdoc (segment.seg, want, segment.getBits ())
		self.bucket +=  bucket

		#-------------------------------------------------------------------------------
		# counting hitdoc
		#-------------------------------------------------------------------------------
		count = self.hits.count ()
		self.totalcount += count

		if self.DEBUG: 
			print("#" * 79)
			print("Segment Result:", count)
			print("#" * 79)
