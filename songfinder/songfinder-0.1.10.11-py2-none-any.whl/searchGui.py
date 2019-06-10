# -*- coding: utf-8 -*-
from __future__ import division

import Tkinter as tk
from songfinder import messages as tkMessageBox
import os

from songfinder import globalvar
from songfinder import fonctions as fonc
from songfinder import inputFrame
from songfinder.elements import elements

class SearchGui(object):
	def __init__(self, frame, searcher, dataBase=None, screens=None, \
				addElementToSelection=None, printer=None):

		self._printer = printer
		self._songFound = []
		self._searcher = searcher
		# database is only needed to delete elements
		self._dataBase = dataBase

		self._addElementToSelection = addElementToSelection

		self._priorityMultiplicator = 1

		if screens and screens[0][0].w > 2000:
			width=46
		else:
			width=30

		self._inputSearch = inputFrame.entryField(frame, width=width, text="Recherche: ")
		explainLabel = tk.Label(frame, text="Chants trouvés: \n"
								"Utilisez leur numéro dans la liste pour les selectionner")
		self._searchResults = tk.Listbox(frame, width=width, height=9)

		self._inputSearch.pack(side=tk.TOP, fill=tk.X, expand=1)

		explainLabel.pack(side=tk.TOP, fill=tk.X)
		self._searchResults.pack(side=tk.TOP, fill=tk.X, expand=1)
		self._searchResults.bind("<ButtonRelease-1>", self._printerWrapper)
		self._searchResults.bind("<Double-Button-1>", lambda event, mouseClic=1: \
												self._select(event, mouseClic))
		self._searchResults.bind("<KeyRelease>", self._select)
		self._searchResults.bind("<KeyRelease-Up>", self._printerWrapper)
		self._searchResults.bind("<KeyRelease-Down>", self._printerWrapper)
		self._searchResults.bind("<Delete>", self._deleteSong)

		self._inputSearch.bind("<KeyRelease>", self._search)
		self._inputSearch.bind("<KeyRelease-BackSpace>", self._nothing)
		self._inputSearch.bind("<KeyRelease-Left>", self._nothing)
		self._inputSearch.bind("<KeyRelease-Right>", self._nothing)
		self._inputSearch.bind("<KeyRelease-Up>", self._nothing)
		self._inputSearch.bind("<KeyRelease-Down>", self._nothing)

		self._inputSearch.focus_set()

	def _printerWrapper(self, event=None):
		if self._printer:
			self._printer(event=event, toPrintDict=self.elementsToPrint)

	def _search(self, event):
		#~ self.timer.cancel()
		#~ self.timer = threading.Timer(0.1, self._searchCore, [event])
		#~ self.timer.start()
		self._priorityMultiplicator = 10
		self._searchCore(event)
		self._priorityMultiplicator = 1

	def _searchCore(self, event):
		if self._inputSearch.get():
			searchInput = fonc.safeUnicode(self._inputSearch.get())
			self._songFound = self._searcher.search(searchInput)
			self._showResults()
		self._select(event)
		self._printerWrapper(event)

	def _showResults(self):
		self._searchResults.delete(0,'end')
		for i,song in enumerate(self._songFound):
			self._searchResults.insert(i, '%s -- %s'%(str(i+1), str(song)))

	def _select(self, event, mouseClic=0):
		if self._addElementToSelection:
			numbers = [str(i) for i in range(1,10)]
			# For ubuntu num lock wierd behaviour
			toucheNumPad = event.keycode
			if globalvar.myOs == "ubuntu":
				listNumPad = [87, 88, 89, 83, 84, 85, 79, 80, 81]
			else:
				listNumPad = []
			if not self._inputSearch.get().isdigit():
				if toucheNumPad in listNumPad:
					keyboardInput = str(listNumPad.index(toucheNumPad) + 1)
				else:
					keyboardInput = event.keysym
			else:
				keyboardInput = None
			if mouseClic == 1 and self._searchResults.curselection():
				keyboardInput = str(int(self._searchResults.curselection()[0])+1)
			if keyboardInput in numbers:
				if int(keyboardInput) < self._searchResults.size()+ 1:
					element = self._songFound[int(keyboardInput)-1]
					self._addElementToSelection(element)
				self._inputSearch.delete(0, tk.END)
				self._inputSearch.focus_set()

	def _deleteSong(self, event):
		if self._dataBase and self._searchResults.curselection():
			select = self._searchResults.curselection()[0]
			toDelete = self._songFound[select]
			if tkMessageBox.askyesno('Confirmation', \
						'Etes-vous sur de supprimer '
						'le chant:\n"%s" ?'%toDelete.nom):
				path = toDelete.chemin
				if os.path.isfile(path):
					os.remove(path)
				self._dataBase.remove(toDelete)
				self._searcher.resetCache()
				if toDelete in self._songFound:
					self._songFound.remove(toDelete)
				self._showResults()
				self._printerWrapper()

	def _nothing(self,event=0):
		pass

	def setSong(self, song):
		self._songFound = [song]
		self._showResults()

	def resetCache(self):
		self._searcher.resetCache()

	def resetText(self):
		for song in self._songFound:
			song.resetText()

	def resetDiapo(self):
		for element in self._songFound:
			del element.diapos[:]

	@property
	def elementsToPrint(self):
		outDictElements = {}
		if self._searchResults.curselection() and self._songFound:
			select = self._searchResults.curselection()[0]
			toAdd = self._songFound[select]
			outDictElements[toAdd] = 18*self._priorityMultiplicator
		if self._searchResults.size() > 0 and self._songFound: # ValueError None
			toAdd = self._songFound[0]
			outDictElements[toAdd] = 6*self._priorityMultiplicator
		return outDictElements

	def bindAddElementToSelection(self, function):
		self._addElementToSelection = function

	def bindPrinter(self, function):
		self._printer = function
