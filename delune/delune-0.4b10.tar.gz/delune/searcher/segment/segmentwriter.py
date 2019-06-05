from . import segment
from delune import _delune
import types

class SegmentWriter (segment.Segment):
	def __init__ (self, si):	
		self.si = si
		newseg = self.si.getNewSegment ()		
		segment.Segment.__init__ (self, None, -1, 'w', version = self.si.version)
		self.memUsage = 4096 #default document buffer
		self.termTable = _delune.TermTable ()
	
	def getMemUsage (self):	
		return self.memUsage + self.fd.usage ()
		
	def newdocid (self):
		if not self.opened:
			newseg = self.si.getNewSegment ()
			self.open (self.si.fs.new (newseg), newseg)
		
		docId = self.numDoc
		self.numDoc += 1
		return docId		
		
	def close (self):
		if self.termTable:
			self.termTable.close ()
			self.termTable = None
			
		segment.Segment.close (self)
			
	def writeField (self, fields, document = ""):
		self.fd.write (fields, document)
	
	def writeSortKey (self, fieldNum, fieldValue, size):
		if type (fieldValue) is list:
			self.memUsage += self.sm.addIntList (fieldNum, fieldValue, size) * size
		else:
			self.memUsage += self.sm.addInt (fieldNum, fieldValue, size) * size
	
	def writeStringSortKey (self, fieldNum, fieldValue, size):
		self.memUsage += self.sm.addShortString (fieldNum, fieldValue, size) * size
	
	def writeNorm (self, fieldNum, numTerm):
		self.memUsage += self.sm.addNorm (fieldNum, numTerm)
		
	def writePosting (self, docId, fieldNum, fieldValue, tf, pos = None):
		if len (fieldValue) > 100:
			self.si.log ("field `%d-%s` is over 100 chars, forcely truncated." % (fieldNum, fieldValue), "warn")
			fieldValue = fieldValue [:100]
		self.memUsage += self.termTable.add (fieldValue, fieldNum, docId, tf, pos)
	
	def flush (self):
		if not self.opened: return
		self.si.log ("writing %d documents to segment %s..." % (self.numDoc, self.seg))
		
		for term, fdno, posting in self.termTable:
			frqposition, prxposition = self.tf.tell ()			
			df, skip, pskip = self.tf.write (posting)
			self.ti.add (term, fdno, df, frqposition, prxposition, skip - frqposition, pskip - prxposition)
			self.tf.commit ()
		
		self.si.log ("flushed %d terms..." % self.termTable.numterm)	
		self.si.addSegment (self.seg, self.numDoc)
		self.si.log ("closing segment...")	
		self.close ()
		self.si.flush ()		
		self.si.log ("flushing done.")		
		
		