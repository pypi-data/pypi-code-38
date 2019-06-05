from . import segment
from . import segmentreader
from ... import _delune
import time

class SegmentMerger (segment.Segment):
	def __init__ (self, si, truncate = False):
		self.si = si
		self.truncate = truncate
		self.delay_sec, self.delay_factor = self.si.getopt (lazy_merge = (0, 3))
		if not self.delay_factor:
			self.delay_factor = 3
		newseg = self.si.getNewSegment ()
		segment.Segment.__init__ (self, si.fs.new (newseg), newseg, 'w', version = self.si.version)
		self.mergeinfo = _delune.MergeInfo ()
		self.smis = self.mergeinfo.get ()
		self.segments = []
		self.deletables = []
	
	def close (self):
		if self.mergeinfo:
			self.mergeinfo.close ()
			self.mergeinfo = None
		segment.Segment.close (self)
			
	def addSegment (self, seg):
		reader = segmentreader.SegmentBulkReader (self.si, seg)
		self.deletables.append (reader)
		if reader.numDoc and not self.truncate:
			self.segments.append (reader)
		
	def merge (self):
		self.segments.sort (key = lambda x: int (x.seg))
		
		for segment in self.segments:
			self.mergeinfo.add (*segment.getMergeInfo ())
			
		self.tf.setsmis (self.smis)	
		self.fd.setsmis (self.smis)
		self.sm.setsmis (self.smis)
		self.si.log ('merging documents...')
		self.mergeDocument ()		
		self.si.log ('merging sort maps...')
		self.mergeSortMap ()		
		self.si.log ('merging sort terms and postings...')
		self.mergeTermInfo ()
		self.flush ()
		self.si.log ('merging finished')
		
	def flush (self):
		for reader in self.deletables:
			seg = reader.seg
			reader.close ()
			self.si.removeSegment (seg)
						
		self.si.addSegment (self.seg, self.numDoc)
		self.close ()
		self.si.flush ()
		
	def mergeTermInfo (self):
		delay_factor = self.delay_factor * 10000
		slots = [None] * len (self.segments)
		i = 0
		for segment in self.segments:
			slots [i] = segment.advanceTermInfo ()
			i += 1			
		
		#slots = slots [:1]
		termnum = 0
		while 1:
			fslots = [_f for _f in slots if _f]
			if not fslots: break
			#slots = slots [:1]
			
			miti = min (fslots)			
			
			_term, _fdno = miti.term, miti.fdno			
			i = 0
			last_docid = 0
			tdf = 0
			frqposition, prxposition = self.tf.tell ()
			for ti in slots:
				if ti and miti == ti:
					tdf, skip, pskip, last_docid = self.tf.merge (i, ti.df, ti.frqPosition, ti.prxPosition, ti.prxLength, tdf, last_docid)
					try: 
						slots [i] = self.segments [i].advanceTermInfo ()					
					except IndexError: 
						slots [i] = None
				i += 1
			
			# only when has docments
			if not tdf:
				continue
				
			self.ti.add (_term, _fdno, tdf, frqposition, prxposition, skip - frqposition, pskip - prxposition) #skipdelta: skip - position
			self.tf.commit ()			
			termnum += 1
			if termnum and termnum % delay_factor == 0:
				time.sleep (self.delay_sec)
			if termnum and termnum % 500000 == 0:
				self.si.log ('..%dK terms' % (termnum / 1000))
			
	def mergeDocument (self):
		delay_factor = self.delay_factor * 1000
		for i in range (len (self.segments)):
			self.si.log ('..segment %s' % self.segments [i].seg)
			for docid in range (self.segments [i].numDoc):				
				self.numDoc += self.fd.merge (i, docid)
				if self.numDoc and self.numDoc % delay_factor == 0:
					time.sleep (self.delay_sec)
			
	def mergeSortMap (self):
		sminfos = self.si.getSortMapFields ()
		works = 0
		for fdno, _size in sminfos:
			works += 1
			self.si.log ('..%d of %d' % (works, len (sminfos)))
			for i in range (len (self.segments)):				
				pointer, size = self.segments [i].getSortMapPointer (fdno)				
				self.sm.merge (i, fdno, pointer, size)
			time.sleep (self.delay_sec)
			