# -*- coding: utf-8 -*-

import os
import sys
import time
import markdown

from songfinder.elements import elements
from songfinder.elements import exports
from songfinder import classSet
from songfinder import globalvar
from songfinder import fonctions as fonc
from songfinder import classSettings as settings
from songfinder import exception

class Converter(object):
	def __init__(self, htmlStylePath=None):
		self._markdowner = markdown.Markdown()
		self._songExtentions = settings.GENSETTINGS.get('Extentions', 'chordpro') \
						+ settings.GENSETTINGS.get('Extentions', 'chant')
		self._listeExtentions = settings.GENSETTINGS.get('Extentions', 'liste')
		self._set = classSet.Set()

		self._dateList = dict()
		self._toDecline = set()
		self._decliningPass = False
		self._counter = 0
		self._makeSubDir = False

		self._declineFunctionsSetter = (self._setListOptions, self._setBassOptions, self._setGuitareOptions, )

		if not htmlStylePath:
			htmlStylePath = os.path.join(globalvar.dataPath, 'htmlTemplates', 'defaultStyle.html')
		if os.path.isfile(htmlStylePath):
			with open(htmlStylePath, 'r') as styleFile:
				self._htmlStyle = styleFile.read()
		else:
			self._htmlStyle = ''

	def _setDefaultOptions(self):
		settings.LATEXSETTINGS.create()
		self._suffix = ''

	def _setListOptions(self):
		self._setDefaultOptions()
		settings.LATEXSETTINGS.set('Latex_Parameters', 'list', 'oui')
		self._suffix = '_list'

	def _setBassOptions(self):
		self._setDefaultOptions()
		settings.LATEXSETTINGS.set('Latex_Parameters', 'keep_last', 'oui')
		settings.LATEXSETTINGS.set('Latex_Parameters', 'simple_chords', 'oui')
		self._suffix = '_bass'

	def _setGuitareOptions(self):
		self._setDefaultOptions()
		settings.LATEXSETTINGS.set('Latex_Parameters', 'keep_first', 'oui')
		settings.LATEXSETTINGS.set('Latex_Parameters', 'capo', 'oui')
		settings.LATEXSETTINGS.set('Latex_Parameters', 'simple_chords', 'oui')
		self._suffix = '_guitar'

	def markdown(self, inputFiles, outputFiles):
		self._exportClass = exports.ExportMarkdown
		self._optionSongs = dict()
		self._optionSets = {'titleLevel':2}
		self._ext = '.md'
		self._titleMark = '# @@title@@\n'
		self._bodyMark = ''
		print('Converting files in "%s" to markdown.'%inputFiles)
		self._convert(inputFiles, outputFiles)

	def html(self, inputFiles, outputFiles):
		self._exportClass = exports.ExportHtml
		self._optionSongs = {'markdowner':self._markdowner}
		self._optionSets = {'markdowner':self._markdowner, 'htmlStyle':'@@body@@', 'titleLevel':2}
		self._ext = '.html'
		self._titleMark = '<title>@@title@@</title>\n<h1>@@title@@</h1>\n'
		self._bodyMark = self._htmlStyle
		print('Converting files in "%s" to html.'%inputFiles)
		self._convert(inputFiles, outputFiles)

	def _convert(self, inputFiles, outputFiles):
		refTime = time.time()
		self._setDefaultOptions()
		if os.path.isfile(inputFiles):
			inputFile = inputFiles
			if outputFiles[-1] == os.sep:
				outputFile = os.path.join(outputFiles, fonc.get_file_name(inputFiles) + self._ext)
			else :
				outputFile = outputFiles
			self._convertOneFile(inputFile, outputFile)
		elif os.path.isdir(inputFiles):
			if outputFiles[-1] != os.sep:
				outputFiles = outputFiles + os.sep
			for root, dirs, files in os.walk(inputFiles):
				for fileName in files:
					inputFile = os.path.join(root, fileName)
					outputFile = inputFile.replace(inputFiles, outputFiles)
					outputFile = fonc.get_file_path(outputFile) + self._ext
					if self._makeSubDir:
						outputFile = self._makeSubDirectory(outputFile)
					self._convertOneFile(inputFile, outputFile)

		# Declining file to guitar/bass/list version
		self._decliningPass = True
		if self._dateList:
			lastKey = sorted(self._dateList.keys())[-1]
			toAdd = (lastKey, self._dateList[lastKey])
			self._toDecline.add(toAdd)
		if self._toDecline:
			for declineParameterSet in self._declineFunctionsSetter:
				declineParameterSet()
				for (inputFile, outputFile) in self._toDecline:
					outputFile = fonc.get_file_path(outputFile) + self._suffix + fonc.get_ext(outputFile)
					self._convertOneFile(inputFile, outputFile)
		self._setDefaultOptions()
		self._dateList = dict()
		self._toDecline = set()
		self._decliningPass = False

		print('Converted %d files. Convertion took %ss.'%(self._counter, time.time()-refTime))
		self._counter =0

	def _convertOneFile(self, inputFile, outputFile):
		if fonc.get_ext(inputFile) in self._songExtentions:
			try:
				os.makedirs(fonc.get_path(outputFile))
			except (OSError, IOError) as error:
				if error.errno == os.errno.EEXIST:
					pass
				else:
					raise
			myElem = elements.Chant(inputFile)
			myExport = self._exportClass(myElem, **self._optionSongs)
			with open(outputFile, 'w') as out:
				out.write( myExport.exportText.encode('utf-8') )
			self._counter += 1

		elif fonc.get_ext(inputFile) in self._listeExtentions:
			self._set.load(inputFile)
			text = ''
			for myElem in self._set:
				myExport = self._exportClass(myElem, **self._optionSets)
				text += '%s\n'%myExport.exportText
			title = self._fillMark('title', self._titleMark, str(self._set))
			text = '%s%s'%(title, text)
			text = self._fillMark('body', self._bodyMark, text)
			with open(outputFile, 'w') as out:
				out.write( text.encode('utf-8') )

			# Filling set to decline in guitar/bass/list versions
			if not self._decliningPass:
				if self._isDate(inputFile):
					self._dateList[inputFile] = outputFile
				else:
					self._toDecline.add((inputFile, outputFile))
			self._counter += 1

	def _fillMark(self, mark, styledText, content):
		if styledText:
			output = styledText.replace('@@%s@@'%mark, content)
		else:
			output = content
		return output

	def _makeSubDirectory(self, filaPath):
		filePath = fonc.get_path(filaPath)
		fileName = fonc.get_file_name_ext(filaPath)
		subDirectory = ''
		jem = fileName.find('JEM')
		if jem != -1:
			num = int(fileName[jem+3:jem+6])
			if num < 373:
				subDirectory = 'JEM1'
			elif num < 722:
				subDirectory = 'JEM2'
			else:
				subDirectory = 'JEM3'
		elif fileName.find('SUP') != -1:
			subDirectory = 'Others'

		filePath = os.path.join(filePath, subDirectory)
		try:
			os.makedirs(filePath)
		except (OSError, IOError) as error:
			if error.errno == os.errno.EEXIST:
				pass
			else:
				raise
		return os.path.join(filePath, fileName)

	def _isDate(self, path):
		fileName = fonc.get_file_name(path)
		listElem = [subsubsubElem for elem in fileName.split('-') \
					for subElem in elem.split('_') \
					for subsubElem in subElem.split('.') \
					for subsubsubElem in subsubElem.split(' ') \
					]
		if all( [elem.isdigit() for elem in listElem] ):
			return True

	def makeSubDirOn(self):
		self._makeSubDir = True

	def makeSubDirOff(self):
		self._makeSubDir = False
