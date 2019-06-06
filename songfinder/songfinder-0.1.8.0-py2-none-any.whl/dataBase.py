# -*- coding: utf-8 -*-
#cython: language_level=2
from __future__ import division

import os
import importlib
import traceback

from songfinder import globalvar

try:
	fileName = os.path.splitext( os.path.split(__file__)[1] )[0]
	module = importlib.import_module('lib.%s_%s'%(fileName, globalvar.arch))
	print("Using compiled version %s module"%fileName)
	globals().update(
		{n: getattr(module, n) for n in module.__all__} if hasattr(module, '__all__')
		else
		{k: v for (k, v) in module.__dict__.items() if not k.startswith('_')
	})
except (ImportError, NameError):
	# print(traceback.format_exc())

	import os
	import xml.etree.cElementTree as ET
	import warnings
	import time
	try:
		import cython
	except ImportError:
		pass

	try: # Windows only imports
		import win32con, win32api
	except ImportError:
		pass

	from songfinder import globalvar
	from songfinder.elements import elements
	from songfinder import classPaths
	from songfinder import fonctions as fonc
	from songfinder import classSettings as settings

	class DataBase(object):
		def __init__(self, **kwargs):
			self._sizeMax = 3
			self._fileName = os.path.join(globalvar.settingsPath, 'dataBase')
			self.update()

		def __contains__(self, value):
			return value in self._dictSongs.keys()

		def __getitem__(self, key):
			return self._dictSongs[key]

		def keys(self):
			return self._dictSongs.keys()

		def remove(self, song):
			del self._dicoLyrics[song.nom]
			del self._dicoTitles[song.nom]
			for num in song.nums.values():
				if num:
					self._dicoNums[num].remove(song)
			self._dictSongs.pop(song.nom)
			self._nbSongs = len(self._dictSongs)

		def add(self, song):
			self._dicoLyrics[song.nom] = self._getStrings('%s %s'%(song.title, song.text))
			self._dicoTitles[song.nom] = self._getStrings(song.title)
			self.addDictNums(song)
			self._dictSongs[song.nom] = song
			self._nbSongs = len(self._dictSongs)

		def addDictNums(self, song):
			for num in [num for num in song.nums.values() if num]:
				try:
					self._dicoNums[num].add(song)
				except KeyError:
					self._dicoNums[num] = set([song])

		def getDico(self, whichOne):
			if self._dicoLyrics.viewkeys() != set(self._dictSongs.keys()):
				self.update()

			if whichOne == 'lyrics':
				return self._dicoLyrics
			elif whichOne == 'titles':
				return self._dicoTitles
			elif whichOne == 'nums':
				return self._dicoNums
			else:
				warnings.warn('Don\'t know which dico to return.'
							'You asked for %s, possible values '
							'are "lyrics" and "titles".'%whichOne )

		def update(self, callback=None, args=[]):
			tmpsRef = time.time()
			self._dictSongs = dict()
			self._dicoLyrics = dict()
			self._dicoTitles = dict()
			self._dicoNums = dict()
			self._findSongs(callback, args)
			print('update dataBase', time.time()-tmpsRef)

		def _findSongs(self, callback, args):
			# tkMessageBox.showerror(u'Attention', u'Le nom de fichier du chant "%s" comporte un caractere spécial, veuillez le changer'%self.set_chants_dispo)
			chemin_chants = classPaths.Paths().songs
			extChant = settings.GENSETTINGS.get('Extentions', 'chant')[0]
			exclude = ['LSG', 'DAR', 'SEM', 'KJV', ]
			counter = 0
			if not chemin_chants:
				return []
			for root, dirs, files in os.walk(chemin_chants):
				for fichier in files:
					if (root+fichier).find(os.sep + '.') == -1 \
							and fonc.get_ext(fichier) == extChant \
							and fichier not in exclude:
						try:
							fichierClean = fonc.enleve_accents(fichier)
							if fichierClean != fichier:
								return fichier
						except TypeError:
							pass
						newChant = elements.Chant( os.path.join(root, fichier)) # About 2/3 of the time
						# ~ newChant._replaceInText('raDieux', 'radieux')
						if newChant.exist(): # About 1/3 of the time
							self._dictSongs[newChant.nom] = newChant
							self.add(newChant)
							self.addDictNums(newChant)
						if callback:
							callback(*args)
						counter += 1
			self._nbSongs = len(self._dictSongs)

		@property
		def songsList(self):
			return list(set(self._dictSongs.values()))

		def _getStrings(self, paroles):
			try:
				i = cython.declare(cython.int)
				size = cython.declare(cython.int)
				nb_mots = cython.declare(cython.int)
			except NameError:
				pass

			paroles = fonc.netoyage_paroles(paroles) # Half the time

			list_mots = paroles.split()
			nb_mots = len(list_mots)-1

			outPut = [paroles.replace(' ', ';')] # First word list can be done faster with replace
			for size in xrange(1, self._sizeMax): # Half the time
				addList = [ ' '.join(list_mots[i:i+size+1]) for i in xrange(max(nb_mots-size, 0)) ]
				addList.append( ' '.join(list_mots[-size-1:]) )
				outPut.append(';'.join(addList))
			return outPut

		def __len__(self):
			return self._nbSongs
