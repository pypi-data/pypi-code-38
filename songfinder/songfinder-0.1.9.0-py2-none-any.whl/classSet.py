# -*- coding: utf-8 -*-
#cython: language_level=2

import xml.etree.cElementTree as ET
import datetime
import os
import warnings

from songfinder.elements import elements
from songfinder import fonctions as fonc
from songfinder import classPaths
from songfinder import globalvar
from songfinder import classSettings as settings

class Set(object):
	def __init__(self, **kwargs):
		self._paths = classPaths.Paths()
		self._listElem = []
		self._generateName()
		self._changed = False

	def __eq__(self, other):
		return self._listElem == other._listElem

	def __len__(self):
		return len(self._listElem)

	def __setitem__(self, key, value):
		self._listElem[key] = value
		self._changed = True

	def __getitem__(self, index):
		return self._listElem[index]

	def __delitem__(self, index):
		del self._listElem[index]
		self._changed = True

	def __contains__(self, element):
		return element in self._listElem

	def __str__(self):
		return self._name

	def _generateName(self):
		nextSunday = datetime.timedelta(days = 6-datetime.datetime.today().weekday())
		self._name = str(datetime.date.today()+ nextSunday)
		while os.path.isfile(self._paths.sets + self._name):
			if len(self._name) == 10:
				self._name = self._name + '_1'
			else:
				self._name = self._name[:11] + str(int(self._name[11:])+1)
		self._fileName = os.path.join(self._paths.sets, self._name) \
						+ settings.GENSETTINGS.get('Extentions', 'liste')[0]

	def _read(self):
		tmp = None
		self._listElem = []
		try:
			tree = ET.parse(self._fileName)
			tree.getroot().find('slide_groups')[:]
		except (IOError, AttributeError):
			warnings.warn('Not able to read %s'%self._fileName)
			return 1
		xmlList = tree.getroot()

		for title in xmlList.find('slide_groups')[:]:
			if title.attrib['type'] == 'song':
				# Different ways of writting the path, test all
				tmp = elements.Chant( os.path.join(self._paths.songs, title.attrib['path'], title.attrib['name']) )
				if not tmp.exist():
					tmp = elements.Chant( os.path.join(self._paths.songs, title.attrib['name']) )
					# ~ if not tmp.exist():
						# ~ warnings.warn('"%s" not found while reading "%s".'%(title.attrib['name'], self._fileName))

			elif title.attrib['type'] == 'media':
				tmp = elements.Element(title.attrib['name'], title.attrib['type'], title.attrib['path'])
			elif title.attrib['type'] == 'image':
				tmp = elements.Element(title.attrib['name'], title.attrib['type'], title.attrib['path'])
			elif title.attrib['type'] == 'verse':
				tmp = elements.Passage( title.attrib['version'], int(title.attrib['livre']), \
												int(title.attrib['chap1']), int(title.attrib['chap2']), \
												int(title.attrib['vers1']), int(title.attrib['vers2']) )
			self._listElem.append(tmp)
		self._changed = False

	def append(self, element):
		self._listElem.append(element)
		self._changed = True

	def insert(self, index, element):
		self._listElem.insert(index, element)
		self._changed = True

	def clear(self):
		del self._listElem[:]
		self._changed = True

	def setName(self, inputPath):
		self._fileName = inputPath
		self._name = fonc.get_file_name(inputPath)

	def save(self):
		new_set = ET.Element("set")
		new_set.set("name", self._name)
		slide_groups = ET.SubElement(new_set, "slide_groups")
		slide_group = []
		for i, element in enumerate(self._listElem):
			chemin = fonc.get_path(element.chemin)
			# For compatibility between linux an windows, all path are writtent with slash
			chemin = chemin.replace(os.sep, '/')
			# Write path relative to songs directory
			chemin = chemin.replace('%s'%self._paths.songs.replace(os.sep, '/'), '')

			slide_group.append(ET.SubElement(slide_groups, "slide_group"))
			slide_group[i].set("type", element.etype)
			if element.etype == 'song':
				slide_group[i].set("path", chemin)
				slide_group[i].set("name", element.nom)
			elif element.etype == 'verse':
				slide_group[i].set("name", element.nom)
				slide_group[i].set("path", chemin)
				slide_group[i].set("version", element.version)
				slide_group[i].set("livre", str(element.livre))
				slide_group[i].set("chap1", str(element.chap1))
				slide_group[i].set("chap2", str(element.chap2))
				slide_group[i].set("vers1", str(element.vers1))
				slide_group[i].set("vers2", str(element.vers2))
			elif element.etype == 'image':
				slide_group[i].set("name", element.nom)
				slide_group[i].set("path", chemin)

		tree = ET.ElementTree(new_set)
		fonc.indent(new_set)
		tree.write(self._fileName, encoding="UTF-8")
		self._changed = False

	def delete(self):
		try:
			os.remove(self._fileName)
		except OSError as os.errno.EEXIST:
			warnings.warn('File "%s" does not exist.'%self._fileName)
		except IOError as os.errno.EACCES:
			warnings.warn('Acces to "%s" is not permited.'%self._fileName)
		self._changed = True

	def load(self, fileName):
		if os.path.isfile(fileName):
			self._fileName = fileName
		else:
			self._fileName = os.path.join(self._paths.sets, fileName)
		if fonc.get_ext(self._fileName) == '':
			self._fileName = self._fileName + settings.GENSETTINGS.get('Extentions', 'liste')[0]
		self._name = fonc.get_file_name(self._fileName)
		self._read()

	@property
	def path(self):
		return self._fileName

	@property
	def changed(self):
		return self._changed
