#!/usr/bin/env python3

import os
import re
from distutils.core import setup
try:
	import py2exe
except ImportError as e:
	py2exe = None
try:
	if py2exe and "py2exe" in sys.argv:
		raise ImportError
	from cx_Freeze import setup, Executable
	cx_Freeze = True
except ImportError as e:
	cx_Freeze = False


isWindows = os.name.lower() in {"nt", "ce"}

extraKeywords = {}

# Workaround for mbcs codec bug in distutils
# http://bugs.python.org/issue10945
import codecs
try:
	codecs.lookup("mbcs")
except LookupError:
	codecs.register(lambda name: codecs.lookup("ascii") if name == "mbcs" else None)


# Create freeze executable list.
guiBase = None
if isWindows:
	guiBase = "Win32GUI"
freezeExecutables = [ ("piccol", None, guiBase), ]
if py2exe:
	extraKeywords["console"] = [ s for s, e, b in freezeExecutables ]
if cx_Freeze:
	executables = []
	for script, exe, base in freezeExecutables:
		if exe:
			if isWindows:
				exe += ".exe"
			executables.append(Executable(script = script,
						      targetName = exe,
						      base = base))
		else:
			executables.append(Executable(script = script,
						      base = base))
	extraKeywords["executables"] = executables
	extraKeywords["options"] = {
			"build_exe"     : {
				"packages"      : [ ],
			}
		}

version = "unknown_version"
m = re.match(r'.*^\s*PICCOL_VERSION\s*=\s*"([\w\d\.\-_]+)"\s*$.*',
	     open("piccol").read(),
	     re.DOTALL | re.MULTILINE)
if m:
	version = m.group(1)
print("piccol version %s" % version)

setup(	name		= "piccol",
	version		= version,
	description	= "Color picker and translator",
	license		= "GNU General Public License v2 or later",
	author		= "Michael Buesch",
	author_email	= "m@bues.ch",
	url		= "https://bues.ch/",
	scripts		= [ "piccol", ],
	keywords	= [ "color", "RGB", "HLS", "HSL", ],
	classifiers	= [
		"Development Status :: 5 - Production/Stable",
		"Environment :: Win32 (MS Windows)",
		"Environment :: X11 Applications",
		"Environment :: X11 Applications :: Qt",
		"Intended Audience :: End Users/Desktop",
		"Intended Audience :: Developers",
		"Intended Audience :: Education",
		"Intended Audience :: Information Technology",
		"Intended Audience :: System Administrators",
		"License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)",
		"Operating System :: Microsoft :: Windows",
		"Operating System :: POSIX",
		"Operating System :: POSIX :: Linux",
		"Programming Language :: Python",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: Implementation :: CPython",
		"Topic :: Desktop Environment",
		"Topic :: Education",
		"Topic :: Scientific/Engineering",
		"Topic :: Software Development",
	],
	long_description = open("README.md").read(),
	**extraKeywords
)
