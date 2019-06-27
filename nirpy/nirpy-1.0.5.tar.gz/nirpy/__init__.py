"""
#Module Created by LimerBoy with Love <3

* nircmdc: https://www.nirsoft.net/utils/nircmd.html
* nircmdc reference: https://nircmd.nirsoft.net

> Example usage:

import nirpy
nirpy.load() # if you pc is 64bit: nirpy.load(architecture=64)

# NIRCMDC.exe
nirpy.execute('monitor off')

# CMD.exe
nirpy.system('echo this is a system command!')

#Execute with high process priority
#Process priority: [LOW | NORMAL | HIGH | REALTIME]
nirpy.execute('savescreenshotfull desktop.png', priority='HIGH')

#Download file from internet.
file = nirpy.wget(link)

#Execute downloaded file.
nirpy.start(file)

#Add/Remove autorun
nirpy.autorun('C:\\Windows', 'notepad.exe', 'you_name', state=True) # Add notepad to startup
nirpy.autorun('C:\\Windows', 'notepad.exe', 'you_name', state=False) # Remove notepad from startup

#After executing you can use: 
nirpy.clean() #Clean nirpy cache
nirpy.unload() #Remove nirpy.exe


"""

# Check system
from platform import system as platform_system
if platform_system().lower() != 'windows':
	raise OSError('I\'m work only in Windows, system ' + platform_system() + ' not support')


# Import modules
from os import system as os_system
from os import path as os_path
from os import mkdir as os_mkdir
from os import remove as os_remove
from os import environ as os_environ
from os import startfile as os_startfile
from time import sleep as time_sleep
from shutil import move as shutil_move
from wget import download as wget_download
from random import randint as random_randint

# Create TEMP folder if is not exists
if not os_path.exists(os_environ['TEMP'] + '\\nirpy'):
	os_mkdir(os_environ['TEMP'] + '\\nirpy')

# Get file path
nircmdc_file_path = os_environ['TEMP'] + '\\nirpy\\nirpy.exe'

# Load file from URL
def wget(link):
	return wget_download(link)

# Start file
def start(file):
	os_startfile(file)


# Add to startup.
def autorun(path, file, name, state=True):
	autorun_path = (os_environ['SystemDrive'] + '\\Users\\' + os_environ['USERNAME'] + '\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup')
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
def load(architecture=32):
	if os_path.exists(nircmdc_file_path):
		return True
	else:	
		if architecture == 64:
			nircmdc_file_part = 'nircmdc'
		else:
			nircmdc_file_part = 'nircmd'

		nircmdc_temp_file = wget_download('https://raw.githubusercontent.com/LimerBoy/nirpy/master/' + nircmdc_file_part + '.exe')
	shutil_move(nircmdc_temp_file, nircmdc_file_path)
	return True

# Unload (delete) nircmdc.exe from system
def unload():
	if os_path.exists(nircmdc_file_path):
		os_remove(nircmdc_file_path)
		return True
	else:
		raise FileNotFoundError('nirpy - Failed to delete file. It does not exist')
		return False
		
# Clean temp nirpy cache
def clean():
	system('@cd %temp%\\nirpy && @del *.bat > NUL && @del *.vbs > NUL')

# Execute system command
def system(command):
	# Temp files names
	bat_script_path = os_environ['TEMP'] + '\\nirpy\\' + 'bat_script_' + str(random_randint(1, 100000)) + '.bat'
	vbs_script_path = os_environ['TEMP'] + '\\nirpy\\' + 'vbs_script_' + str(random_randint(1, 100000)) + '.vbs'
	# Temp files commands
	bat_script = '@' + command
	vbs_script = 'CreateObject(\"WScript.Shell\").Run \"cmd.exe /c ' + bat_script_path + '\", 0, false'
	# Write bat commands
	with open(bat_script_path, "w") as bat_script_write:
		bat_script_write.write(bat_script)
	# Write vbs commands
	with open(vbs_script_path, "w") as vbs_script_write:
		vbs_script_write.write(vbs_script)
	time_sleep(0.1)
	os_startfile(vbs_script_path)

# Execute nircmdc command
def execute(command, priority='NORMAL'):
	# Check nircmdc.exe file
	if os_path.exists(nircmdc_file_path):
		system('@start /MIN /B /' + priority + ' ' +  nircmdc_file_path + ' ' + command)
	else:
		raise FileNotFoundError('nirpy - You don\'t loaded nircmdc.exe please make nirpy.load() after importing this module.')

if __name__ == '__main__':
	input('nirpy - I\'m need be imported!')