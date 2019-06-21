"""
#Module Created by LimerBoy with Love <3

* nircmdc: https://www.nirsoft.net/utils/nircmd.html
* nircmdc reference: https://nircmd.nirsoft.net

> Example usage:

import nirpy
nirpy.load() # if you pc is 32bit: nirpy.load(link='LINK.TO.YOU.NIRCMDC.FILE')

# NIRCMDC.exe
nirpy.execute('monitor off')

# CMD.exe
nirpy.system('echo this is a system command!')

Wait until all commands are executed and continue to execute your code.
nirpy.execute('infobox "Computer will restart" "INFO" && shutdown.exe -r -t 3600', wait=True)

Wait until command are executed with high process priority and continue to execute your code.
Process priority: [LOW | NORMAL | HIGH | REALTIME]
nirpy.execute('savescreenshotfull desktop.png', wait=True, priority='HIGH')

Download file from internet.
file = nirpy.wget(link)

Execute downloaded file.
nirpy.start(file)

Add/Remove autorun
nirpy.autorun('C:\\Windows', 'notepad.exe', 'test_name', state=True) # Add notepad to startup
nirpy.autorun('C:\\Windows', 'notepad.exe', 'test_name', state=False) # Remove notepad from startup

after executing you can use: nirpy.unload() to remove nircmdc.exe from system.

"""

# Check system
from platform import system as platform_system
if platform_system().lower() != 'windows':
	raise OSError('I\'m work only in Windows, system ' + platform_system() + ' not support')


# Import modules
from os import system as os_system
from os import path as os_path
from os import remove as os_remove
from os import environ as os_environ
from os import getenv as os_getenv
from os import startfile as os_startfile
from shutil import move as shutil_move
from wget import download as wget_download

# Get file path
nircmdc_file_path = os_environ['TEMP'] + '\\nirpy.exe'

# Load file from URL
def wget(link):
	return wget_download(link)

# Start file
def start(file):
	os_startfile(file)


# Add to startup.
def autorun(path, file, name, state=True):
	autorun_path = (os_getenv("SystemDrive") + '\\Users\\' + os_environ['USERNAME'] + '\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup')
	if os_path.exists(path + '\\' + file):
		if state == True:
			with open(autorun_path + '\\' + name + ".bat", "w") as tempfile:
				tempfile.write('@cd ' + path + '\n@start "" ' + file)
		else:
			try:
				os_remove(autorun_path + '\\' + name + '.bat')
			except FileNotFoundError:
				raise FileNotFoundError('nirpy - Failed to remove file: ' + file + ' from startup')
	else:
		raise FileNotFoundError('nirpy - Failed to add file: ' + file + ' to startup')


# Load nircmdc.exe
def load(link=''):
	if os_path.exists(nircmdc_file_path):
		return True
	else:
		if link != '':
			try:
				nircmdc_temp_file = wget_download(link)
			except:
				raise ConnectionError('nirpy - This link does not exist: ' + link)
		else:
			nircmdc_temp_file = wget_download('https://raw.githubusercontent.com/LimerBoy/nirpy/master/nircmdc.exe')
		shutil_move(nircmdc_temp_file, nircmdc_file_path)
		return True

# Unload (delete) nircmdc.exe from system
def unload():
	if os_path.exists(nircmdc_file_path):
		os_remove(nircmdc_file_path)
		return True
	else:
		raise FileNotFoundError('nirpy - Failed to delete file. It does not exist')
		
# Execute nircmdc command
def execute(command, wait=False, priority='NORMAL'):
	if wait == True:
		wait_string = '/wait '
	else:
		wait_string = ' '

	if os_path.exists(nircmdc_file_path):
		os_system('@start /MIN /B /' + priority + ' ' + wait_string +  nircmdc_file_path + ' ' + command)
	else:
		raise FileNotFoundError('nirpy - You don\'t loaded nircmdc.exe please make nirpy.load() after importing this module.')

# Execute system command
def system(command, wait=False, priority='NORMAL'):
	execute('execmd ' + command, wait, priority)

if __name__ == '__main__':
	input('nirpy - I\'m need be imported!')