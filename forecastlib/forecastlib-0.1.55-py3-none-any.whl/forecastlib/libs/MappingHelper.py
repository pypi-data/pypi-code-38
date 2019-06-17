import re

import pandas as pd


class MappingHelper(object):
	def __init__(self):
		self.interval_re = re.compile("[\(\[]\s*(-?\d+.?\d*)\s*,\s*(-?\d+.?\d*)\s*[\)\]]")

	def to_interval(self, s: str):
		match = self.interval_re.search(s)
		if match is None or match.groups().__len__() != 2:
			return None
		return pd.Interval(int(match.group(1)), int(match.group(2)))

	def try_interval(self, s):
		if type(s) is not str:
			return s
		interval = self.to_interval(s)
		if interval is None:
			return s
		return interval

	def is_interval(self, s):
		if type(s) is not str:
			return False

		res = self.interval_re.match(s)

		return res is not None

	def map_interval_value(self, val, m):
		for k in m.keys():
			if int(val) in k:
				return m[k]

		return None

	def map_interval(self, collection, m):
		return list(map(lambda x: self.map_interval_value(x, m), collection))
