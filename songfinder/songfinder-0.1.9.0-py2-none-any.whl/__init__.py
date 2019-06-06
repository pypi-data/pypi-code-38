# -*- coding: utf-8 -*-

__version__ = "0.1.9.0"
__author__ = "danbei"
__appName_ = "songfinder"


import Tkinter as tk
from PIL import ImageTk
import os
import sys
import warnings

from songfinder import screen
from songfinder import splash
from songfinder import globalvar

def songFinderGui():
	# Creat main window and splash icon
	fenetre = tk.Tk()
	fenetre.withdraw()
	screens = screen.Screens()
	try:
		splashScreen = splash.Splash(fenetre, os.path.join(globalvar.dataPath, 'icon.png'), 0, screens[0][0])
		splashScreen.__enter__()
	except Exception as e:
		warnings.warn(str(e))

	# Compile cython file and cmodules
	if not globalvar.portable:
		try:
			import subprocess
			import distutils.spawn
			python = distutils.spawn.find_executable('python')
			if python:
				command = python + ' setup_cython.py build_ext --inplace'
				proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				out, err = proc.communicate()
				if out:
					print(out)
					print(err)
		except Exception as e:
			warnings.warn(str(e))

	from songfinder import interface

	# Get command line args for opening songs and sets
	fileIn = None
	if len(sys.argv) > 1:
		fileIn = sys.argv[1]

	# Set bar icon
	try:
		if os.name == 'posix':
			img = ImageTk.PhotoImage(file = os.path.join(globalvar.dataPath, 'icon.png') )
			fenetre.tk.call('wm', 'iconphoto', fenetre._w, img)
		else:
			fenetre.iconbitmap( os.path.join(globalvar.dataPath, 'icon.ico'))
	except Exception as e:
		warnings.warn(str(e))

	songFinder = interface.Interface(fenetre, screens=screens, fileIn=fileIn)
	fenetre.title('Song Finder')
	fenetre.protocol("WM_DELETE_WINDOW", songFinder.quit)

	# Set windows size
	fenetre.update_idletasks()
	fen_w = fenetre.winfo_reqwidth()
	fen_h = fenetre.winfo_reqheight()
	fenetre.minsize(fen_w, fen_h)
	fenetre.geometry( screen.get_size(fen_w, fen_h, screens[0][0], 5) )
	fenetre.resizable(width=True, height=True)

	try:
		splashScreen.__exit__()
	except Exception as e:
		warnings.warn(str(e))
	fenetre.deiconify()
	fenetre.lift()
	fenetre.mainloop()

if __name__ == '__main__':
	songFinderGui()
