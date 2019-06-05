import types
from .. import memory
from .. import util

class Fetcher:
	DEBUG = 0
	def __init__ (self, segments, bucket, summarize, highlights, returns, nthdoc, encoding = None):
		self.segments = segments
		self.bucket = bucket
		self.encoding = encoding
		
		if type (highlights) is bytes:
			self.highlights = highlights.split ("|")
		elif type (highlights) is dict:
			self.highlights = list(highlights.keys ())
		else:
			self.highlights = highlights
		
		self.returns = returns
		self.nthdoc = nthdoc
		self._returns = None
		self.summarize = summarize
		self.fetched_index = 0
		self.fetchmax = len (self.bucket)

	def close (self):
		pass

	def __fetch (self, seg, docid, extra, score):
		mem = memory.get (self.segments [seg]) #get mutex
		field, summary = self.segments [seg].getDocument (mem, docid, self.summarize, self.highlights, self.nthdoc)
		field = util.deserialize (field)
		if self.returns:
			if self._returns is None:
				self._returns = [x.strip () for x in self.returns.split (",")]
				if type (field) is list:
					self._returns = [int (x) for x in self._returns]
			nfield = []
			for i  in self._returns:
				nfield.append (field [i])
			field = nfield

		row = [field]
		if self.summarize:
			if self.encoding:
				summary = summary.encode (self.encoding)
			row.append (summary)
		else:
			row.append ("")
		row.append (seg)
		row.append (docid)
		row.append (extra)
		row.append (score)
		return row

	def fetchmany (self, count):
		result = []
		for hit in self.bucket [self.fetched_index: self.fetched_index + count]:
			field = self.__fetch (*hit)
			result.append (field)

		self.fetched_index += count
		return result

	def fetchone (self):
		if self.fetched_index >= self.self.fetchmax:
			return None

		field = self.__fetch (self.bucket [self.fetched_index] *hit)
		self.fetched_index += 1
		return field

	def fetchall (self):
		return self.fetchmany (self.fetchmax)
