# -*- coding: utf-8 -*-
from __future__ import division

import Tkinter as tk
import tkFont
import ttk
from songfinder import messages as tkMessageBox
import os
import threading
import sys
import traceback

from songfinder import globalvar
from songfinder import versionning as version
from songfinder import latex
from songfinder.elements import elements
from songfinder import preferences as pref
from songfinder import fonctions as fonc
from songfinder import commandLine
from songfinder import classPaths
from songfinder import exception
from songfinder import search
from songfinder import dataBase
from songfinder import background
from songfinder import themes
from songfinder import screen
from songfinder import classDiapo
from songfinder import simpleProgress
from songfinder import searchGui
from songfinder import editGui
from songfinder import selectionListGui
from songfinder import presentGui
from songfinder import diapoListGui
from songfinder import classSettings as settings


class Interface(object, tk.Frame):
	def __init__(self, fenetre, screens=None, fileIn=None, **kwargs):
		tk.Frame.__init__(self, fenetre, **kwargs)

		self._screens = screens
		self._fenetre = fenetre

		if screens[0][0].w < 1000:
			fontSize = 8
		else:
			fontSize = 9
		for font in ["TkDefaultFont", "TkTextFont", "TkFixedFont", "TkMenuFont"]:
			tkFont.nametofont(font).configure(size=fontSize)

		mainmenu = tk.Menu(fenetre)  ## Barre de menu
		menuFichier = tk.Menu(mainmenu)  ## tk.Menu fils menuExample
		menuFichier.add_command(label="Mettre à jour la base de données", \
						command = self.updateData )
		menuFichier.add_command(label="Mettre à jour SongFinder", \
						command = self._updateSongFinder )
		menuFichier.add_command(label="Quitter", \
						command=self.quit)
		mainmenu.add_cascade(label = "Fichier", \
						menu = menuFichier)

		menuEditer = tk.Menu(mainmenu)
		menuEditer.add_command(label="Paramètres généraux", \
						command = self._paramGen )
		menuEditer.add_command(label="Paramètres de présentation", \
						command = self._paramPres )
		mainmenu.add_cascade(label = "Editer", menu = menuEditer)

		menuSync = tk.Menu(mainmenu)
		menuSync.add_command(label="Envoyer les chants", \
						command = self._sendSongs )
		menuSync.add_command(label="Recevoir les chants",\
						command = self._recieveSongs )
		mainmenu.add_cascade(label = "Réception/Envoi", \
						menu = menuSync)

		menuLatex = tk.Menu(mainmenu)
		menuLatex.add_command(label="Générer les fichiers Latex",\
						command = lambda noCompile=1: self._writeLatex(noCompile) )
		menuLatex.add_command(label="Compiler les fichiers Latex",\
						command = self._compileLatex )
		mainmenu.add_cascade(label = "Latex", menu = menuLatex)

		menuHelp = tk.Menu(mainmenu)
		menuHelp.add_command(label="README",command = self._showREADME )
		menuHelp.add_command(label = "Documentation", command = self._showDoc)
		mainmenu.add_cascade(label = "Aide", menu = menuHelp)

		fenetre.config(menu=mainmenu)

		self._generalParamWindow = None
		self._presentationParamWindow = None
		self._latexWindow = None

		self._scrollWidget = None

		leftPanel = ttk.Frame(fenetre)
		searchPanel = ttk.Frame(leftPanel)
		listPanel = ttk.Frame(leftPanel)
		editPanel = ttk.Frame(fenetre)
		rightPanel = ttk.Frame(fenetre)
		previewPanel = ttk.Frame(rightPanel)
		presentPanel = ttk.Frame(rightPanel)
		pdfPanel = ttk.Frame(rightPanel)
		self._presentedListPanel = ttk.Frame(fenetre)

		searchPanel.pack(side=tk.TOP, fill=tk.X)
		listPanel.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

		leftPanel.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
		editPanel.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
		rightPanel.pack(side=tk.LEFT, fill=tk.X)
		previewPanel.pack(side=tk.TOP)
		presentPanel.pack(side=tk.TOP, fill=tk.X)
		pdfPanel.pack(side=tk.TOP, fill=tk.X)

		# Preview panel
		if screens[0][0].w < 2000:
			self._previewSize = 300
		else:
			self._previewSize = 400
		ratio = screen.getRatio(settings.GENSETTINGS.get('Parameters', 'ratio'))
		self._themePres = themes.Theme(previewPanel, \
						width=self._previewSize, height=self._previewSize/ratio)
		self._themePres.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
		emptySlide = classDiapo.Diapo(elements.Element(), 0, \
						settings.GENSETTINGS.get('Syntax', 'newslide')[0], 20)
		emptySlide.printDiapo(self._themePres)
		#######

		####### Path definition
		classPaths.PATHS.update()
		classPaths.PATHS.sync(self)
		try:
			self._repo = version.Repo(classPaths.PATHS.root, 'hg', True, self, screen=screens[0][0])
		except exception.CommandLineError:
			tkMessageBox.showerror(u'Erreur', traceback.format_exc())
		self._dataBase = dataBase.DataBase()
		searcher = search.Searcher(self._dataBase)

		# Modular panels
		self._editGui = editGui.EditGui(editPanel, dataBase=self._dataBase, screens=screens)
		self._selectionListGui = selectionListGui.SelectionListGui(listPanel)
		self._searchGui = searchGui.SearchGui(searchPanel, searcher, self._dataBase, screens=screens)
		self._presentGui = presentGui.PresentGui(presentPanel, screens=screens)
		listGui = diapoListGui.DiapoListGui(self._presentedListPanel)
		#######

		# Modular panels bindings
		self._editGui.bindPrinterCallback(self._printPreview)
		self._editGui.bindSaveCallback(self._resetTextAndCache)
		self._editGui.bindSetSong(self._searchGui.setSong)
		self._selectionListGui.bindPrinter(self._editGui.printer)
		self._selectionListGui.bindSearcher(searcher.search)
		self._selectionListGui.bindListUpdateCallback(self._presentGui.loadDiapoList)
		self._searchGui.bindPrinter(self._editGui.printer)
		self._searchGui.bindAddElementToSelection(self._selectionListGui.addElementToSelection)
		self._presentGui.bindElementToPresent(self._editGui.printedElement)
		self._presentGui.bindListToPresent(self._selectionListGui.list)
		self._presentGui.bindNumDiapoStart(self._selectionListGui.num)
		self._presentGui.bindCallback(self._printPreview)
		self._presentGui.bindDiapoListGui(listGui)
		#######

		createPDFButton = tk.Button(pdfPanel, \
							text='Générer un PDF', \
							command=self._quickPDF)
		createPDFButton.pack(side=tk.TOP, fill=tk.X)
		# List present panel
		#######

		self._expanded = False
		self._expandDiapoListGuiButton = tk.Button(pdfPanel, \
							text='>>', \
							command=self._expandDiapoListGui)
		self._expandDiapoListGuiButton.pack(side=tk.TOP, fill=tk.X)

		self.bind_all('<Enter>', self._bound_to_mousewheel)
		self.bind_all('<Leave>', self._unbound_to_mousewheel)

		self.focus_set()


		# ~ backColor = '#F0F0F0'
		# ~ self.configure(background=backColor)
		# ~ for item in fonc.all_children(self):
			# ~ if item.winfo_class() == 'Label' or item.winfo_class() == 'Radiobutton':
				# ~ item['bg'] = backColor
			# ~ elif item.winfo_class() == 'Text' or item.winfo_class() == 'Entry':
				# ~ item['bg'] = 'white'
			# ~ elif item.winfo_class() == 'tk.Button' or item.winfo_class() == 'tk.Menu':
				# ~ item['bg'] = '#FFFBF5'

		# Open file in argument
		if fileIn:
			fileIn = os.path.abspath(fileIn)
			ext = fonc.get_ext(fileIn)
			if ext in settings.GENSETTINGS.get('Extentions', 'chant'):
				element = elements.Chant(fileIn)
				if element.exist():
					self._searchGui.addsong(element)
					self._editGui.printer(toPrintDict={element:100})
			elif ext in settings.GENSETTINGS.get('Extentions', 'liste'):
				self._selectionListGui.setList(fileIn)


		fenetre.attributes("-alpha", 1)
		fenetre.lift()

	def _expandDiapoListGui(self):
		if self._expanded:
			self._presentedListPanel.pack_forget()
			self._expandDiapoListGuiButton["text"] = '>>'
			self._expanded = False
		else:
			self._presentedListPanel.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
			self._expandDiapoListGuiButton["text"] = '<<'
			self._expanded = True
		self._fenetre.update()
		self._resizeMainWindow()

	def _resizeMainWindow(self):
		width = max(self._fenetre.winfo_width(), self._fenetre.winfo_reqwidth())
		height = max(self._fenetre.winfo_height(), self._fenetre.winfo_reqheight())
		self._fenetre.geometry( screen.get_size(width, height, self._screens[0][0], 100) )

	def closeLatexWindow(self):
		if self._latexWindow:
			self._latexWindow.destroy()
			self._latexWindow = None

	def liftLatexWindow(self):
		self._latexWindow.lift()

	def _resetTextAndCache(self):
		if self._searchGui:
			self._searchGui.resetCache()
			self._searchGui.resetText()
		if self._selectionListGui:
			self._selectionListGui.resetText()

	def _printPreview(self):
		self._themePres.resize(self._previewSize, self._previewSize/self._presentGui.ratio)
		toPrint = self._editGui.printedElement()
		if toPrint:
			try:
				toPrint.diapos[0].printDiapo(self._themePres)
			except IndexError:
				pass

	def _bound_to_mousewheel(self, event):
		self._scrollWidget = event.widget
		self.bind_all("<MouseWheel>", self._on_mousewheel)

	def _unbound_to_mousewheel(self, event):
		self._scrollWidget = None
		self.unbind_all("<MouseWheel>")

	def _on_mousewheel(self, event):
		try:
			self._scrollWidget.focus_set()
			self._scrollWidget.yview_scroll(-1*(event.delta//8), "units")
		except AttributeError:
			pass

	def updateData(self):
		progressBar = simpleProgress.SimpleProgress(self, \
							"Mise à jour de la base de données", \
							screens=self._screens)
		total = len(self._dataBase) if len(self._dataBase) != 0 else 1000
		progressBar.start(total=total)
		self._dataBase.update(progressBar.update)
		self._selectionListGui.getSetList()
		self._searchGui.resetText()
		self._selectionListGui.resetText()
		self._searchGui.resetCache()
		self._editGui.resetText()
		self._editGui.printer()
		progressBar.stop()
		tkMessageBox.showinfo('Confirmation', 'La base de donnée a '
							'été mise à jour: %d chants.'%len(self._dataBase))

	def quit(self):
		try:
			settings.GENSETTINGS.write()
			settings.PRESSETTINGS.write()
			settings.LATEXSETTINGS.write()
		except Exception:
			tkMessageBox.showerror('Attention', \
					'Error while writting settings:\n%s'%traceback.format_exc())
		try:
			background.cleanDiskCacheImage()
		except Exception:
			tkMessageBox.showerror('Attention', \
					'Error in clean cache:\n%s'%traceback.format_exc())
		self.destroy()
		sys.exit()

	def _paramGen(self):
		if self._generalParamWindow:
			self._generalParamWindow.destroy()
			self._generalParamWindow = None
		self._generalParamWindow = tk.Toplevel(self)
		self._generalParamWindow.title('Paramètres généraux')
		self._generalParamWindow.resizable(width=True, height=True)
		self._generalParamWindow.wm_attributes("-topmost", 1)
		self._generalParamWindow.update_idletasks()
		paramGen = pref.ParamGen(self._generalParamWindow, self)

	def _paramPres(self):
		if self._presentationParamWindow:
			self._presentationParamWindow.destroy()
			self._presentationParamWindow = None
		self._presentationParamWindow = tk.Toplevel(self)
		self._presentationParamWindow.title('Paramètres de présentation')
		self._presentationParamWindow.resizable(width=True, height=True)
		self._presentationParamWindow.wm_attributes("-topmost", 1)
		self._presentationParamWindow.update_idletasks()
		paramPres = pref.ParamPres(self._presentationParamWindow, self)
		self._searchGui.resetDiapo()
		self._selectionListGui.resetDiapo()

	def _writeLatex(self, noCompile=0):
		chants_selection = self._selectionListGui.list()
		if chants_selection == []:
			tkMessageBox.showerror('Attention', \
						"Il n'y a aucun chants dans la liste.")
			return 1

		if self._latexWindow:
			self._latexWindow.destroy()
			self._latexWindow = None
		self._latexWindow = tk.Toplevel()
		self._latexWindow.title('Paramètres Export PDF')
		self._latexWindow.resizable(width=True, height=True)
		self._latexWindow.lift()
		self._latexWindow.update_idletasks()
		self.LatexParam = latex.LatexParam(self._latexWindow, chants_selection, self, noCompile)

	def _compileLatex(self):
		latexCompiler = latex.CreatePDF([])
		latexCompiler.compileLatex()

	def _quickPDF(self):
		self._writeLatex()

	def _showDoc(self):
		docPath = os.path.join(globalvar.dataPath, 'documentation')
		docFile = os.path.join(docPath, '%s.pdf'%globalvar.appName)
		if not os.path.isfile(docFile):
			fileToCompile = os.path.join(docPath, '%s.tex'%globalvar.appName)
			if os.path.isfile(fileToCompile):
				os.chdir(docPath)
				pdflatex = commandLine.MyCommand('pdflatex')
				pdflatex.checkCommand()
				code, out, err = pdflatex.run(options=[fileToCompile, '&&', fileToCompile], timeOut=10)
				os.chdir(globalvar.chemin_root)
				if code != 0:
					tkMessageBox.showerror('Attention', \
							'Error while compiling latex files. '
							'Error %s:\n%s'%(str(code), err))
					return 1
		if os.path.isfile(docFile):
			commandLine.run_file(docFile)
		else:
			tkMessageBox.showerror(u'Attention', u'Impossible d\'ouvrire '
								'la documentation, le fichier "%s" n\'existe pas.'%docFile)

	def _showREADME(self):
		fileName = 'README.md'
		pathsReadme = [os.path.join(globalvar.dataPath, fileName), \
						os.path.join(fileName)]
		found = False
		for readmeFile in pathsReadme:
			if os.path.isfile(readmeFile):
				commandLine.run_file(readmeFile)
				found = True
				break
		if not found:
			tkMessageBox.showerror(u'Attention', u'Impossible d\'ouvrire '
								'le fichier README, le fichier "%s" n\'existe pas.'%', '.join(pathsReadme))

	def _sendSongs(self):
		self._repo.send()

	def _recieveSongs(self):
		if self._repo.receive() == 0:
			self.updateData()

	def _updateSongFinder(self):
		pip = commandLine.MyCommand('pip')
		try:
			pip.checkCommand()
		except commandLine.CommandLineError:
			tkMessageBox.showerror(u'Erreur', traceback.format_exc())
		else:
			progressBar = simpleProgress.SimpleProgress(self, \
								"Mise à jour de SongFinder", \
								screens=self._screens, mode='indeterminate')
			progressBar.start()
			progressBar.update()
			code, out, err = pip.run(options=['install %s --upgrade'%globalvar.appName], timeOut=60)
			if code != 0:
				tkMessageBox.showerror('Attention', \
						'Error while updating SongFinder. '
						'Error %s:\n%s'%(str(code), err))
			else:
				tkMessageBox.showinfo('Confirmation', 'SongFinder a '
									'été mis à jour et va être fermé.')
				sys.exit()
			progressBar.stop()
