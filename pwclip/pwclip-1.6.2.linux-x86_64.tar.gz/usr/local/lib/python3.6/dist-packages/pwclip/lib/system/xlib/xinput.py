"""xinput window"""
# -*- encoding: utf-8 -*-
#
# This file is free software by d0n <d0n@janeiskla.de>
#
# You can redistribute it and/or modify it under the terms of the GNU -
# Lesser General Public License as published by the Free Software Foundation
#
# This is distributed in the hope that it will be useful somehow.
#
# !WITHOUT ANY WARRANTY!
#
# Without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
from os import name as osname

from system.xlib.xenv import xenv

try:
	from tkinter import StringVar, Button, Entry, Frame, Label, Tk, TclError
except ImportError:
	from Tkinter import StringVar, Button, Entry, Frame, Label, Tk, TclError
try:
	import readline
except ImportError:
	pass

class XInput(Frame):
	"""password clipping class for tkinter.Frame"""
	inp = None
	def __init__(self, master, message, exchange='', noop=None, noin=None):
		xenv()
		self.noop = noop
		self.noin = noin
		self.exchg = exchange
		self.message = message
		Frame.__init__(self, master)
		self.pack()
		self.inputwindow()
	def _enterexit(self, _=None):
		"""exit by saving challenge-response for input"""
		self.inp = True if not self.input else self.input.get()
		self.quit()
	def _exit(self, _=None):
		"""just exit (for ESC mainly)"""
		self.quit()
	def inputwindow(self):
		"""password input window creator"""
		self.lbl = Label(self, text=self.message)
		self.lbl.pack()
		okside = {}
		clside = {}
		self.ok = Button(self)
		self.ok.bind("<Control-c>", self._exit)
		self.ok.bind("<Escape>", self._exit)
		self.ok.bind("<Return>", self._enterexit)
		self.input = False
		self.ok["command"] = self._enterexit
		okside = {'side': 'bottom'}
		if not self.noin:
			self.entry = Entry(self, show=self.exchg)
			self.entry.bind("<Return>", self._enterexit)
			self.entry.bind("<Control-c>", self._exit)
			self.entry.bind("<Escape>", self._exit)
			self.entry.focus_set()
			self.entry.pack()
			self.input = StringVar()
			self.entry["textvariable"] = self.input
			okside = {'side': 'left'}
		if not self.noop:
			self.cl = Button(self)
			self.cl.bind("<Escape>", self._exit)
			self.cl["text"] = "cancel"
			self.cl["command"] = self._exit
			clside = {'side': 'right'}
			#clside = {}
			#self.cl.pack(side="right")
			self.cl.pack(clside)
		self.ok["text"] = "ok"
		if self.noin:
			self.ok.focus_set()
		self.ok.pack(okside)

def _set_focus(window):
	"""os independent focus setter"""
	if osname == 'nt':
		window.after(1, lambda: window.focus_force())

def xinput(message='enter input'):
	"""x screen input window"""
	root = Tk()
	try:
		pwc = XInput(root, message, None)
	except KeyboardInterrupt:
		root.destroy()
	_set_focus(root)
	pwc.lift()
	pwc.mainloop()
	root.destroy()
	return pwc.inp

def xgetpass(message="input will not be displayed"):
	"""gui representing function"""
	root = Tk()
	try:
		pwc = XInput(root, message, exchange='*')
	except KeyboardInterrupt:
		root.destroy()
	_set_focus(root)
	pwc.lift()
	pwc.mainloop()
	root.destroy()
	return pwc.inp

def xmsgok(message='press ok to continue'):
	"""gui representing function"""
	root = Tk()
	try:
		pwc = XInput(root, message, noop=True, noin=True)
	except KeyboardInterrupt:
		root.destroy()
	_set_focus(root)
	pwc.lift()
	pwc.mainloop()
	root.destroy()

def xyesno(message='press ok to continue'):
	"""gui representing function"""
	root = Tk()
	try:
		pwc = XInput(root, message, noin=True)
	except KeyboardInterrupt:
		root.destroy()
	_set_focus(root)
	pwc.lift()
	pwc.mainloop()
	root.destroy()
	return pwc.inp


if __name__ == '__main__':
	exit(1)
