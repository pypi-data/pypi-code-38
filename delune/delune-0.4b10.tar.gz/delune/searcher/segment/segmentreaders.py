from . import segmentreader
from ... import memory

class SegmentReaders:
	def __init__ (self, si):
		self.si = si
		self.numdel = 0
		self.segment_readers = []
		self.segment_map = {}
	
	def __len__ (self):
		return len (self.segment_readers)

	def __iter__ (self):
		return self.segment_readers.__iter__ ()
	
	def __getitem__ (self, i):
		return self.segment_map [int (i)]
	
	def first (self):
		return self.segment_readers [0]
	
	def last (self):
		return self.segment_readers [-1]
			
	def close (self):
		for reader in self.segment_readers:
			reader.close ()
			memory.remove (reader)
	
	def commit (self):
		for reader in self.segment_readers:
			reader.commit_deleted ()
			
	def remove (self, segs):
		segment_readers = []
		for reader in self.segment_readers:
			if int (reader.seg) in segs:
				self.si.log ("segment error, %s removed" % reader.seg)
				reader.close ()
				memory.remove (reader)
			else:
				segment_readers.append (reader)
		self.segment_readers = segment_readers
	
	def reload_deleted (self):
		for reader in self.segment_readers:
			reader.reload_deleted ()
		
	def load (self):
		latest_segments = self.si.getSegmentList ()
		segment_readers = []
		segment_map = {}
		
		while 1:
			try: reader = self.segment_readers.pop (0)
			except IndexError: break
			if reader.seg in latest_segments:
				reader.reload_deleted ()
				segment_readers.append (reader)
				segment_map [int (reader.seg)] = reader

			else:
				reader.close ()
				memory.remove (reader)
		
		for seg in latest_segments:
			if seg not in segment_map:
				try:
					reader = segmentreader.SegmentReader (self.si, seg)										
				except:
					self.si.log ("segment %s had been broken" % seg, "fail")
					self.si.trace ()	 # deleted by indexer?
					self.clean = 0
				else:
					self.si.log ("segment %s had been loaded" % seg)
					reader.mutex_id = memory.set (reader)
					segment_map [seg] = reader
					segment_readers.append (reader)

		segment_readers.sort (key = lambda x: int (x.seg), reverse = True)
		self.numdel = len ([_f for _f in [reader.rd for reader in segment_readers] if _f])
		self.segment_readers = segment_readers
		self.segment_map = segment_map
