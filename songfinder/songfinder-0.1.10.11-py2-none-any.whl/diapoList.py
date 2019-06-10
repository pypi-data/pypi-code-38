# -*- coding: utf-8 -*-
from __future__ import division

import Tkinter as tk
import time

from songfinder.elements import elements
from songfinder import globalvar
from songfinder import classDiapo
from songfinder import exception
from songfinder import classSettings as settings

class DiapoList(object):
	def __init__(self, elementList=[], guiUpdate=None):
		self._elementList = [element for element in elementList if element]
		self._emptyDiapo = classDiapo.Diapo(elements.Element(), 0, settings.GENSETTINGS.get('Syntax', 'newslide')[0], 90)
		self._diapos = []
		self._element2diapo = [0]
		self._lenght = 0
		self._num = 0
		self._upToDate = False

		self._guiUpdate = guiUpdate

	def getList(self, elementNum=None):
		if not self._upToDate and self._elementList:
			previous = 'empty'
			for i, element in enumerate(self._elementList):
				if element.etype != 'image' or previous != 'image':
					self._diapos += [self._emptyDiapo]
				self._diapos += element.diapos
				self._element2diapo.append(len(self._diapos))
				previous = element.etype
			self._diapos += [self._emptyDiapo]
			self._lenght = len(self._diapos)

		if elementNum is not None:
			self._num = self._element2diapo[elementNum]
		self._upToDate = True
		return self._diapos

	def __len__(self):
		if self._lenght == 0:
			self.getList()
		return self._lenght

	def prefetch(self, themes, callback=None, args=[]):
		tmp = time.time()
		self.getList()
		for diapo in reversed(self._diapos):
			diapo.prefetch(themes, text=False)
			if callback:
				callback(*args)
		print('Image prefetching time: %f'%(time.time()-tmp))

	def _getFromNum(self, num):
		if num < len(self) and num >= 0:
			output = self._diapos[num]
		else:
			output = self._emptyDiapo
		return output

	@property
	def current(self):
		return self._getFromNum(self._num)

	@property
	def next(self):
		return self._getFromNum(self._num+1)

	@property
	def nextnext(self):
		return self._getFromNum(self._num+2)

	@property
	def previous(self):
		return self._getFromNum(self._num-1)

	def incremente(self):
		self._num = min(self._num+1, self._lenght-1)
		if self._guiUpdate:
			self._guiUpdate()

	def decremente(self):
		self._num = max(self._num-1, 0)
		if self._guiUpdate:
			self._guiUpdate()

	@property
	def number(self):
		return self._num

	@number.setter
	def number(self, num):
		if num >= len(self) and num < 0:
			raise exception.DiapoError(num)
		self._num = num

	def setElem(self, elementNum):
		num = self._element2diapo[elementNum]
		if num >= len(self) and value < 0:
			raise exception.DiapoError(num)
		self._num = num

	def bindGuiUpdate(self, guiUpdate):
		self._guiUpdate = guiUpdate
