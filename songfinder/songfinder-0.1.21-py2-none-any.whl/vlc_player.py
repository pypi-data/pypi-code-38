#! /usr/bin/python
# -*- coding: utf-8 -*-

#
# tkinter example for VLC Python bindings
# Copyright (C) 2015 the VideoLAN team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#
"""A simple example for VLC python bindings using tkinter. Uses python 3.4

Author: Patrick Fay
Date: 23-09-2015
"""

# import external libraries
import vlc
import sys

#~ import Tkinter as Tk
import ttk
from tkFileDialog import askopenfilename
from tkMessageBox import *


# import standard libraries
import os
#~ import pathlib
import threading
#~ from threading import Thread, Event
#~ import time
import platform

from fonctions import *

class ttkTimer(threading.Thread):
	"""a class serving same function as wxTimer... but there may be better ways to do this
	"""
	def __init__(self, callback, tick):
		threading.Thread.__init__(self)
		self.callback = callback
		self.stopFlag = threading.Event()
		self.tick = tick
		self.iters = 0

	def run(self):
		while not self.stopFlag.wait(self.tick):
			self.iters += 1
			self.callback()

	def stop(self):
		self.stopFlag.set()

	def get(self):
		return self.iters

class Player(Frame):
	"""The main window has to deal with events.
	"""
	def __init__(self, parent, fen_gestion, videopanel, title=None):
		Frame.__init__(self, parent)
		self.grid()


		self.parent = parent

		if title == None:
			title = "tk_vlc"
		self.parent.title(title)
		#~ --------------------
		self.parent.overrideredirect(1)

		# The second panel holds controls
		self.player = None
		self.videopanel = videopanel

		self.canvas = Canvas(self.videopanel).pack(fill=BOTH,expand=1)
		self.videopanel.pack(fill=BOTH,expand=1)

		s = ttk.Style()
		s.configure('My.TFrame')


		self.ctrlpanel = ttk.Frame(fen_gestion, style='My.TFrame')
		message = ttk.Label(self.ctrlpanel, text="Lecteur multimedia : ")
		stop   = ttk.Button(self.ctrlpanel, text="Stop", command=self.OnStop)
		self.play_pause_button   = Button(self.ctrlpanel, text="Play/Pause", command=self.Play_Pause)
		volume = ttk.Label(self.ctrlpanel, text="Volume")
		self.mute_button = Button(self.ctrlpanel, text="Mute", command=self.mute)
		self.volume_pad_button = Button(self.ctrlpanel, text="Volume Pad", command=self.volume_pad, relief=RAISED)
		message.grid(row=0, column=0, rowspan=1, columnspan=1, sticky='ne')
		self.play_pause_button.grid(row=2, column=0, rowspan=1, columnspan=1)
		stop.grid(row=3, column=0, rowspan=1, columnspan=1)
		volume.grid(row=4, column=0, rowspan=2, columnspan=1)
		self.mute_button.grid(row=4, column=2, rowspan=2, columnspan=1)
		self.volume_pad_button.grid(row=4, column=3, rowspan=2, columnspan=1)
		self.play_on = 0
		self.mute_on = 0
		self.pad_on = 0
		self.volume_var = IntVar()
		self.volume_var.set(50)
		self.volslider = Scale(self.ctrlpanel, variable=self.volume_var, command=self.volume_sel,
				from_=0, to=100, orient=HORIZONTAL, length=100)
		self.volslider.grid(row=3, column=1, rowspan=2, columnspan=1)
		self.ctrlpanel.grid(row=0, column=3, rowspan=1, columnspan=5)

		self.ctrlpanel2 = ttk.Frame(fen_gestion, style='My.TFrame')
		self.scale_var = DoubleVar()
		self.timeslider_last_val = ""
		self.timeslider = Scale(self.ctrlpanel2, variable=self.scale_var, command=self.scale_sel,
				from_=0, to=1000, orient=HORIZONTAL, length=500)
		self.timeslider.grid(row=6, column=0, rowspan=1, columnspan=1)
		self.timeslider_last_update = time.time()
		self.ctrlpanel2.grid(row=6, column=3, rowspan=1, columnspan=5)


		# VLC player controls
		self.Instance = vlc.Instance()
		self.player = self.Instance.media_player_new()

		# below is a test, now use the File->Open file menu
		#media = self.Instance.media_new('output.mp4')
		#self.player.set_media(media)
		#self.player.play() # hit the player button
		#self.player.video_set_deinterlace(str_to_bytes('yadif'))
		#~ self.player.audio_set_volume(50)
		#~ self.volume_sel()

		self.timer = ttkTimer(self.OnTimer, 1.0)
		self.timer.start()
		self.parent.update()

		#self.player.set_hwnd(self.GetHandle()) # for windows, OnOpen does does this

		fen_gestion.bind_all("<space>", self.Play_Pause)

	def OnExit(self, evt=0):
		"""Closes the window.
		"""
		self.Close()

	def OnOpen(self):
		"""Pop up a new dialow window to choose a file, then play the selected file.
		"""
		# if a file is already running, then stop it.
		self.OnStop()

		# Create a file dialog opened in the current home directory, where
		# you can display all kind of files, having as title "Choose a file".
		#~ p = pathlib.Path(os.path.expanduser("~"))
		fullname =  askopenfilename(title = "choose your file",filetypes = (("all files","*.*"),("mp4 files","*.mp4")))
		if os.path.isfile(fullname):
			dirname  = os.path.dirname(fullname)
			filename = os.path.basename(fullname)
			# Creation
			self.Media = self.Instance.media_new(str(os.path.join(dirname, filename)))
			self.player.set_media(self.Media)
			# Report the title of the file chosen
			#title = self.player.get_title()
			#  if an error was encountred while retriving the title, then use
			#  filename
			#if title == -1:
			#    title = filename
			#self.SetTitle("%s - tkVLCplayer" % title)

			# set the window id where to render VLC's video output
			if platform.system() == 'Windows':
				self.player.set_hwnd(self.GetHandle())
			else:
				self.player.set_xwindow(self.GetHandle()) # this line messes up windows
			# FIXME: this should be made cross-platform
			self.Play_Pause()
			self.focus_set()

			# set the volume slider to the current volume
			#self.volslider.SetValue(self.player.audio_get_volume() / 2)
			#~ self.volslider.set(self.player.audio_get_volume())

	def Open(self, fullname):
		self.OnStop()

		if os.path.isfile(fullname):
			dirname  = os.path.dirname(fullname)
			filename = os.path.basename(fullname)
			# Creation
			self.Media = self.Instance.media_new(str(os.path.join(dirname, filename)))
			self.player.set_media(self.Media)

			if platform.system() == 'Windows':
				self.player.set_hwnd(self.GetHandle())
			else:
				self.player.set_xwindow(self.GetHandle())
			self.Play_Pause()
			self.focus_set()

	def GetHandle(self):
		return self.videopanel.winfo_id()

	#def OnPause(self, evt):
	def Play_Pause(self, event=0):
		if self.play_on == 1 :
			self.player.pause()
			self.play_on = 0
			self.play_pause_button.config(relief=RAISED)
		elif self.play_on == 0 :
			if not self.player.get_media():
				self.OnOpen()
			if self.player.play() == -1 :
				showerror("Attention", "Unable to play.")
			else :
				self.play_on = 1
				self.play_pause_button.config(relief=SUNKEN)


	def OnStop(self):
		"""Stop the player.
		"""
		self.player.stop()
		self.play_on = 0
		self.play_pause_button.config(relief=RAISED)
		# reset the time slider
		self.timeslider.set(0)

	def OnTimer(self):
		"""Update the time slider according to the current movie time.
		"""
		if self.player == None:
			return
		# since the self.player.get_length can change while playing,
		# re-set the timeslider to the correct range.
		length = self.player.get_length()
		dbl = length * 0.001
		self.timeslider.config(to=dbl)

		# update the time on the slider
		tyme = self.player.get_time()
		if tyme == -1:
			tyme = 0
		dbl = tyme * 0.001
		self.timeslider_last_val = ("%.0f" % dbl) + ".0"
		# don't want to programatically change slider while user is messing with it.
		# wait 2 seconds after user lets go of slider
		if time.time() > (self.timeslider_last_update + 2.0):
			self.timeslider.set(dbl)

	def scale_sel(self, evt):
		if self.player == None:
			return
		nval = self.scale_var.get()
		sval = str(nval)
		if self.timeslider_last_val != sval:
			# this is a hack. The timer updates the time slider.
			# This change causes this rtn (the 'slider has changed' rtn) to be invoked.
			# I can't tell the difference between when the user has manually moved the slider and when
			# the timer changed the slider. But when the user moves the slider tkinter only notifies
			# this rtn about once per second and when the slider has quit moving.
			# Also, the tkinter notification value has no fractional seconds.
			# The timer update rtn saves off the last update value (rounded to integer seconds) in timeslider_last_val
			# if the notification time (sval) is the same as the last saved time timeslider_last_val then
			# we know that this notification is due to the timer changing the slider.
			# otherwise the notification is due to the user changing the slider.
			# if the user is changing the slider then I have the timer routine wait for at least
			# 2 seconds before it starts updating the slider again (so the timer doesn't start fighting with the
			# user)
			self.timeslider_last_update = time.time()
			mval = "%.0f" % (nval * 1000)
			self.player.set_time(int(mval)) # expects milliseconds


	def volume_sel(self, evt=0):
		if self.player == None:
			return
		volume = self.volume_var.get()
		if volume > 100:
			volume = 100
		if self.player.audio_set_volume(volume) == -1:
			showerror("Attention", "Failed to set volume")

	def volume_pad(self, evt=0):
		if self.player == None:
			return
		volume = self.volume_var.get()
		if self.pad_on == 1 :
			volume = min(volume*2, 100)
			self.pad_on = 0
			self.volume_pad_button.config(relief=RAISED)
		elif self.pad_on == 0 :
			volume = min(volume/2, 100)
			self.pad_on = 1
			self.volume_pad_button.config(relief=SUNKEN)
		self.volume_var.set(volume)
		if self.player.audio_set_volume(volume) == -1:
			showerror("Attention", "Failed to set volume")

	def mute(self, evt=0):
		if self.player == None:
			return
		if self.mute_on == 1 :
			volume = min(self.volume_var.get(), 100)
			self.mute_on = 0
			self.mute_button.config(relief=RAISED)
		elif self.mute_on == 0 :
			volume = 0
			self.mute_on = 1
			self.mute_button.config(relief=SUNKEN)

		if self.player.audio_set_volume(volume) == -1:
			showerror("Attention", "Failed to set volume")



	def OnToggleVolume(self, evt):
		"""Mute/Unmute according to the audio button.
		"""
		is_mute = self.player.audio_get_mute()

		self.player.audio_set_mute(not is_mute)
		# update the volume slider;
		# since vlc volume range is in [0, 200],
		# and our volume slider has range [0, 100], just divide by 2.
		self.volume_var.set(self.player.audio_get_volume())

	def OnSetVolume(self):
		"""Set the volume according to the volume sider.
		"""
		volume = self.volume_var.get()
		# vlc.MediaPlayer.audio_set_volume returns 0 if success, -1 otherwise
		if volume > 100:
			volume = 100
		if self.player.audio_set_volume(volume) == -1:
			showerror("Attention", "Failed to set volume")


def Tk_get_root():
	if not hasattr(Tk_get_root, "root"): #(1)
		Tk_get_root.root= Tk()  #initialization call is inside the function
	return Tk_get_root.root

def _quit():
	print("_quit: bye")
	root = Tk_get_root()
	root.quit()     # stops mainloop
	root.destroy()  # this is necessary on Windows to prevent
					# Fatal Python Error: PyEval_RestoreThread: NULL tstate
	os._exit(1)

if __name__ == "__main__":
	# Create a App(), which handles the windowing system event loop
	root = Tk_get_root()
	root.protocol("WM_DELETE_WINDOW", _quit)
	fen_gestion = Toplevel()
	player = Player(root, fen_gestion, title="tkinter vlc")
	# show the player window centred and run the application
	root.mainloop()
