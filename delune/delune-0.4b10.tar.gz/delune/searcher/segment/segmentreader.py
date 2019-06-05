from . import segment
from delune import _delune
import os

class Term:
	def __init__ (self, term, fdno, df, frqPosition, prxPosition, skipDelta, prxLength):
		self.term = term
		self.fdno = fdno
		self.df = df
		self.frqPosition = frqPosition		
		self.prxPosition = prxPosition		
		self.skipDelta = skipDelta		
		self.prxLength = prxLength		
	
	def __lt__ (self, other):
		return self.fdno == other.fdno and self.term < other.term or self.fdno < other.fdno
	
	def __eq__ (self, other):
		return self.fdno == other.fdno and self.term == other.term
		
	def __cmp__ (self, other):
		if self.fdno == other.fdno:
			return cmp (self.term, other.term)	
		else:
			return cmp (self.fdno, other.fdno)	
		
	def __repr__ (self):
		return "<Term %s: %d>" % (self.term, self.fdno)
			

class SegmentReader (segment.Segment):
	def __init__ (self, si, seg):
		self.si = si
		segment.Segment.__init__ (self, si.fs.get (seg), seg, 'r', self.si.plock, version = self.si.version)
	
	def readPosting (self, mem, df, doff, poff, skip, plen, zoff = -1, zlen = -1, getprox = 0):		
		return self.tf.read (mem, df, doff, poff, skip, plen, zoff, zlen, getprox)
	
	def getNumDoc (self):
		return self.numDoc
	
	def getSortMapPointer (self, fdno):
		if self.si.getType (fdno) is None: 
			return -1
		
		self.si.getSortMapFields () # create cache
		
		pointer = 0		
		i = 0
		while 1:
			n, s = self.si.cache_sortmap [i]
			if n == fdno: break
			pointer += self.numDoc * s
			i += 1
		
		return pointer, s
		
	def getDeletedCount (self):
		if self.rd: return self.rd.count ()
		else: return 0
			
	def getBits (self):
		return self.rd and self.rd.getbits () or None
			
	def getDocument (self, mem, docId, summary = 0, terms = None, nthdoc = 0):
		return self.fd.read (mem, docId, summary, terms or [], nthdoc)		
		
	def getTermInfo (self, mem, term, fdno):
		return self.ti.get (mem, term [:100], fdno)
	
	def getTermInfos (self, mem, term, fdno):
		return self.ti.get_wildcard (mem, term [:100], fdno)		
	
	def getTermInfos2 (self, mem, terms, fdno):
		return self.ti.get_range (mem, terms [0], terms [1], fdno)
				
	def delete (self, docid):
		if self.rd is None:
			self.create_bitvector ()
		else:
			self.reload_deleted ()
		self.rd.set (docid)
		
	
class SegmentBulkReader (SegmentReader):
	def __init__ (self, si, seg):
		self.si = si
		segment.Segment.__init__ (self, si.fs.get (seg), seg, 'm', version = self.si.version)
	
	def getMergeInfo (self):
		return ( 
			self.numDoc, 
			self.fs_tfq,
			self.fs_prx, 
			self.fs_fdi, 
			self.fs_fda, 
			self.fs_smp,
			self.rd and self.rd.getbits () or None
		)	
	
	def advanceTermInfo (self):		
		ti = self.ti.advance ()
		return Term (*ti)
		