# -*- coding: utf-8 -*-

class CommandLineError(NotImplementedError):
	def __init__(self, command):
		self.command = command
		self.packetDict = {"sox":"sox libsox-fmt-mp3", "flac":"flac", \
						"opusenc":"opus-tools", "oggenc":"vorbis-tools", \
						"lame":"ubuntu-restricted-extras lame", "hg":"mercurial"}
	def __str__(self):
		aptCommand = self.packetDict.get(self.command, None)
		if aptCommand:
			ubuntuInfo = " On Ubuntu try 'sudo apt install %s'."%aptCommand
		else:
			ubuntuInfo = ''
		out = '%s is not a valid command. Please install it to use this feature.%s'%(self.command, ubuntuInfo)
		return repr(out)

class DataReadError(IOError):
	def __init__(self, theFile):
		self.theFile = theFile
	def __str__(self):
		out = 'Impossible de lire le fichier "%s"'%self.theFile
		return repr(out)

class DiapoError(Exception):
	def __init__(self, number):
		self.number = number
	def __str__(self):
		out = 'Le numero de diapo "%s" n\'est pas valide'%self.number
		return repr(out)
