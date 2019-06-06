# -*- coding: utf-8 -*-
from __future__ import division

from PIL import Image, ImageTk
import os
import shutil
import warnings
import time
import Tkinter as TK
import ttk
import psutil
import math

from songfinder import globalvar
from songfinder import cache
from songfinder import classSettings as settings

class Background(object):
	def __init__(self, path, width, height, keepRatio):
		self.w = int(width)
		self.h = int(height)
		self.path = path
		tmp = os.path.splitext( os.path.split(self.path)[1] )[0]
		self.name = '%s_%s_%s'%(tmp, str(self.w), str(self.h))
		self.keepRatio = keepRatio

	def __str__(self):
		return self.name

	def __repr__(self):
		return repr(self.name)

class Backgrounds(object):
	def __init__(self):
		self._imageFile = None
		self._cachePath = os.path.join(globalvar.settingsPath, 'cache')
		try:
			os.makedirs( self._cachePath )
		except OSError as os.errno.EEXIST:
			pass
		cacheSlots = 10 + int(psutil.virtual_memory()[1]*2e-8)
		print 'Using %s cache slots for backgrounds'%cacheSlots
		self._cache = cache.Cache(cacheSlots, self._getImageFile)

	def get(self, back):
		return self._cache.get(back.name, [back])

	def _getImageFile(self, back):
		try:
			path = os.path.join(self._cachePath, back.name + '.png')
			self._imageFile = Image.open(path)
		except IOError:
			try:
				self._imageFile = Image.open(back.path)
			except IOError:
				return None
			self._resize(back)
			self._imageFile.save(path)
		return ImageTk.PhotoImage(self._imageFile)

	def _resize(self, back):
		if back.keepRatio == 'keep':
			im_w, im_h = self._imageFile.size
			aspect_ratio = im_w/im_h
			back.w = min(back.w, int(back.h*aspect_ratio))
			back.h = int(back.w/aspect_ratio)
		self._imageFile = self._imageFile.resize((back.w, back.h), Image.ANTIALIAS)

def cleanDiskCacheImage():
	path = os.path.join(globalvar.settingsPath, 'cache')
	if os.path.isdir(path):
		size = directorySize(path)
		if size > 10**8:
			print('Cleaning image cache: %s'%prettySize(size))
			shutil.rmtree(path, ignore_errors=True, onerror=None)

def directorySize(folder):
	total_size = os.path.getsize(folder)
	for item in os.listdir(folder):
		itempath = os.path.join(folder, item)
		if os.path.isfile(itempath):
			total_size += os.path.getsize(itempath)
		elif os.path.isdir(itempath):
			total_size += directorySize(itempath)
	return total_size

def prettySize(size):
	base = 1024
	echelles = [' o', ' Ko', ' Mo', ' Go', ' To', 'Po']
	str_size = str(0)
	for i, echelle in enumerate(echelles):
		if size >= base**(i):
			str_size = str(round(size/base**(i),2)) + echelle
	return str_size

def checkBackgrounds():
	etypes = settings.GENSETTINGS.get('Syntax', 'element_type')
	notOk = []
	for etype in etypes:
		fileToCheck = settings.PRESSETTINGS.get(etype, 'Background')
		if not os.path.isfile(fileToCheck):
			notOk.append(etype)
	return notOk


BACKGROUNDS = Backgrounds()
