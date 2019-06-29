# -*- coding: utf-8 -*-

__version__ = "0.1.25"
__author__ = "danbei"
__appName_ = "songfinder"


try:
	import tkinter as tk
except ImportError:
	import Tkinter as tk
from PIL import ImageTk
import os
import sys
import warnings
import traceback
import argparse

from songfinder import screen
from songfinder import splash
from songfinder import globalvar
from songfinder import messages as tkMessageBox
from songfinder import guiHelper
from songfinder import webServer
from songfinder import fileConverter

def _gui(fenetre, fileIn=None):
	# Creat main window and splash icon
	fenetre.withdraw()
	screens = screen.Screens()

	with splash.Splash(fenetre, os.path.join(globalvar.dataPath, 'icon.png'), 0, screens[0][0]):
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
			except Exception:
				warnings.warn(traceback.format_exc())

		from songfinder import interface

		# Set bar icon
		try:
			if os.name == 'posix':
				img = ImageTk.PhotoImage(file = os.path.join(globalvar.dataPath, 'icon.png') )
				fenetre.tk.call('wm', 'iconphoto', fenetre._w, img)
			else:
				fenetre.iconbitmap( os.path.join(globalvar.dataPath, 'icon.ico'))
		except Exception:
			warnings.warn(traceback.format_exc())
		if fileIn :
			fileIn = fileIn[0]
		songFinder = interface.Interface(fenetre, screens=screens, fileIn=fileIn)
		fenetre.title('SongFinder')
		fenetre.protocol("WM_DELETE_WINDOW", songFinder.quit)

		# Set windows size
		fenetre.update_idletasks()
		fen_w = fenetre.winfo_reqwidth()
		fen_h = fenetre.winfo_reqheight()
		fenetre.minsize(fen_w, fen_h)
		fenetre.geometry( screen.get_size(fen_w, fen_h, screens[0][0], 5) )
		fenetre.resizable(width=True, height=True)

	fenetre.deiconify()
	guiHelper.upFront(fenetre)
	fenetre.mainloop()

def _webServer():
	server = webServer.FlaskServer()
	server.run()

def _song2markdown(fileIn, fileOut):
	converter = fileConverter.Converter()
	converter.makeSubDirOn()
	converter.markdown(fileIn, fileOut)

def _song2html(fileIn, fileOut):
	converter = fileConverter.Converter()
	converter.makeSubDirOn()
	converter.html(fileIn, fileOut)

def dir_path(path):
	if os.path.isdir(path):
		return path
	else:
		raise argparse.ArgumentTypeError("readable_dir:%s is not a valid path"%path)

def _parseArgs():
	arg_parser = argparse.ArgumentParser()
	arg_parser = argparse.ArgumentParser(description="%s v%s"% (globalvar.appName, __version__),
									formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	arg_parser.add_argument("-f", "--file",
						nargs=1,
						metavar=('inputFile',),
						help="Song file or set file to open")

	arg_parser.add_argument("-m", "--songtomarkdown",
						nargs=2,
						metavar=('song[File/Dir]', 'markdown[File/Dir]'),
						help="Convert song file (xml or chordpro) files to markdown file")

	arg_parser.add_argument("-t", "--songtohtml",
						nargs=2,
						metavar=('song[File/Dir]', 'html[File/Dir]'),
						help="Convert song file (xml or chordpro) files to html file")

	arg_parser.add_argument("-w", "--webserver",
						action="store_true",
						default=False,
						help="Launch songfinder webserver")

	arg_parser.add_argument("-v", "--verbosity",
						type=int, choices=[0, 1, 2],
						help="Increase output verbosity")

	return arg_parser.parse_args()

def songFinderMain():
	args = _parseArgs()
	if args.webserver:
		_webServer()
	elif args.songtomarkdown:
		_song2markdown(*args.songtomarkdown)
	elif args.songtohtml:
		_song2html(*args.songtohtml)
	else:
		fenetre = tk.Tk()
		try:
			_gui(fenetre, fileIn=args.file)
		except SystemExit:
			raise
		except:
			tkMessageBox.showerror('Erreur', traceback.format_exc())
			raise

if __name__ == '__main__':
	songFinderMain()
