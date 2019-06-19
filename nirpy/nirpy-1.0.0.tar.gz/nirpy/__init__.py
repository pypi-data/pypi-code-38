"""
#Module Created by LimerBoy with Love <3

* nircmdc: https://www.nirsoft.net/utils/nircmd.html
* nircmdc reference: https://nircmd.nirsoft.net

> Example usage:

import nirpy
nirpy.load()
nirpy.execute('monitor off')

Wait until all commands are executed and continue to execute your code.
nirpy.execute('infobox "Computer will restart" "INFO" && shutdown.exe -r -t 3600', wait=True)

Wait until command are executed with high process priority and continue to execute your code.
Process priority: [LOW | NORMAL | HIGH | REALTIME]
nirpy.execute('savescreenshotfull desktop.png', wait=True, priority='HIGH')

Download file from internet.
file = nirpy.wget(link)

Execute downloaded file.
nirpy.start(file)

after executing you can use: nirpy.unload() to remove nircmdc.exe from system.

"""


# Import modules
from zipfile import ZipFile
from os import system as os_system
from os import path as os_path
from os import remove as os_remove
from os import environ as os_environ
from os import startfile as os_startfile
from shutil import move as shutil_move
from wget import download as wget_download
from platform import system as platform_system

# Check system
if platform_system().lower() != 'windows':
	raise OSError('I\'m work only in Windows, system ' + platform_system() + ' not support')

# Load file from URL
def wget(link):
	return wget_download(link)

# Start file
def start(file):
	os_startfile(file)

# Extract file from archive
def unzip(archive, file):
	with ZipFile(archive, 'r') as zip:
		zip.extract(file)

# Add file to archive
def addzip(archive, file):
	with ZipFile(archive,'w') as zip: 
		zip.write(file)


# Load nircmdc.exe
def load(*argv):
	# Nircmdc file path
	global nircmdc_file
	nircmdc_file = os_environ['TEMP'] + '\\nircmdc.exe'

	if os_path.exists(nircmdc_file):
		return True
	else:
		if argv:
			try:
				wget_download(argv)
			except ValueError:
				raise ConnectionError('nirpy - This link does not exist: ' + argv)
		else:
			wget_download('https://raw.githubusercontent.com/LimerBoy/nirpy/master/nircmdc.exe')
		shutil_move('nircmdc.exe', nircmdc_file)
		return True

# Unload (delete) nircmdc.exe from system
def unload():
	# Nircmdc file path
	nircmdc_file = os_environ['TEMP'] + '\\nircmdc.exe'

	if os_path.exists(nircmdc_file):
		os_remove(nircmdc_file)
		return True
	else:
		raise FileNotFoundError('nirpy - Failed to delete file. It does not exist')
		
# Execute nircmdc command
def execute(command, wait=False, priority='NORMAL'):
	if wait == True:
		wait_string = '/wait '
	else:
		wait_string = ' '

	try:
		os_system('@start /MIN /B /' + priority + ' ' + wait_string +  nircmdc_file + ' ' + command)
	except NameError:
		raise FileNotFoundError('nirpy - You don\'t loaded nircmdc.exe please make nirpy.load() after importing this module.')

if __name__ == '__main__':
	print('[NIRPY] - I\'m need be imported!')