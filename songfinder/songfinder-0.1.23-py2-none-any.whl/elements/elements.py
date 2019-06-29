# -*- coding: utf-8 -*-

import os
import xml.etree.cElementTree as ET
import warnings
import traceback
import string

from songfinder import gestchant
from songfinder import classPaths
from songfinder import fonctions as fonc
from songfinder import exception
from songfinder import classDiapo
from songfinder import messages as tkMessageBox
from songfinder import screen
from songfinder import creplace
from songfinder import classSettings as settings

RECEUILS = ['JEM', 'ASA', 'WOC', 'HER', 'HEG', 'FAP', 'MAR', \
			'CCO', 'PBL', 'LDM', 'JFS', 'THB', 'EHO', 'ALG', \
			'BLF', 'ALR', 'HLS', 'IMP', 'PNK', 'DNL', 'ROG', \
			'WOC', 'SOL', 'FRU', 'OST']

class Element(object):
	def __init__(self, nom='', etype='empty', chemin='', **kwargs):
		self.newline = settings.GENSETTINGS.get('Syntax', 'newline')
		self.nom = fonc.enleve_accents(nom)
		self._title = self.nom
		self._supInfo = ''
		self._ref = ''
		if nom:
			self.nom = fonc.upper_first(self.nom)

		self.etype = etype
		self.chemin = chemin
		self._diapos = []
		self._text = ''
		self._author = ''
		self._copyright = ''
		self._ccli = ''
		self._customNumber = None
		self._turfNumber = None
		self._hymnNumber = None

	def __str__(self):
		out = '%s -- %s%s %s'%(self.etype, self.ref, \
							self._turfNumber or self._hymnNumber or self._customNumber, \
							self.title)
		if self.supInfo:
			out = '%s (%s)'%(out, self.supInfo)
		return out.encode('utf-8')

	def __repr__(self):
		return repr(str(self))

	@property
	def text(self):
		return self._text

	@property
	def title(self):
		if self._title == '':
			self.text
		return self._title

	@property
	def supInfo(self):
		if self._supInfo is None:
			self.title
		return self._supInfo

	@property
	def ref(self):
		if self._ref == '':
			self.text
		if self._turfNumber:
			self._ref = 'TURF'
		return self._ref

	@property
	def transpose(self):
		return ''

	@property
	def capo(self):
		return ''

	@property
	def key(self):
		return ''

	@property
	def nums(self):
		return dict()

	@property
	def diapos(self):
		if self._diapos != []:
			return self._diapos
		# ~ self._diapos = []

		text = self.text
		text = fonc.supressB(text, '\\ac', '\n')
		ratio = screen.getRatio(settings.GENSETTINGS.get('Parameters', 'ratio'))
		max_car = int(settings.PRESSETTINGS.get('Presentation_Parameters', 'size_line')*ratio)

		listStype = []
		# La première est vide ie au dessus du premier \s
		listText, listStype = fonc.splitPerso([text], \
								settings.GENSETTINGS.get('Syntax', 'newslide'), \
								listStype, 0)
		del listText[0]
		listStypePlus = gestchant.getListStypePlus(listStype)
		# Completion des diapo vide
		diapoVide = [i for i, text in enumerate(listText) if text.find('\\...') != -1 \
								or gestchant.nettoyage(text) == '']

		plus = 0
		for index in diapoVide:
			listCandidat = gestchant.getIndexes(listStype[:index], listStype[index])
			if listCandidat != []:
				# Si plus de diapo que disponible sont demander, cela veut dire qu'il faut ducpliquer plusieur fois les diapo
				if not gestchant.getPlusNum(listStypePlus, index) > len(listCandidat):
					plus = 0
				elif plus == 0:
					plus = gestchant.getPlusNum(listStypePlus, index) - len(listCandidat)
				toTake = -gestchant.getPlusNum(listStypePlus, index)+plus
				indexCopie = listCandidat[toTake]
				if listText[index].find('\\...') != -1:
					listText[index] = listText[index].replace('\\...', listText[indexCopie])
				else:
					listText[index] = listText[indexCopie]

		nombre = len(listText)
		for i, text in enumerate(listText):
			diapo = classDiapo.Diapo(self, i+1, listStype[i], \
										max_car, nombre, text)
			self._diapos.append(diapo)
		return self._diapos

	@title.setter
	def title(self, newTitle):
		self._supInfo = ''
		if newTitle:
			if newTitle[:3] in ['JEM', 'SUP'] and newTitle[3:6].isdigit():
				newTitle = newTitle[7:]
			newTitle = newTitle.replace('\n', '')
			newTitle = newTitle.strip(' ')

			deb = self.nom.find('(')
			fin = self.nom.find(')')
			if deb != -1 and fin != -1:
				self._supInfo = self.nom[deb+1:fin]

			deb = newTitle.find('(')
			fin = newTitle.find(')')
			if deb != -1 and fin != -1:
				newTitle = newTitle[:deb] + newTitle[fin+1:]

		else:
			newTitle = ''
			self._supInfo = ''
		self._title = fonc.safeUnicode(newTitle)
		self._latexText = ''
		self._beamerText = ''
		self._markdownText = ''

	def exist(self):
		if os.path.isfile(self.chemin) and self.text:
			return 1
		else:
			return 0

	def save(self):
		pass

	def safeUpdateXML(self, xmlRoot, field, value):
		if value is not None:
			try:
				xmlRoot.find(field).text = unicode(value)
			except AttributeError:
				ET.SubElement(xmlRoot, field)
				xmlRoot.find(field).text = unicode(value)

class ImageObj(Element):
	def __init__(self, chemin, **kwargs):
		self.etype = 'image'
		Element.__init__(self, fonc.get_file_name(chemin), self.etype, chemin)

	@property
	def text(self):
		return settings.GENSETTINGS.get('Syntax', 'newslide')[0]

	def exist(self):
		if os.path.isfile(self.chemin):
			return 1
		else:
			return 0

class Passage(Element):
	def __init__(self, version, livre, chap1, chap2, vers1, vers2, **kwargs):
		Element.__init__(self)
		self.etype = 'verse'
		self.version = version
		self.chemin = os.path.join(classPaths.PATHS.bibles, version \
						+ settings.GENSETTINGS.get('Extentions', 'bible')[0])

		self.livre = livre
		self.chap1 = chap1
		self.chap2 = chap2
		self.vers1 = vers1
		self.vers2 = vers2

		self._title = None
		self._text = None
		self.__bible = None

	def _parse(self):
		if not self.__bible:
			try:
				tree_bible = ET.parse(self.chemin)
			except (OSError, IOError):
				raise exception.DataReadError(self.chemin)
			self.__bible = tree_bible.getroot()

	@property
	def text(self):
		if not self._text:
			self._parse()
			newslide = settings.GENSETTINGS.get('Syntax', 'newslide')
			newline = settings.GENSETTINGS.get('Syntax', 'newline')
			text = u''
			if self.chap1==self.chap2:
				for i,passage in enumerate(self.__bible[self.livre][self.chap1][self.vers1:self.vers2+1]):
					text = text + newslide[0] + u'\n' + unicode(self.vers1+i+1) + u'  ' \
								+ unicode(passage.text) + u'\n' + newline + '\n'
			else:
				text = text + u'Chapitre ' + unicode(self.chap1+1) + u'\n' + newline + '\n'
				for i,passage in enumerate(self.__bible[self.livre][self.chap1][self.vers1:]):
					text = text + newslide[0] + u'\n' + unicode(self.vers1+i+1) \
								+ u' ' + unicode(passage.text) + u'\n' + newline + '\n'
				text = text + u'Chapitre ' + unicode(self.chap2+1) + u'\n' + newline + '\n'
				for i,passage in enumerate(self.__bible[self.livre][self.chap2][:self.vers2+1]):
					text = text + newslide[0] + u'\n' + unicode(i+1) + u'  ' \
								+ unicode(passage.text) + u'\n' + newline + '\n'
			self._text = gestchant.nettoyage(text)

			self.title
			self.__bible = None
		return self._text

	@property
	def title(self):
		if not self._title:
			self._parse()
			title = ''
			if self.livre != -1:
				title += self.__bible[self.livre].attrib['n']\
				+ ' ' + self.__bible[self.livre][self.chap1].attrib['n']

			title += 'v' + self.__bible[self.livre][self.chap1][self.vers1].attrib['n'] + '-'
			if self.chap1!=self.chap2:
				title += self.__bible[self.livre][self.chap2].attrib['n'] + 'v'

			title += self.__bible[self.livre][self.chap1][self.vers2].attrib['n']
			self._title = fonc.enleve_accents(title)
			self.nom = self._title

			self.text
			self.__bible = None
		return self._title

class Chant(Element):
	def __init__(self, chant, nom='', **kwargs):
		self.etype = 'song'
		if fonc.get_ext(chant) == '':
			chant = chant + settings.GENSETTINGS.get('Extentions', 'chant')[0]
		self.chemin = os.path.join(chant)

		Element.__init__( self, chant, self.etype, self.chemin)
		self.nom = fonc.get_file_name(self.chemin)
		self.title = nom
		if self.nom[3:6].isdigit():
			self._ref = self.nom[:3]
			self._customNumber = int(self.nom[3:6])
		self.resetText()

	def resetText(self):
		self._text = ''
		self._transpose = None
		self._capo = None
		self._key = ''
		self._turfNumber = None
		self._hymnNumber = None

	def save(self):
		ext = settings.GENSETTINGS.get('Extentions', 'chant')[0]
		self.chemin = os.path.join(fonc.get_path(self.chemin), fonc.get_file_name(self.chemin)) + ext
		try:
			tree = ET.parse(self.chemin)
			chant_xml = tree.getroot()
		except (OSError, IOError) as error:
			if error.errno == os.errno.ENOENT:
				chant_xml = ET.Element(self.etype)
			else:
				raise exception.DataReadError(self.chemin)
		self.safeUpdateXML(chant_xml, 'lyrics', self._text.replace('\n', '\r\n'))
		self.safeUpdateXML(chant_xml, 'title', self._title)
		self.safeUpdateXML(chant_xml, 'transpose', self._transpose)
		self.safeUpdateXML(chant_xml, 'capo', self._capo)
		self.safeUpdateXML(chant_xml, 'key', self._key)
		self.safeUpdateXML(chant_xml, 'turf_number', self._turfNumber)
		self.safeUpdateXML(chant_xml, 'hymn_number', self._hymnNumber)
		self.safeUpdateXML(chant_xml, 'author', self._author)
		self.safeUpdateXML(chant_xml, 'copyright', self._copyright)
		self.safeUpdateXML(chant_xml, 'ccli', self._ccli)
		fonc.indent(chant_xml)

		tree = ET.ElementTree(chant_xml)
		tree.write(self.chemin, encoding="UTF-8")
		del self._diapos[:]

	def _replaceInText(self, toReplace, replaceBy):
		self.text = self.text.replace(toReplace, replaceBy)
		self.save()

	@property
	def nums(self):
		return {'custom':self.customNumber, \
				'turf':self.turfNumber, \
				'hymn':self.hymnNumber, \
				}

	@property
	def turfNumber(self):
		return self._turfNumber

	@property
	def hymnNumber(self):
		return self._hymnNumber

	@property
	def customNumber(self):
		return self._customNumber

	@property
	def transpose(self):
		if self._text == '':
			self.text
		return self._transpose

	@property
	def capo(self):
		if self._text == '':
			self.text
		return self._capo

	@property
	def key(self):
		if self._text == '':
			self.text
		return self._key

	@property
	def author(self):
		return self._author

	@property
	def copyright(self):
		return self._copyright

	@property
	def ccli(self):
		return self._ccli

	@property
	def text(self):
		if not self._text:
			if fonc.get_ext(self.chemin) in settings.GENSETTINGS.get('Extentions', 'chordpro'):
				self._getChordPro()
			elif fonc.get_ext(self.chemin) in settings.GENSETTINGS.get('Extentions', 'chant'):
				self._getXML()
			else:
				warnings.warn('Unknown file format for "%s".'%self.chemin)
		return self._text

	def _getXML(self):
		try:
			tree = ET.parse(self.chemin)
		except (OSError, IOError):
			warnings.warn('Not able to read "%s"'%self.chemin)
			self.title = self.nom
			return ''
		except ET.ParseError:
			print('Error on %s:\n%s'%(self.chemin, traceback.format_exc()))
			tkMessageBox.showerror(u'Erreur', 'Le fichier "%s" est illisible.'%self.chemin)
			return ''
		chant_xml = tree.getroot()
		try:
			tmp = chant_xml.find('lyrics').text
			title = chant_xml.find('title').text
		except (AttributeError, KeyError):
			tmp = ''
			title = ''
		if tmp is None:
			tmp = ''
		try:
			self._transpose = int( chant_xml.find('transpose').text )
		except (AttributeError, KeyError, ValueError, TypeError):
			self._transpose = None
		try:
			self._capo = int( chant_xml.find('capo').text )
		except (AttributeError, KeyError, ValueError, TypeError):
			self._capo = None
		try:
			self._hymnNumber = int( chant_xml.find('hymn_number').text )
		except (AttributeError, KeyError, ValueError, TypeError):
			self._hymnNumber = None
		try:
			self._turfNumber = int( chant_xml.find('turf_number').text )
		except (AttributeError, KeyError, ValueError, TypeError):
			self._turfNumber = None
		try:
			self._key = chant_xml.find('key').text
		except (AttributeError, KeyError):
			self._key = ''
		if not isinstance(self._key, basestring):
			self._key = ''
		self._key = self._key.replace('\n', '')
		if self._key != '':
			self._key = self._key
		try:
			self._author = chant_xml.find('author').text
		except (AttributeError, KeyError):
			self._author = None
		try:
			self._copyright = chant_xml.find('copyright').text
		except (AttributeError, KeyError):
			self._copyright = None
		try:
			self._ccli = chant_xml.find('ccli').text
		except (AttributeError, KeyError):
			self._ccli = None
		self.title = title
		tmp = gestchant.nettoyage(fonc.safeUnicode(tmp))
		self._text = tmp

	@transpose.setter
	def transpose(self, value):
		value = value.strip('\n')
		try:
			self._transpose = int(value)
		except (ValueError, TypeError):
			if not value:
				self._transpose = 0
			else:
				self._transpose = None

	@capo.setter
	def capo(self, value):
		value = value.strip('\n')
		try:
			self._capo = int(value)
		except (ValueError, TypeError):
			if not value:
				self._capo = 0
			else:
				self._capo = None

	@turfNumber.setter
	def turfNumber(self, value):
		value = value.strip('\n')
		try:
			self._turfNumber = int(value)
		except (ValueError, TypeError):
			if not value:
				self._turfNumber = 0
			else:
				self._turfNumber = None

	@hymnNumber.setter
	def hymnNumber(self, value):
		value = value.strip('\n')
		try:
			self._hymnNumber = int(value)
		except (ValueError, TypeError):
			if not value:
				self._hymnNumber = 0
			else:
				self._hymnNumber = None

	@key.setter
	def key(self, value):
		self._key = value.replace('\n', '')

	@text.setter
	def text(self, value):
		value = fonc.supressB(value, '[', ']') ######
		value = gestchant.nettoyage(value)
		value = '%s\n'%value
		self._text = value

	@author.setter
	def author(self, value):
		self._author = value

	@copyright.setter
	def copyright(self, value):
		self._copyright = value

	@ccli.setter
	def ccli(self, value):
		self._ccli = value


	def _getChordPro(self):
		try:
			with open(self.chemin) as f:
				brut = f.read().decode('utf-8')
		except (OSError, IOError):
			warnings.warn('Not able to read "%s"'%self.chemin)
			return ''

		self.title = fonc.getB(brut, '{t:', '}')[0]
		self._author = fonc.getB(brut, '{st:', '}')[0]
		self._copyright = fonc.getB(brut, '{c:', '}')[0]
		self._key = fonc.getB(brut, '{key:', '}')[0]
		ccliBrut = fonc.getB(brut, '{c:shir.fr', '}')[0]
		self._getSongBook(ccliBrut)

		brut = creplace.cleanupChar(brut.encode('utf-8')).decode('utf-8')

		# Interprete chorpro syntax
		brut = ' \\ss\n' + brut
		brut = brut.replace('\n\n', '\n\n\\ss\n')
		brut = brut.replace('{soc}', '\n\n\\sc\n')
		brut = brut.replace('{eoc}', '\n\n\\ss\n')
		brut = brut.replace('{c:Pont}', '\n\n\\sb\n')
		brut = fonc.supressB(brut, '{', '}')

		brut = brut.replace('\\ss\n\n\\sc', '\\sc')
		brut = brut.replace('\\ss\n\n\\sb', '\\sb')
		brut = gestchant.nettoyage(brut)
		brut = gestchant.nettoyage(brut)

		# Put double back slash at the last chord of each line
		brut = brut + '\n'
		fin = len(brut)
		while fin != -1:
			line = brut.rfind('\n', 0, fin)
			fin = brut.rfind(']', 0, line)
			if line == fin+1:
				precedant = fin
				while brut[precedant] == ']':
					precedant = brut.rfind('[', 0, precedant)-1
				brut = brut[:precedant+2] + '(' + brut[precedant+2:fin] + ')\\' + brut[fin:]
			else:
				brut = brut[:fin] + '\\' + brut[fin:]
		brut = fonc.strip_perso(brut, '\\\n')

		# Remove space after chord
		for letter in string.uppercase[:7]:
			brut = brut.replace('\n[%s] '%letter, '\n[%s]'%letter)
		brut = self._convertChordsFormat(brut)
		self._text = brut

	def _getSongBook(self, ccliBrut):
		for receuil in RECEUILS:
			deb = ccliBrut.find(receuil)
			fin = deb + len(receuil)
			for i in range(10):
				if len(ccliBrut)> fin and not ccliBrut[fin].isdigit():
					break
				fin += 1
			if deb != -1 and fin != -1:
				self._ccli = ccliBrut[deb:fin]
				num = ccliBrut[deb + len(receuil):fin]
				try:
					self._hymnNumber = int(num)
					self._ref = receuil
				except ValueError:
					print num
			if self._hymnNumber:
				break

	def _convertChordsFormat(self, text):
		if text != '':
			text = text + '\n'
			listChords = fonc.getB(text, '[', ']')
			previous = 0
			where = 0
			last = 0
			for i,chord in enumerate(listChords):
				# Add parenthesis for chord at end of lines
				if chord.find('\\') != -1:
					toAdd = '\\ac ' + ' '.join( listChords[last:i+1] ).replace('\\', '') + '\n'
					where = text.find(chord, where)
					where = text.find('\n', where) + 1
					text = text[:where] + toAdd + text[where:]
					last = i+1
			text = fonc.strip_perso(text, '\n')

			text = fonc.supressB(text, '[', ']')

			for newslide in settings.GENSETTINGS.get('Syntax', 'newslide')[0]:
				text = text.replace('%s\n\n\\ac'%newslide, '%s\n\\ac'%newslide)
			return text
