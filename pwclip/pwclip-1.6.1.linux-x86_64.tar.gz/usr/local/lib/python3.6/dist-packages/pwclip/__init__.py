#/usr/bin/env python3
"""pwclip init module"""
import sys
from os import path, devnull, environ, getenv, remove, name as osname
from subprocess import call

# this only makes sence while i need the lib folder in the PYTHONPATH
# otherwise i need to rewrite lots of code cause i have thus libs in the
# python environment path at my workstation and do not change that =)
__lib = path.join(path.dirname(__file__), 'lib')
if path.exists(__lib) and __lib not in sys.path:
	sys.path = [__lib] + sys.path
if sys.platform == 'win32' and sys.executable.split('\\')[-1] == 'pythonw.exe':
	sys.stdout = open(devnull, 'w')
	sys.stderr = open(devnull, 'w')
from system import xnotify
from colortext import abort
from pwclip.cmdline import cli, gui
try:
	def pwclip():
		"""pwclip passcrypt gui mode"""
		gui()
	def ykclip():
		"""pwclip yubico gui mode"""
		gui('yk')
except KeyboardInterrupt:
	xnotify('aborted by keystroke')

def pwcli():
	"""pwclip cli mode"""
	cli()
