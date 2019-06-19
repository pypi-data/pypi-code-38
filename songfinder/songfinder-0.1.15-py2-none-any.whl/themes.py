# -*- coding: utf-8 -*-
from __future__ import division

import math
import Tkinter as tk
import tkFont

from songfinder import globalvar
from songfinder import background
from songfinder import cache
from songfinder import classSettings as settings

class Theme(object, tk.Frame):
	def __init__(self, fenetre, etype='empty', **kwargs):
		tk.Frame.__init__(self, fenetre, **kwargs)
		self._width = kwargs.get('width', 640)
		self._height = kwargs.get('height', 450)
		self._text = AutoSizeLabel(self, \
					justify=settings.PRESSETTINGS.get(etype, 'Justification'), bg=self['bg'])

		self._text.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

		self._previousBack = None
		self._name = 'theone'

	def resizeFont(self):
		self._text.resizeFont(self._width, self._height)

	def updateBack(self, backName, aspectRatio='loose'):
		back = background.Background(backName, self._width, self._height, aspectRatio)
		if back.name != self._previousBack:
			self._text["image"] = background.BACKGROUNDS.get(back)
			self._previousBack = back.name

	def prefetchBack(self, backName, aspectRatio='loose'):
		back = background.Background(backName, self._width, self._height, aspectRatio)
		background.BACKGROUNDS.get(back)

	def resize(self, width, height):
		self._width = width
		self._height = height
		self._text.cleanCache()

	@property
	def name(self):
		return self._name

	@property
	def text(self):
		return self._text['text']

	@text.setter
	def text(self, value):
		self._text['text'] = value

class AutoSizeLabel(object, tk.Label):
	def __init__(self, frame, **kwargs):
		tk.Label.__init__(self, frame, compound=tk.CENTER, fg='white', **kwargs)
		self._fontSize = settings.PRESSETTINGS.get('Presentation_Parameters', 'size')
		self._font = settings.PRESSETTINGS.get('Presentation_Parameters', 'font')
		self._policeCache = cache.Cache(200, self._computeSize)

	def _textWidth(self, police):
		# To be more precise all lines should be measured but it is to slow
		lignes = self['text'].split("\n")
		dictLen={len(ligne):ligne for ligne in lignes}
		ligneMax=dictLen[max(dictLen.keys())]
		return police.measure(ligneMax)

	def _textHeight(self, police):
		h_line = police.metrics("linespace")
		lignes = self['text'].split("\n")
		return len(lignes)*h_line

	def _computeSize(self, width, height):
		rapport = min(width/1920, height/1080)
		police = tkFont.Font(family=self._font, \
										size=int(math.floor(self._fontSize*rapport)), \
										weight="bold")
		try:
			resize = min(width*0.9/self._textWidth(police), \
						height*0.9/self._textHeight(police), \
						1)
		except ZeroDivisionError:
			resize = 1
		police["size"] = int(math.floor( self._fontSize*resize*rapport ))
		return police

	def resizeFont(self, width, height):
		self['font'] = self._policeCache.get(self['text'], [width, height])

	def cleanCache(self):
		self._policeCache.reset()
