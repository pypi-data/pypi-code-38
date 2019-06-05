from .. import _delune, colsetup
from .segment import typeinfo
import types
from . import searcher, indexer

class Segments (colsetup.Segments):
	def __init__ (self, alias = "", version = None):
		colsetup.Segments.__init__ (self, alias, version)
		self.N = 0
		self.lastIndexedId = 0
		self.fieldNum = -1
		self.fieldInfo = {}
		self.primary = None		
		self.weightMap = {}
		

class Collection (colsetup.CollectionSetup):
	exts = ["tfq", "prx", "del", "tii", "tis", "fda", "fdi", "smp"]
	segment_class = Segments
	
	def __init__ (self, indexdir, mode = 'r', analyzer = None, logger = None,  plock = None, ident = None, version = 1):
		colsetup.CollectionSetup.__init__ (self, indexdir, mode, analyzer, logger, plock, ident, version)
		self.cache_type = {}
		self.cache_sortmap = []
	
	def getSortMapFields (self):
		if not self.cache_sortmap:
			for type, num in list(self.segments.fieldInfo.values ()):
				tlen = typeinfo.typemap.getsize (type)
				if tlen:
					self.cache_sortmap.append ((num, tlen)) #fieldnum, size
				elif typeinfo.typemap.hasnorm (type):
					self.cache_sortmap.append ((num, 1))
						
			self.cache_sortmap.sort (key = lambda x: x[0])
				
		return self.cache_sortmap
		
	def getType (self, fdno):
		if not self.cache_type:
			for t, n in list(self.segments.fieldInfo.values ()):
				self.cache_type [n] = t
		return self.cache_type [fdno]
	
	def getTypeByName (self, fieldName):
		try: 
			return self.segments.fieldInfo [fieldName][0]
		except KeyError:
			return
	
	def setWeight (self, field, weight = 1.0):
		if type (field) is dict:
			for _name, _weight in list(field.items ()):
				self.segments.weightMap [_name] = _weight				
		else:
			self.segments.weightMap [field] = weight		
		
	def getWeight (self, fieldName):
		try:
			return float (self.segments.weightMap [fieldName])
		except KeyError:
			return 1.0		
	
	def getFieldInfo (self, fieldName):
		try:
			fieldNum = self.segments.fieldInfo [fieldName][-1]
		except KeyError:
			return "", ""
			
		fieldType = self.getType (fieldNum)		
		return fieldType, fieldNum
		
	def getFdnoByName (self, fieldName):		
		try:
			return self.segments.fieldInfo [fieldName][1]
		except KeyError:
			return
	
	def setPrimary (self, fdname):
		self.segments.primary = fdname
	
	def getPrimary (self):
		return self.segments.primary
		
	def setLastIndexedId (self, id):
		self.segments.lastIndexedId = id
		
	def getLastIndexedId (self):
		return self.segments.lastIndexedId
		
	def setFieldInfo (self, fieldName, type):
		try: 
			return self.segments.fieldInfo [fieldName][1]
		except KeyError: 
			self.segments.fieldNum += 1
			self.segments.fieldInfo [fieldName] = (type, self.segments.fieldNum)
			self.cache_type = {} # expire
			self.cache_sortmap = [] # expire
			return self.segments.fieldNum
	
	def getN (self):
		return self.segments.N
	
	def get_indexer (self, **karg):
		self.setopt (**karg)
		return indexer.Indexer (self)
	
	def get_searcher (self, **karg):
		self.setopt (**karg)
		return searcher.Searcher (self)
	
	def get_deletable_searcher (self, **karg):
		self.setopt (**karg)
		return searcher.DeletableSearcher (self)
	

		
		