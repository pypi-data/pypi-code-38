# -*- coding: utf-8 -*-
from __future__ import division

import Tkinter as tk
import ttk
from songfinder import messages as tkMessageBox
from songfinder import messages as tkFileDialog
import os
import copy
import traceback
import gc

from songfinder import globalvar
from songfinder import fonctions as fonc
from songfinder import elements
from songfinder import classSet
from songfinder import exception
from songfinder import classVersets
from songfinder import classSettings as settings

#~ try:
	#~ import vlc_player
	#~ vlc = 1
#~ except:
	#~ warnings.warn('VLC not found')
	#~ vlc = 0
vlc = 0

class SelectionListGui(object):
	def __init__(self, frame, path=None, screens=None, \
				searchFuntion=None, printer=None, listUpdateCallback=None):

		self._verseWindow = None
		self._set = classSet.Set()
		self._searchFuntion = searchFuntion
		self._printer = printer
		self._listUpdateCallback = listUpdateCallback
		self._path = path

		self._priorityMultiplicator = 1
		self._curSelection = -1
		self._setName = ''

		lisButtonSubPanel = ttk.Frame(frame)
		listSubPanel = ttk.Frame(frame)

		lisButtonSubPanel.pack(side=tk.TOP, fill=tk.X)
		listSubPanel.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

		self._saveButton = tk.Button(lisButtonSubPanel, \
								text='Sauver', \
								command=self._saveSet, \
								state=tk.DISABLED)
		self._deleteSetButton = tk.Button(lisButtonSubPanel, \
								text='Suppr', \
								command=self._deleteSet, \
								state=tk.DISABLED)

		self._upButton = tk.Button(lisButtonSubPanel, \
								text='Monter', \
								command=self._up, state=tk.DISABLED)
		self._downButton = tk.Button(lisButtonSubPanel, \
								text='Descendre', \
								command=self._down, state=tk.DISABLED)
		self._deleteElemButton = tk.Button(lisButtonSubPanel, \
								text='Suppr', \
								command=self._deleteElem, state=tk.DISABLED)
		self._clearButton = tk.Button(lisButtonSubPanel, \
								text='Initialiser', \
								command=self._clear, state=tk.DISABLED)

		nameLabel = tk.Label(lisButtonSubPanel, text="Liste: ")

		self._setList = []
		setSelectionVar	= tk.StringVar()
		self._setSelection	= ttk.Combobox(lisButtonSubPanel, \
								textvariable = setSelectionVar, \
								values = self._setList, \
								state = 'readonly', width=20)

		addMediaButton = tk.Button(lisButtonSubPanel, \
								text='Ajouter\nMedias', \
								command=self._addMedia)
		if vlc == 0:
			addMediaButton.config(state=tk.DISABLED)
		addImageButton = tk.Button(lisButtonSubPanel, \
								text='Ajouter\nImages', \
								command=self._addImage)
		addVerseButton = tk.Button(lisButtonSubPanel,\
								text='Ajouter\nVersets', \
								command=self._addVers)

		if screens and screens[0][0].w > 2000:
			width=46
		else:
			width=30

		self._listboxElem = tk.Listbox(listSubPanel, width=width)
		listboxElemScroll = tk.Scrollbar(listSubPanel, command=self._listboxElem.yview)
		self._listboxElem['yscrollcommand'] = listboxElemScroll.set

		nameLabel.grid(row=0, column=0, columnspan=2, rowspan=1)
		self._setSelection.grid(row=0, column=2, columnspan=6)
		self._saveButton.grid(row=0, column=8, columnspan=2)
		self._deleteSetButton.grid(row=0, column=10, columnspan=2)

		addMediaButton.grid(row=1, column=6, columnspan=2, rowspan=2)
		addImageButton.grid(row=1, column=8, columnspan=2, rowspan=2)
		addVerseButton.grid(row=1, column=10, columnspan=2, rowspan=2)

		self._upButton.grid(row=1, column=0, columnspan=3)
		self._downButton.grid(row=2, column=0, columnspan=3)
		self._deleteElemButton.grid(row=1, column=3, columnspan=3)
		self._clearButton.grid(row=2, column=3, columnspan=3)

		self._listboxElem.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
		listboxElemScroll.pack(side=tk.LEFT, fill=tk.Y)

		self._setSelection.bind("<<ComboboxSelected>>", self._selectSet)
		self._listboxElem.bind("<ButtonRelease-1>", self._selectSong)
		self._listboxElem.bind("<KeyRelease-Up>", self._selectSong)
		self._listboxElem.bind("<KeyRelease-Down>", self._selectSong)
		self._listboxElem.bind("<u>", self._up)
		self._listboxElem.bind("<d>", self._down)
		self._listboxElem.bind("<Delete>", self._deleteElem)

		self.getSetList()
		if settings.GENSETTINGS.get('Parameters', 'autoload') == 'oui':
			if len(self._setList) > 0:
				self._setSelection.set(self._setList[0])


		self.FILETYPES = [ ("All files", "*.*"), ]
		self.FILETYPES_video = [(ext[1:].upper(), ext) for ext in \
					settings.GENSETTINGS.get('Extentions', 'video')] + [("All files", "*.*")]
		self.FILETYPES_audio = [(ext[1:].upper(), ext) for ext in \
					settings.GENSETTINGS.get('Extentions', 'audio')] + [("All files", "*.*")]
		self.FILETYPES_image = [(ext[1:].upper(), ext) for ext in \
					settings.GENSETTINGS.get('Extentions', 'image')] + [("All files", "*.*")]
		self.FILETYPES_present = [(ext[1:].upper(), ext) for ext in \
					settings.GENSETTINGS.get('Extentions', 'presentation')] + [("All files", "*.*")]
		self.FILETYPES_media = [("MP4", ".mp4"), ("All files", "*.*")] + \
					self.FILETYPES_video[:-1] + self.FILETYPES_audio[:-1]

		self._activeSaveButton()
		self._selectSet()

	def _selectSong(self, event=None):
		self._activeBoutons()
		if self._printer:
			self._printer(event=event, toPrintDict=self.elementsToPrint)

	def _selectSet(self, event=0):
		newSetName = self._setSelection.get()
		if newSetName:
			if self._saveButton['state'] != tk.DISABLED:
				if tkMessageBox.askyesno('Sauvegarde', \
						'Voulez-vous sauvegarder les modifications '
						'sur la liste "%s" ?'%self._setName):
					self._setSelection.set(self._setName)
					self._saveSet()
			self._setName = newSetName
			try:
				self._set.load(self._setName)
			except exception.DataReadError as e:
				tkMessageBox.showerror(u'Attention', traceback.format_exc())
				return 1
			self._updateList()
			self._selectSong()

		self._activeSaveButton()
		self._activeSupprSetButton()

	def _updateList(self):
		if self._setName != '':
			self._setSelection.set(self._setName)
		self._listboxElem.delete(0,'end')
		for i,element in enumerate(self._set):
			self._listboxElem.insert(i, str(i+1) + ' -- ' + str(element))
			if not element.exist() and self._listboxElem.itemcget(i, 'fg') != 'green':
				self._listboxElem.itemconfig(i, fg='green')

		if len(self._set) is not 0:
			self._listboxElem.yview('moveto', self._curSelection/len(self._set))
		self._listboxElem.activate(self._curSelection)
		self._activeSaveButton()
		if self._listUpdateCallback:
			self._listUpdateCallback()

	def _up(self, event=0):
		index = int(self._listboxElem.curselection()[0])
		if index > 0:
			self._set[index-1], self._set[index] \
					= self._set[index], self._set[index-1]
			self._updateList()
			self._listboxElem.activate(index-1)
			self._listboxElem.selection_set(index-1)
			self._curSelection = index-1

	def _down(self, event=0):
		index = int(self._listboxElem.curselection()[0])
		if index < len(self._set)-1:
			self._set[index+1], self._set[index] \
				= self._set[index], self._set[index+1]
			self._updateList()
			self._listboxElem.activate(index+1)
			self._listboxElem.selection_set(index+1)
			self._curSelection = index+1

	def _deleteElem(self, event=0):
		select = self._listboxElem.curselection()
		if select:
			index = int(select[0])
			del self._set[index]
			self._updateList()
			lenght = self._listboxElem.size()
			if index < lenght:
				self._listboxElem.activate(index)
				self._listboxElem.selection_set(index)
			elif lenght > 0:
				self._listboxElem.activate(lenght-1)
				self._listboxElem.selection_set(lenght-1)

	def _addMedia(self):
		medias = tkFileDialog.askopenfilenames(filetypes=self.FILETYPES_media)
		if medias:
			for media in medias:
				mediaFile = fonc.get_file_name(media)
				extention = fonc.get_ext(media)
				anwser = 1
				mediaType = settings.GENSETTINGS.get('Extentions', 'audio') \
							+ settings.GENSETTINGS.get('Extentions', 'video')
				if media and (extention not in mediaType):
					anwser = tkMessageBox.askyesno('Type de fichier', \
					'Le fichier "%s.%s" ne semble pas être un fichier audio ou vidéo. '
					'Voulez-vous continuer malgré tout ?'%(mediaFile.encode('utf-8'), \
														extention.encode('utf-8')))
				if media and anwser:
					self.addElementToSelection(elements.Element(mediaFile, 'media', media))

	def _addImage(self):
		images = tkFileDialog.askopenfilenames(filetypes=self.FILETYPES_image)
		if images:
			for full_path in images:
				mediaFile = fonc.get_file_name_ext(full_path)
				extention = fonc.get_ext(full_path)
				anwser = 1
				typeImage = settings.GENSETTINGS.get('Extentions', 'image')
				if full_path and (extention not in typeImage):
					anwser = tkMessageBox.askyesno('Type de fichier', \
					'Le fichier "%s.%s" ne semble pas être un fichier image. '
					'Voulez-vous continuer malgré tout ?'%(mediaFile.encode('utf-8'),\
														extention.encode('utf-8')))
				if full_path and anwser:
					self.addElementToSelection(elements.ImageObj(full_path))

	def _clear(self):
		if self._saveButton['state'] != tk.DISABLED:
			if tkMessageBox.askyesno('Sauvegarde', \
					'Voulez-vous sauvegarder les modifications '
					'sur la liste "%s" ?'%self._setName):
				self._setSelection.set(self._setName)
				self._saveSet()
		self._setName = ''
		self._setSelection.delete(0, tk.END)
		self._set.clear()
		self._updateList()
		self._activeSaveButton()

	def getSetList(self):
		if self._path:
			self._setList = []
			for root, dirs, files in os.walk(self._path):
				for i,fichier in enumerate(sorted(files, reverse=True)):
					self._setList.append(fonc.get_file_name(fichier))
			self._setSelection['values'] = self._setList

	def _deleteSet(self):
		if tkMessageBox.askyesno('Confirmation', \
						'Etes-vous sur de _deleteElem '
						'la liste:\n"%s" ?'%str(self._set)):
			index = self._setList.index(str(self._set))
			self._set.delete()
		self.getSetList()
		if len(self._setList) >= index:
			self._setSelection.set(self._setList[index])
			self._selectSet()
		self._activeSupprSetButton()

	def _saveSet(self):
		if self._path:
			if not self._set:
				tkMessageBox.showerror(u'Attention', u'La liste est vide')
				return 0
			if self._setSelection.get():
				self._set.setName( self._setSelection.get() )
			extention = settings.GENSETTINGS.get('Extentions', 'liste')[0]
			saveSetName = tkFileDialog.asksaveasfilename(initialdir = self._path, \
										initialfile = str(self._set), \
										defaultextension=extention, \
										filetypes=((extention + " file", "*" + extention),
										("All Files", "*.*") ))
			self._set.setName(saveSetName)
			if saveSetName != '':
				self._set.save()
				self.getSetList()
				self._activeSaveButton()
				self._setSelection.set(str(self._set))
				self._selectSet()

	def _activeSaveButton(self):
		if not self._path or not self._set.changed:
			self._saveButton.config(state=tk.DISABLED)
		else:
			self._saveButton.config(state=tk.NORMAL)

	def _activeSupprSetButton(self):
		if self._path and self._setSelection.get():
			self._deleteSetButton.config(state=tk.NORMAL)
		else:
			self._deleteSetButton.config(state=tk.DISABLED)

	def _addVers(self):
		self.closeVerseWindow()
		self._verseWindow = tk.Toplevel()
		self._verseWindow.wm_attributes("-topmost", 1)
		self._verseInterface = classverset.class_versets(self._verseWindow, self)
		self._verseWindow.title("Bible")
		self._verseWindow.update_idletasks()
		self._verseWindow.protocol("WM_DELETE_WINDOW", self.closeVerseWindow)
		w = self._verseWindow.winfo_width()
		h = self._verseWindow.winfo_height()
		self._verseWindow.resizable(False,False)
		self._verseWindow.update()

	def selectVers(self):
		try:
			passage = elements.Passage(self._verseInterface.version, \
										self._verseInterface.livre, \
										self._verseInterface.chap1, \
										self._verseInterface.chap2, \
										self._verseInterface.vers1, \
										self._verseInterface.vers2)
		except exception.DataReadError as e:
			tkMessageBox.showerror(u'Attention', traceback.format_exc())
			return 1
		else:
			self._verseInterface.select_state()
			self.addElementToSelection(passage)
			self._selectSong()

	def _activeBoutons(self):
		if self._listboxElem.curselection(): # ValueError
			self._upButton.config(state=tk.NORMAL)
			self._downButton.config(state=tk.NORMAL)
			self._deleteElemButton.config(state=tk.NORMAL)
		else:
			self._upButton.config(state=tk.DISABLED)
			self._downButton.config(state=tk.DISABLED)
			self._deleteElemButton.config(state=tk.DISABLED)

		if self._set:
			self._clearButton.config(state=tk.NORMAL)
		else:
			self._clearButton.config(state=tk.DISABLED)

	def _checkIfElementExists(self, element):
		if element and self._searchFuntion and not element.exist() and element.nom:
			cleanName = fonc.safeUnicode(element.nom)
			searchResults = self._searchFuntion(cleanName)
			if searchResults:
				tkMessageBox.showinfo('Remplacement', \
							'L\'élément "%s" est introuvable, '
							'il va être échangé par "%s".'%(element.nom, searchResults[0].nom))
				self._set[self._curSelection] = searchResults[0]
				element = searchResults[0]
			else:
				tkMessageBox.showerror('Attention', \
							'L\'élément "%s" est introuvable, '
							'il va être supprimé de la liste.'%element.nom)
				self._deleteElem()
				self._curSelection = -1
			self._updateList()
		return element

	def resetText(self):
		for song in self._set:
			try:
				song.resetText()
			except AttributeError:
				pass

	def resetDiapo(self):
		for element in self._set:
			del element.diapos[:]

	def addElementToSelection(self, element):
		self._curSelection = int(self._curSelection) + 1
		self._set.insert(self._curSelection, element)
		self._updateList()

	def closeVerseWindow(self):
		if self._verseWindow:
			self._verseInterface.quit()
			self._verseInterface = None
			self._verseWindow = None
			print('GC collected objects : %d' % gc.collect())

	def setList(self, fileIn):
		self._setSelection.set(fileIn)

	def list(self):
		return [element for element in self._set if element.exist()]

	def num(self):
		# This routine is used only for starting a presentation on a precise element
		if self._listboxElem.curselection():
			out = self._listboxElem.curselection()[0]
		else:
			out = 0
		return out

	@property
	def elementsToPrint(self):
		outDictElements = {}
		if self._listboxElem.curselection() and self._set:
			self._curSelection = int(self._listboxElem.curselection()[0])
			toAdd = self._set[self._curSelection]
			toAdd = self._checkIfElementExists(toAdd)
			outDictElements[toAdd] = 16*self._priorityMultiplicator
		if self._listboxElem.size() > 0 and self._set:
			toAdd = self._set[0]
			toAdd = self._checkIfElementExists(toAdd)
			outDictElements[toAdd] = 4*self._priorityMultiplicator
		return outDictElements

	def bindPrinter(self, function):
		self._printer = function

	def bindSearcher(self, function):
		self._searchFuntion = function

	def bindListUpdateCallback(self, function):
		self._listUpdateCallback = function
