# -*- coding: utf-8 -*-

import time

from songfinder import corrector
from songfinder import fonctions as fonc
from songfinder import cache

class Searcher(object):
	def __init__(self, dataBase, **kwargs):
		self._dataBase = dataBase
		self._correctors = dict()
		self._cache = cache.Cache(100, self._search)
		self._correctorModes = ['lyrics', 'titles']
		for mode in self._correctorModes:
			singles = ';'.join((sets[0] for sets in self._dataBase.getDico(mode).values()))
			couples = ';'.join((sets[1] for sets in self._dataBase.getDico(mode).values()))
			self._correctors[mode] = corrector.Corrector(singles, couples)
		self._tolerance =  0.3

	def search(self, toSearch):
		if not toSearch.isdigit():
			self._toSearch = fonc.netoyage_paroles(toSearch)
		else:
			self._toSearch = toSearch
		# ~ tmps1=time.time()
		self._toSearch = self._correctors['lyrics'].check(self._toSearch)
		# ~ print('temps corrections %ss'%(time.time()-tmps1))
		return self._cache.get(self._toSearch, args=[self._toSearch])

	def _search(self, toSearch): # Use of caching
		if toSearch.isdigit():
			try:
				num = int(toSearch)
				return list(self._dataBase.getDico('nums')[num])
			except KeyError:
				print('KeyError: %s'%toSearch)
				pass
		self._songDict = self._dataBase.getDico('lyrics')
		self._found = self._dataBase.songsList
		self._modeSearch('lyrics')
		if len(self._found) > 20:
			self._modeSearch('titles')
		return self._found[:9]

	def _modeSearch(self, mode):
		self._toSearchList = self._toSearch.split(' ')
		self._tolerance =  0.3

		if len(self._found) != 1:
			self._keyWordSearch(1)
			if len(self._toSearchList) > 1 and len(self._found) > 5:
				self._keyWordSearch(2)
			if len(self._toSearchList) > 2 and len(self._found) > 5:
				self._keyWordSearch(3)
			if len(self._toSearchList) > 1 and len(self._found) > 5:
				self._tolerance = 0.2
				self._keyWordSearch(2)
			if len(self._toSearchList) > 1 and len(self._found) > 5:
				self._tolerance = 0.1
				self._keyWordSearch(2)
			if len(self._toSearchList) > 2 and len(self._found) > 5:
				self._keyWordSearch(3)

	def _keyWordSearch(self, nbWords):
		dico_taux = dict()
		toSearchSet = set()
		plusieurs_mots = []
		for i,mot in enumerate(self._toSearchList):
			plusieurs_mots.append(mot)
			if i > nbWords-2:
				toSearchSet.add(' '.join(plusieurs_mots))
				plusieurs_mots = plusieurs_mots[1:]
		taux_max = 0
		for song in self._found:
			refWords = self._songDict[song.nom][nbWords-1]
			refSet = set(refWords.split(';'))
			taux = float(len(toSearchSet &  refSet))/len(toSearchSet)

			try:
				dico_taux[taux].append(song)
			except KeyError:
				dico_taux[taux] = [song]

			if taux > taux_max:
				taux_max = taux

		self._found = []
		taux_ordered = sorted(dico_taux.viewkeys(), reverse=True)
		for taux in taux_ordered:
			if taux > taux_max-self._tolerance-float(nbWords)/10:
				self._found += sorted(dico_taux[taux])

	def resetCache(self):
		self._cache.reset()
		for corrector in self._correctors.values():
			corrector.resetCache()
