# -*- coding: utf-8 -*-
from __future__ import division

# Do not import globalvar as it is imported by modules importing globalvar

class Cache(object):
	def __init__(self, tailleMax, function):
		self.__tailleMax = tailleMax
		self.__function = function
		self.__elems = dict()
		self.__hits = 0
		self.__misses = 0

	def _add(self, nom, elem):
		if len(self.__elems) >= self.__tailleMax:
			for _ in range(len(self.__elems)//3):
				self.__elems.popitem()
		self.__elems[nom] = elem

	def get(self, nom, args=[]):
		try:
			elem = self.__elems[nom]
			self.__hits += 1
		except KeyError:
			elem = self.__function(*args)
			self._add(nom, elem)
			self.__misses += 1
		return elem

	def reset(self):
		self.__elems.clear()

	def resize(self, value):
		self.__tailleMax = int(value)

	@property
	def hitMissRatio(self):
		try:
			ratio = self.__hits/(self.__misses+self.__hits)
		except ZeroDivisionError:
			ratio = float('inf')
		return ratio
