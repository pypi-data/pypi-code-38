# -*- coding: utf-8 -*-
#cython: language_level=2

import os
from songfinder import messages as tkMessageBox
import Tkinter as tk
import traceback
from songfinder import messages as tkFileDialog

from songfinder import globalvar
from songfinder import versionning as version
from songfinder import exception
from songfinder import classSettings as settings

class Paths:
	def __init__(self, fenetre=None):
		self.fenetre = fenetre

	def save(self, chemin): # TODO do it better
		if chemin != '':
			try:
				f = open(chemin + 'test.test',"w")
				f.close()
				os.remove(chemin + 'test.test')
			except IOError as os.errno.EACCES:
				tkMessageBox.showerror('Erreur', 'Le chemin "%s" n\'est pas '
										'accesible en écriture, '
										'choisissez un autre répertoire.'\
										%chemin.encode('utf-8'), parent = self.fenetre)
				self.save( tkFileDialog.askdirectory(parent = self.fenetre) )
				return 1
			if os.path.isdir(chemin):
				settings.GENSETTINGS.set('Paths', 'data', chemin)
				self.root = chemin
				self.update()
			else:
				tkMessageBox.showerror('Erreur', 'Le chemin "%s" n\'existe pas.'\
										%chemin.encode('utf-8'), parent = self.fenetre)

	def update(self):
		self.root = settings.GENSETTINGS.get('Paths', 'data')
		if self.root == '' and not globalvar.unittest:
			tkMessageBox.showinfo('Répertoire', 'Aucun répertoire pour les chants et '
									'les listes n\'est configuré.\n'
									'Selectionnez ou créez un répertoire '
									'pour la base de donnés.', \
									parent = self.fenetre)
			path = tkFileDialog.askdirectory( initialdir = os.path.expanduser("~"), \
												parent = self.fenetre )
			if path:
				chemin = path
				try:
					os.makedirs(chemin)
				except OSError as os.errno.EEXIST:
					pass
				except IOError as os.errno.EACCES:
					tkMessageBox.showerror('Erreur', 'Le chemin "%s" n\'est '
											'pas accesible en ecriture, '
											'choisissez un autre répertoire.'\
											%chemin.encode('utf-8'), parent = self.fenetre)
					self.save( tkFileDialog.askdirectory(parent = self.fenetre) )
					return 1
				self.save(chemin)
			else:
				raise Exception('No data directory configured, shuting down SongFinder.')

		self.songs = os.path.join(self.root, 'songs')
		self.sets = os.path.join(self.root, 'sets')
		self.bibles = os.path.join(self.root, 'bibles')
		self.pdf = os.path.join(self.root, 'pdf')
		self.preach = os.path.join(self.root, 'preach')
		self.listPaths = [self.songs, self.sets, self.bibles, self.pdf, self.preach]

		for path in self.listPaths:
			try:
				os.makedirs(path)
			except OSError as os.errno.EEXIST:
				pass

	def sync(self, interface):
		if settings.GENSETTINGS.get('Parameters', 'sync') == 'oui' and\
			not os.path.isdir(os.path.join(self.root, '.hg')) and\
			tkMessageBox.askyesno('Sauvegarde', 'Voulez-vous définir le dépot distant ?\n'
									'Ceci supprimera tout documents présent dans "%s"'\
									%self.root.encode('utf-8')):
			fen_clone = tk.Toplevel()
			fen_clone.title("Clonage d'un dépôt")
			fen_clone.update()
			try:
				addRepo = version.AddRepo(fen_clone, self, 'hg', interface)
			except exception.CommandLineError:
				tkMessageBox.showerror('Erreur', traceback.format_exc())
		else:
			settings.GENSETTINGS.set('Parameters', 'sync', 'non')


PATHS = Paths()
