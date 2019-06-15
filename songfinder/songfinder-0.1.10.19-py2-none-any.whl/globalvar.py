# -*- coding: utf-8 -*-

import os
import sys
import platform
import re
import warnings

appName = "songfinder"

try: # Windows only imports
	from win32com.client import Dispatch
except ImportError:
	pass

def getOs():
	if platform.system() == "Linux":
		if platform.dist()[0] == "Ubuntu":
			myOs = "ubuntu"
		else:
			myOs = "linux"
	elif platform.system() == "Windows":
		myOs = "windows"
	else:
		myOs = "notSupported"
		warnings.warn(
			"Your `%s` isn't a supported operatin system`." % platform.system())
	return myOs

myOs = getOs()

# Define root diretcory
chemin_root = os.getcwd()

# Define data directory
dataPath = os.path.join(os.path.split(__file__)[0], 'data')

# Define settings directory
if os.path.isfile( os.path.join(chemin_root, 'PORTABLE') ):
	portable = True
else:
	portable = False

# Set if installation is portable
try:
	f = open( os.path.join(chemin_root, 'test.test') ,"w")
	f.close()
	os.remove( os.path.join(chemin_root, 'test.test') )
except IOError as os.errno.EACCES:
	portable = False

# Define Settings directory
if portable == False:
	print 'Installed version'
	settingsPath = os.path.join(os.path.expanduser("~"), '.' + appName, '')
else:
	print 'Portable version'
	settingsPath = os.path.join(chemin_root, '.' + appName, '')

if sys.maxsize == 9223372036854775807:
	arch = 'x64'
else:
	arch = 'x86'
dependances = 'deps-%s'%arch
unittest = False
