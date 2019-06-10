# -*- coding: utf-8 -*-
from __future__ import division

import Tkinter as tk
import ttk
from songfinder import messages as tkMessageBox

from songfinder import globalvar
from songfinder import screen
from songfinder import background
from songfinder import diapoList
from songfinder import fullScreenPresent as pres
from songfinder import classSettings as settings

class PresentGui(object):
	def __init__(self, frame, screens=None, \
				elementToPresent=None, listToPresent=None, \
				numDiapoStart=None, callback=None):

		self._frame = frame
		self._elementToPresent = elementToPresent
		self._listToPresent = listToPresent
		self._numDiapoStart = numDiapoStart
		self._callback = callback
		self._frame = frame
		self._screens = screens

		self._presentation = None
		self._listGui = None

		self._presentListButton = tk.Button(frame, \
							text='Activer la présentation',  \
							command=self._present)
		updateListButton = tk.Button(frame, \
							text='Présentation de la liste',  \
							command=self._presentList)
		presentElementButton = tk.Button(frame, \
							text='Présentation de l\'élément selectionné', \
							command=self._presentCurrentElement)

		ratioLabel = tk.Label(frame, text='Format de l\'écran :')
		ratioList = settings.GENSETTINGS.get('Parameters', 'ratio_avail')
		self._ratioSelect	= ttk.Combobox(frame, \
								values = ratioList, \
								state = 'readonly', width=20)
		self._ratioSelect.set(settings.GENSETTINGS.get('Parameters', 'ratio'))

		self._presentListButton.pack(side=tk.TOP, fill=tk.X)
		updateListButton.pack(side=tk.TOP, fill=tk.X)
		presentElementButton.pack(side=tk.TOP, fill=tk.X)
		ratioLabel.pack(side=tk.TOP)
		self._ratioSelect.pack(side=tk.TOP)


		frame.bind_all("<F5>", self._presentList)
		frame.bind_all("<F6>", self._presentCurrentElement)
		self._ratioSelect.bind("<<ComboboxSelected>>", self._setRatio)

		self._setRatio()

	def _setRatio(self, event=0):
		ratio = self._ratioSelect.get()
		settings.GENSETTINGS.set('Parameters', "ratio", ratio)
		self._ratio = screen.getRatio(ratio)
		if self._callback:
			self._callback()

	def loadDiapoList(self, toPresent=None):
		if not self._presentation:
			if self._listToPresent and not toPresent:
				toPresent = diapoList.DiapoList(self._listToPresent())
			if self._listGui:
				self._listGui.bindDiapoList(toPresent)

	def _presentList(self):
		if not self._presentation:
			self._present()
		if self._listToPresent:
			debut = 0
			if self._numDiapoStart:
				debut = self._numDiapoStart()
			toPresent = diapoList.DiapoList(self._listToPresent())
			self._presentation.loadList(toPresent, debut)
			self.loadDiapoList(toPresent=toPresent)

	def _presentCurrentElement(self):
		if not self._presentation:
			self._present()
		if self._elementToPresent:
			toPresent = diapoList.DiapoList([self._elementToPresent()])
			self._presentation.loadList(toPresent)
			if self._listGui:
				self._listGui.bindDiapoList(toPresent)

	def _present(self, event=0):
		if self._presentation:
			self._presentation.quit()
		else:
			missingBacks = background.checkBackgrounds()
			if missingBacks != []:
				tkMessageBox.showerror('Attention', 'Les fonds d\'écran '
									'pour les types "%s" sont introuvable.'\
									%', '.join(missingBacks))
			settings.PRESSETTINGS.write()
			self._presentation = pres.Presentation(self._frame, screens=self._screens, closeCallback=self.closePresentWindow)
			if self._listGui:
				self._listGui.bindCallback(self._presentation.printer)
				# ~ self._listGui.getSelect()

			self._presentListButton['text'] = 'Désactiver la présentation'

	@property
	def ratio(self):
		return self._ratio

	def closePresentWindow(self):
		# This function is called in the presentation class
		if self._presentation:
			self._presentation = None
			if self._listGui:
				self._listGui.unBindCallback()
			self._presentListButton['text'] = 'Activer la présentation'

	def bindListToPresent(self, function):
		self._listToPresent = function

	def bindElementToPresent(self, function):
		self._elementToPresent = function

	def bindNumDiapoStart(self, function):
		self._numDiapoStart = function

	def bindCallback(self, function):
		self._callback = function

	def bindDiapoListGui(self, listGui):
		self._listGui = listGui
		if self._presentation:
			self._listGui.bindCallback(self._presentation.printer)
