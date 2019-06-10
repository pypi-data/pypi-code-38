# -*- coding: utf-8 -*-

import os
import sys
import platform
import distutils.spawn
import threading
import subprocess

from songfinder import globalvar
from songfinder import exception

class MyCommand(object):
	def __init__(self, command, *args, **kwargs):
		self._command = command
		self._locaPaths = os.path.join(globalvar.chemin_root, globalvar.dependances, "")
		self._myOs = globalvar.myOs

	def checkCommand(self):
		if self._command != '' and self._checkInPath() and self._checkAuto() and self._checkLocal():
			raise exception.CommandLineError(self._command)
		else:
			return 0

	def _checkInPath(self):
		# try to find command in path
		if self._myOs in ['ubuntu', 'linux']:
			code, out, err = self.run(before=['type -a'])
		elif self._myOs == 'windows':
			code, out, err = self.run(before=['where'])
		else:
			code = 1
		return code

	def _checkAuto(self):
		try:
			command = distutils.spawn.find_executable(self._command)
		except AttributeError: # distutils.spawn throws attribute error on windows freezed
			pass
		if not command:
			return 1
		else:
			self._command = command
			return 0

	def _checkLocal(self):
		# Look for portable instalaltion packaged with the software
		for root, dirs, files in os.walk(self._locaPaths):
			for fichier in files:
				if fichier in [self._command, '.'.join([self._command, "exe"])]:
					self._command = os.path.join(root, fichier)
					return 0
		return 1

	def run(self, options=[], timeOut=float('inf'), **kwargs):
		before = kwargs.get('before', None)
		winOptions = kwargs.get('winOptions', None)
		linuxOptions = kwargs.get('linuxOptions', None)

		commandList = []
		if before:
			commandList = (before)
		commandList.append('"' + self._command + '"')

		if self._myOs == "ubuntu" and linuxOptions:
			commandList += linuxOptions
		elif self._myOs == "windows" and winOptions:
			commandList += winOptions

		commandList += options
		for symbol in ['&&', '&', ';']:
			index = -2
			try:
				while True:
					index = commandList.index(symbol, index+2)
					commandList.insert(index+1, '"' + self._command + '"')
			except ValueError:
				pass
		fullCommand = ' '.join(commandList)
		proc = subprocess.Popen(fullCommand,  shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		timer = threading.Timer(timeOut, proc.kill)
		try:
			timer.start()
			stdout, stderr = proc.communicate()
		finally:
			timer.cancel()
			returncode = proc.returncode
		if not stdout:
			stdout = ''
		if not stderr:
			stderr = ''
		stderr = '\n'.join([fullCommand, stderr])
		return returncode, stdout, stderr

def ping(host):
	ping = MyCommand('ping')
	code, out, err = ping.run(linuxOptions=['-c 2', '-w 3'], winOptions=['-n 2', '-w 3000'], options=['google.fr'], timeOut=5)
	return code

def run_file(path):

	# Pas de EAFP cette fois puisqu'on est dans un process externe,
	# on ne peut pas gérer l'exception aussi facilement, donc on fait
	# des checks essentiels avant.

	# Vérifier que le fichier existe
	if not os.path.exists(path):
		raise IOError('No such file: %s' % path)

	# On a accès en lecture ?
	if hasattr(os, 'access') and not os.access(path, os.R_OK):
		raise IOError('Cannot access file: %s' % path)

	# Lancer le bon programme pour le bon OS:

	if hasattr(os, 'startfile'): # Windows
		# Startfile est très limité sous Windows, on ne pourra pas savoir
		# si il y a eu une erreu
		proc = os.startfile(path)

	elif sys.platform.startswith('linux'): # Linux:
		proc = subprocess.Popen(['xdg-open', path],
								 # on capture stdin et out pour rendre le
								 # tout non bloquant
								 stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	elif sys.platform == 'darwin': # Mac:
		proc = subprocess.Popen(['open', '--', path],
								stdout=subprocess.PIPE, stderr=subprocess.PIPE)

	else:
		raise NotImplementedError(
			"Your `%s` isn't a supported operatin system`." % sys.platform)

	# Proc sera toujours None sous Windows. Sous les autres OS, il permet de
	# récupérer le status code du programme, and lire / ecrire sur stdin et out
	return proc
