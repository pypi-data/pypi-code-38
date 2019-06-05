from ... import _delune
from ... import util
from . import segmentwriter
from . import fieldwriter
import types

class WDocument:
	def __init__ (self, docId, si, fw, analyzer):
		self.docId = docId
		self.si = si
		self.fw = fw
		self.analyzer = analyzer
		self.stored = []
		self.summary = ""

	def addField (self, type, name, value, lang, option = []):
		num = self.si.setFieldInfo (name, type)
		self.fw (type, self.docId, num, name, value, lang, option)

	def setData (self, contents):
		self.stored = [util.serialize (content) for content in contents]		
	
	def addSummary (self, summary, lang, option = []):
		self.summary = summary		
		if self.analyzer:
			self.summary = fieldwriter.translate (self.analyzer, summary, lang, option)		
		assert type (self.summary) is str


class IndexWriter:
	def __init__ (self, si, analyzer):
		self.si = si
		self.analyzer = analyzer
		self.tcache = {}

		self.fw = None
		self.segment = None
		self.newSegment ()

	def close (self):
		if self.segment:
			self.segment.close ()
		self.segment = None

	def newSegment (self):
		self.segment = segmentwriter.SegmentWriter (self.si)
		self.fw = fieldwriter.FieldWriter (self.segment, self.analyzer)

	def getNumDoc (self):
		return self.segment.numDoc

	def getMemUsage (self):
		return self.segment.getMemUsage ()

	def newWDocument (self):
		docId = self.segment.newdocid ()
		d = WDocument (docId, self.si, self.fw, self.analyzer)
		return d

	def addWDocument (self, d):		
		self.segment.writeField (d.stored, d.summary)
		d = None

	#---------------------------------------------------------------------------
	# flushing
	#---------------------------------------------------------------------------
	def flush (self, final):
		if self.segment:
			self.segment.flush ()
			self.segment = None

		if not final:
			self.newSegment ()
