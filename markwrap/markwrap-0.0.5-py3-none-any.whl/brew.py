'''
Python wrapper for the brew (Homebrew) command

Please manually test and verify before committing changes.
'''

import logging
import shutil
import subprocess

BREW="/usr/local/bin/brew"

def list():
	logging.info("Process started   :  %s %s %s", BREW, "list", "-1")
	result = subprocess.call([BREW,"list","-1"], subprocess.PIPE, stderr=subprocess.STDOUT)
	if (result != 0):
		logging.error("Error running process:  %s %s %s", BREW, "list", "-1")
		raise RuntimeError()
	logging.info("Process terminated:  %s %s %s", BREW, "list", "-1")

def update():
	logging.info("Process started   :  %s %s", BREW, "update")
	result = subprocess.call([BREW,"update"], subprocess.PIPE, stderr=subprocess.STDOUT)
	if (result != 0):
		logging.error("Error running process:  %s %s", BREW, "update")
		raise RuntimeError()
	logging.info("Process terminated:  %s %s", BREW, "update")

def upgrade():
	logging.info("Process started   :  %s %s", BREW, "upgrade")
	result = subprocess.call([BREW,"upgrade"], subprocess.PIPE, stderr=subprocess.STDOUT)
	if (result != 0):
		logging.error("Error running process:  %s %s", BREW, "upgrade")
		raise RuntimeError()
	logging.info("Process terminated:  %s %s", BREW, "upgrade")

def validateInstall():
	logging.info("Validating Homebrew install at %s", BREW)
	result = shutil.which(BREW)
	if (result is None):
		logging.error("Homebrew not found with shutil at %s", BREW)
		raise RuntimeError()
	logging.info("Homebrew found at %s", BREW)
	result = subprocess.call([BREW,"--version"], subprocess.PIPE, stderr=subprocess.STDOUT)
	if (result != 0):
		logging.error("Error running process (exit code %d):  %s %s", result, BREW, "--version")
		raise RuntimeError()
	logging.info("Validated Homebrew install at %s", BREW)
