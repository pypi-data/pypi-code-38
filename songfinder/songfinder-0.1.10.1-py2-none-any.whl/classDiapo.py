# -*- coding: utf-8 -*-
from __future__ import division

import tkFont
import math
import Tkinter as tk

from songfinder import gestchant
from songfinder import globalvar
from songfinder import guiHelper
from songfinder import fonctions as fonc
from songfinder import classSettings as settings

class Diapo(object):
	def __init__(self, element, numero, stype, max_car, nombre=0, text='', **kwargs):
		self.element = element
		self.numero = numero
		self.nombre = nombre
		self.etype = element.etype
		self.stype = stype
		self.max_car = max_car
		self._title = None

		self._text = text
		self.nbLignes = None

		self.police = None
		self._themeName = 'theone'
		self._aspectRatio = None

	@property
	def text(self):
		if not self.nbLignes:
			newline = settings.GENSETTINGS.get('Syntax', 'newline')
			text = self._text
			text = '\n' + newline + '\n' + text
			text = text.replace('\n ', '\n')
			text = gestchant.numerote(text, self.numero, self.nombre, self.etype)
			text = gestchant.print_title(text, self.element.title, self.numero, self.etype)
			text = gestchant.check_bis(text, self.etype)
			text = gestchant.saut_ligne(text, self.max_car, self.etype)
			text = text.replace('\\newline', '')
			text = gestchant.verifie_ponctuation(text, self.etype)
			text = gestchant.nettoyage(text)
			text = gestchant.clean_maj(text, self.etype)
			text = gestchant.verifie_ponctuation_maj(text, self.etype)
			text = gestchant.majuscule(text, self.etype)
			text = gestchant.nettoyage(text)
			text = gestchant.clean_line(text)

			self.nbLignes = len( [ligne for ligne in text.splitlines() if ligne !=''] )
			self._text = text
		return self._text

	@property
	def title(self):
		if not self._title:
			if self.element.title:
				self._title = self.etype + ' -- ' + self.element.title
				if self.nombre > 1:
					self._title =  '%s -- %s/%s'%(self._title, str(self.numero), str(self.nombre))
			else:
				self._title = self.etype
		return self._title

	@property
	def beamer(self):
		text = self.text
		if settings.PRESSETTINGS.get(self.etype, 'Numerote_diapo') == 'oui':
			num = '(%s/%s)'%(str(self.numero), str(self.nombre))
			text = text.replace(num, '{\\footnotesize %s}\n\\vspace{1em}\n'%num)
		elif settings.PRESSETTINGS.get(self.etype, 'Print_title') == 'oui':
			text = text.replace('%s\n'%self.element.title.upper(), \
								'%s\n\\vspace{1em}\n'%self.element.title.upper())
		# Add background header
		return text

	@property
	def latex(self):
		# Remove title if is in text because it will be added latter
		text = self.text
		lenghTitle = len(self.element.title)
		if text[:lenghTitle] == self.element.title.upper():
			text = text[lenghTitle:]

		# Add subtitle: Refrain; Pont
		if self.stype == '\\sc':
			tab = '\\tab '
			title = 'Refrain'
		elif self.stype == '\\sb':
			tab = ''
			title = 'Pont'
		else:
			tab = ''
			title = ''
		add = '\n\\textbf{%s}\n%s'%(title, tab)

		if title != '' and text.find(add) == -1:
			out = add + text.replace('\n', '\n%s'%tab) + '\n\n'
		else:
			out = text
		return out

	@property
	def num(self):
		if self.numero:
			text = '(' + str(self.numero) + '/' + str(self.nombre) + ')'
		return text

	@property
	def themeName(self):
		return self._themeName

	@property
	def backgroundName(self):
		backName = settings.PRESSETTINGS.get(self.etype, 'Background')
		if self.etype == 'image':
			backName = self.element.chemin
			self._aspectRatio = 'keep'
		return backName

	@property
	def markdown(self):
		# Add subtitle: Refrain; Pont
		if self.stype == '\\sc':
			tab = '> '
			title = 'Refrain'
		elif self.stype == '\\sb':
			tab = ''
			title = 'Pont'
		else:
			tab = ''
			title = ''
		add = '\n**%s**\n%s'%(title, tab)

		if title != '' and self.text.find(add) == -1:
			out = add + self.text.replace('\n', '\n%s'%tab) + '\n\n'
		else:
			out = self.text
		return out

	def printDiapo(self, theme):
		theme.text = self.text
		theme.updateBack(self.backgroundName, self._aspectRatio)
		theme.resizeFont()
		theme.update()

	def prefetch(self, themes, text=False):
		for theme in reversed(themes):
			if text:
				theme.text = self.text
				theme.resizeFont()
			theme.prefetchBack(self.backgroundName, self._aspectRatio)
