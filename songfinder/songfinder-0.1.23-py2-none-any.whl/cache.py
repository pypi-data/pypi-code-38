# -*- coding: utf-8 -*-
from __future__ import division

# Do not import globalvar as it is imported by modules importing globalvar

class Cache(object):
	def __init__(self, tailleMax, function):
		self._function = function
		self._elems = dict()
		self._hits = 0
		self._misses = 0
		self.maxSize = tailleMax

	def _add(self, nom, elem):
		if len(self._elems) >= self._maxSize:
			for _ in range(len(self._elems)//3):
				self._elems.popitem()
		self._elems[nom] = elem

	def get(self, nom, args=()):
		try:
			elem = self._elems[nom]
			self._hits += 1
		except KeyError:
			elem = self._function(*args)
			self._add(nom, elem)
			self._misses += 1
		return elem

	def reset(self):
		self._elems.clear()

	@property
	def maxSize(self):
		return self._maxSize

	@maxSize.setter
	def maxSize(self, value):
		self._maxSize = int(value)

	@property
	def hitMissRatio(self):
		try:
			ratio = self._hits/(self._misses+self._hits)
		except ZeroDivisionError:
			ratio = float('inf')
		return ratio
