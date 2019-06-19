# -*- coding: utf-8 -*-
#cython: language_level=2

from Tkinter import *
import os
import xml.etree.cElementTree as ET

# ~ from src.fonctions import *
from songfinder import gestchant
from songfinder import classPaths
from songfinder import fonctions as fonc
from songfinder import globalvar
from songfinder import classSettings as settings

class class_versets(object, Frame):
	def __init__(self, fenetre, papa, **kwargs):
		Frame.__init__(self, fenetre, **kwargs)
		self.grid()
		self.fenetre = fenetre
		self.paths = classPaths.PATHS
		self.chemin_bibles = self.paths.bibles
		self.papa = papa

		self.screen_w = fenetre.winfo_screenwidth()
		self.screen_h = fenetre.winfo_screenheight()

		self.testament = IntVar()
		self.testament.set(1)
		self.filename = StringVar(self)
		self.liste_livres = Listbox(self, width=18, height=15, selectmode='single')
		self.liste_chap1 = Listbox(self, width=6, height=15, selectmode='single')
		self.liste_chap2 = Listbox(self, width=6, height=15, selectmode='single')
		self.liste_vers1 = Listbox(self, width=6, height=15, selectmode='single')
		self.liste_vers2 = Listbox(self, width=6, height=15, selectmode='single')
		self.text = Text(self, width=66, height=14)
		self.de = Label(self, text="de:")
		self.a = Label(self, text="à:")
		self.chapitre1 = Label(self, text="chapitre")
		self.verset1 = Label(self, text="verset")
		self.chapitre2 = Label(self, text="chapitre")
		self.verset2 = Label(self, text="verset")

		self.liste_bibles = Listbox(self, width=5, height=5, selectmode='single')
		self.ancien = Radiobutton(self, text="Ancien testament", variable=self.testament, value=0, command=self.affiche_livres)
		self.nouveau = Radiobutton(self, text="Nouveau testament", variable=self.testament, value=1, command=self.affiche_livres)
		self.bouton_select = Button(self, text='Sélectionner', command = self.papa.selectVers, state=NORMAL)

		self.livre = -1
		self.chap1 = 0
		self.chap2 = 0
		self.vers1 = 0
		self.vers2 = 0
		self.verset = 0

		self.liste_livres.bind("<ButtonRelease-1>", self.affiche_chap1)
		self.liste_chap1.bind("<ButtonRelease-1>", self.affiche_vers1)
		self.liste_vers1.bind("<ButtonRelease-1>", self.affiche_chap2)
		self.liste_chap2.bind("<ButtonRelease-1>", self.affiche_vers2)
		self.liste_vers2.bind("<ButtonRelease-1>", self.affiche_text)

		self.scroll_livre = Scrollbar(self, command=self.liste_livres.yview)
		self.scroll_chap1 = Scrollbar(self, command=self.liste_chap1.yview)
		self.scroll_chap2 = Scrollbar(self, command=self.liste_chap2.yview)
		self.scroll_vers1 = Scrollbar(self, command=self.liste_vers1.yview)
		self.scroll_vers2 = Scrollbar(self, command=self.liste_vers2.yview)
		self.scroll_text = Scrollbar(self, command=self.text.yview)

		self.liste_livres['yscrollcommand'] = self.scroll_livre.set
		self.liste_chap1['yscrollcommand'] = self.scroll_chap1.set
		self.liste_chap2['yscrollcommand'] = self.scroll_chap2.set
		self.liste_vers1['yscrollcommand'] = self.scroll_vers1.set
		self.liste_vers2['yscrollcommand'] = self.scroll_vers2.set
		self.text['yscrollcommand'] = self.scroll_text.set

		self.text.grid(row=16, column=0, rowspan=20, columnspan=26, sticky='w')
		self.scroll_text.grid(row=16, column=26, rowspan=20, sticky='nsew')

		self.liste_bibles.grid(row=0, column=0, rowspan=4, columnspan=3, sticky='w')
		self.ancien.grid(row=0, column=3, rowspan=1, columnspan=7, sticky='nsew')
		self.nouveau.grid(row=1, column=3, rowspan=1, columnspan=7, sticky='nsew')
		self.bouton_select.grid(row=15, column=8, columnspan=10, sticky='w')

		self.liste_livres.grid(row=2, column=3, columnspan=7, rowspan=13)
		self.scroll_livre.grid(row=2, column=10, rowspan=13, sticky='nsew')

		self.de.grid(row=0, column=12, columnspan=3, rowspan=1)
		self.chapitre1.grid(row=1, column=11, columnspan=3, rowspan=1)
		self.liste_chap1.grid(row=2, column=11, columnspan=2, rowspan=13)
		self.scroll_chap1.grid(row=2, column=13, rowspan=13, sticky='nsew')
		self.verset1.grid(row=1, column=15, columnspan=3, rowspan=1)
		self.liste_vers1.grid(row=2, column=15, columnspan=2, rowspan=13)
		self.scroll_vers1.grid(row=2, column=17, rowspan=13, sticky='nsew')
		self.a.grid(row=0, column=20, columnspan=3, rowspan=1)
		self.chapitre2.grid(row=1, column=19, columnspan=3, rowspan=1)
		self.liste_chap2.grid(row=2, column=19, columnspan=2, rowspan=13)
		self.scroll_chap2.grid(row=2, column=21, rowspan=13, sticky='nsew')
		self.verset2.grid(row=1, column=23, columnspan=3, rowspan=1)
		self.liste_vers2.grid(row=2, column=23, columnspan=2, rowspan=13)
		self.scroll_vers2.grid(row=2, column=25, rowspan=13, sticky='nsew')

		self.liste_bibles.delete(0,'end')
		for root, dirs, files in os.walk(self.chemin_bibles):
			for i,fichier in enumerate(sorted(files)):
				self.liste_bibles.insert(i, fonc.get_file_name(fichier))

		self.liste_bibles.select_set(2)
		self.parse()

		self.liste_bibles.bind("<ButtonRelease-1>", self.parse)
		self.liste_bibles.bind("<KeyRelease-Up>", self.parse)
		self.liste_bibles.bind("<KeyRelease-Down>", self.parse)
		self.text.delete(1.0, END)
		self.select_state()

	def parse(self, event=0):
		self.version = self.liste_bibles.get(self.liste_bibles.curselection()[0])
		chemin = os.path.join(self.chemin_bibles, self.version \
					+ settings.GENSETTINGS.get('Extentions', 'bible')[0])
		self.tree_bible = ET.parse(chemin)
		self.bible = self.tree_bible.getroot()
		self.affiche_livres()
		self.affiche_text()

	def affiche_livres(self, event=0):
		self.liste_livres.delete(0,'end')
		if self.testament.get():
			for i,livre in enumerate(self.bible[39:]):
				self.liste_livres.insert(i, livre.attrib['n'])
		else:
			for i,livre in enumerate(self.bible[:39]):
				self.liste_livres.insert(i, livre.attrib['n'])

	def affiche_chap1(self, event=0):
		if self.liste_livres.curselection():
			self.livre = int(self.liste_livres.curselection()[0]) + self.testament.get()*39
			self.liste_livres.selection_clear(0, 'end')
			self.liste_chap1.delete(0,'end')
			for i,chap in enumerate(self.bible[self.livre][:]):
				self.liste_chap1.insert(i, chap.attrib['n'])
			self.affiche_vers1()


	def affiche_chap2(self, event=0):
		if self.liste_vers1.curselection():
			self.vers1 = int(self.liste_vers1.curselection()[0])
		elif self.liste_livres.curselection() or self.liste_chap1.curselection():
			self.vers1 = 0
		self.liste_chap2.delete(0,'end')
		for i,chap in enumerate(self.bible[self.livre][self.chap1:self.chap1+2]):
			self.liste_chap2.insert(i, chap.attrib['n'])
		self.affiche_vers2()

	def affiche_vers1(self, event=0):
		if self.liste_chap1.curselection():
			self.chap1 = int(self.liste_chap1.curselection()[0])
		elif self.liste_livres.curselection():
			self.chap1 = 0
		self.liste_vers1.delete(0,'end')
		for i,vers in enumerate(self.bible[self.livre][self.chap1][:]):
			self.liste_vers1.insert(i, vers.attrib['n'])
		self.affiche_chap2()

	def affiche_vers2(self, event=0):
		if self.liste_chap2.curselection():
			self.chap2 = int(self.liste_chap2.curselection()[0])+self.chap1
		elif self.liste_vers1.curselection():
			self.chap2 = self.chap2
		else:
			self.chap2 = self.chap1
		self.liste_vers2.delete(0,'end')
		for i,vers in enumerate(self.bible[self.livre][self.chap2][self.vers1*(self.chap1==self.chap2):]):
			self.liste_vers2.insert(i, vers.attrib['n'])
		self.affiche_text()

	def affiche_text(self, event=0):
		if self.liste_vers2.curselection():
			self.verset = 1
			self.vers2 = int(self.liste_vers2.curselection()[0])+self.vers1*(self.chap1==self.chap2)
		elif self.liste_chap2.curselection():
			self.vers2 = 0
		if self.chap1 > self.chap2:
			self.chap2 = self.chap1
		if self.chap1 == self.chap2 and self.vers2 < self.vers1:
			self.vers2 = self.vers1

		self.text.delete(1.0, END)

		if self.chap1==self.chap2:
			for i,text in enumerate(self.bible[self.livre][self.chap1][self.vers1:self.vers2+1]):
				self.text.insert(INSERT,'  ' + str(self.vers1+i+1) + '  ' + text.text+'')
		else:
			self.text.insert(INSERT,'  Chapitre ' + str(self.chap1+1) +'\n')
			for i,text in enumerate(self.bible[self.livre][self.chap1][self.vers1:]):
				self.text.insert(INSERT, '  ' + str(self.vers1+i+1) + '  ' + text.text+'')
			self.text.insert(INSERT,'\n  Chapitre ' + str(self.chap2+1) +'\n')
			for i,text in enumerate(self.bible[self.livre][self.chap2][:self.vers2+1]):
				self.text.insert(INSERT, '  ' + str(i+1) + '  ' + text.text+'')

		self.select_state()

	def select_state(self):
		text = self.text.get(1.0, END)
		text = text.replace('\n', ' ')
		text = gestchant.nettoyage(text)
		if text:
			self.bouton_select.config(state=NORMAL)
		else:
			self.bouton_select.config(state=DISABLED)

	def quit(self):
		self.bible = None
		self.fenetre.destroy()
