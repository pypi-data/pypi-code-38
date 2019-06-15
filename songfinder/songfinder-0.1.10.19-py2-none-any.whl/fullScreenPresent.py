# -*- coding: utf-8 -*-
from __future__ import division

import tkFont
import Tkinter as tk
import math
import warnings
import time
import traceback
import gc
import copy

from songfinder import elements
from songfinder import screen
from songfinder import globalvar
from songfinder import classDiapo
from songfinder import themes
from songfinder import simpleProgress
from songfinder import diapoListGui
from songfinder import diapoList
from songfinder import classSettings as settings


class Presentation(object):
	def __init__(self, frame, screens=None, closeCallback=None, \
					listDiapos=diapoList.DiapoList(), \
					startingElement=0, **kwargs):
		tmpsTotal=time.time()
		self._closeCallback = closeCallback
		self._frame = frame

		# Fenetre de presentation
		self._presentationWindow = tk.Toplevel(frame)
		self._presentationWindow.withdraw()
		self._presentationWindow.title("Presentation")
		if globalvar.myOs == 'ubuntu':
			self._presentationWindow.attributes("-fullscreen", True)
		else:
			self._presentationWindow.overrideredirect(1)
		self._presentationWindow.protocol("WM_DELETE_WINDOW", self.quit)

		if not screens:
			screens = screen.Screens() ## very Slow
		else:
			screens.update()

		if len(screens) > 1:
			self._myScreen = copy.copy(screens[1][0])
		else:
			self._myScreen = copy.copy(screens[0][0])

		inputRatio = screen.getRatio(settings.GENSETTINGS.get('Parameters', 'ratio'), self._myScreen.ratio)
		self._presentationWindow.geometry(self._myScreen.full)
		if inputRatio != 0:
			self._myScreen.set_w( int(math.floor(min(inputRatio*self._myScreen.h, self._myScreen.w))) )
			self._myScreen.set_h( int(math.floor(min(self._myScreen.w//inputRatio, self._myScreen.h))) )

		self._themePres = themes.Theme(self._presentationWindow, width=self._myScreen.w, height=self._myScreen.h, bg='black')
		self._themePres.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
		listToPrefetch = [self._themePres]

		globalBindings = {"<Left>":self._previousSlide, \
						"<Right>":self._nextSlide, \
						"<Prior>":self._previousSlide, \
						"<Next>":self._nextSlide, \
						"<Escape>":self.quit}
		self._bindingsObjects = {key:frame.bind_all(key, value) for key,value in globalBindings.items()}
		self._presentationWindow.bind("<Up>", self._previousSlide)
		self._presentationWindow.bind("<Down>", self._nextSlide)
		self._presentationWindow.bind("<Button-1>", self._nextSlide)
		self._presentationWindow.bind("<Button-3>", self._previousSlide)

		self.loadList(listDiapos, startingElement)
		###
		self._presentationWindow.deiconify()
		self._presentationWindow.focus_set()
		print("Temps creation presentation " + str(time.time()-tmpsTotal))

	def loadList(self, listDiapos, startingElement=0):
		self._listDiapos = listDiapos
		self._listDiapos.getList(startingElement)
		self.printer()

	def _previousSlide(self, event):
		self._listDiapos.decremente()
		self.printer()

	def _nextSlide(self, event):
		self._listDiapos.incremente()
		self.printer()

	def printer(self):
		diapo = self._listDiapos.current
		if self._themePres.name != diapo.themeName:
			self._themePres.destroy()
			self._themePres = themes.Theme(self._presentationWindow, diapo.etype, width=self._myScreen.w, height=self._myScreen.h)
			self._themePres.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
		diapo.printDiapo(self._themePres)
		self._prefetcher()

	def _prefetcher(self):
		themes = []
		themes.append(self._themePres)
		self._listDiapos.previous.prefetch(themes)
		self._listDiapos.next.prefetch(themes)

	def quit(self, event=None):
		for key,value in self._bindingsObjects.items():
			self._frame.unbind(key, value)
		self._listDiapos = None
		self._presentationWindow.destroy()
		self._presentationWindow = None
		if self._closeCallback:
			self._closeCallback()
		print('GC collected objects : %d' % gc.collect())
