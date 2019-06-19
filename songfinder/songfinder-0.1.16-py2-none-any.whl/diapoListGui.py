# -*- coding: utf-8 -*-
# ~ from __future__ import division

import Tkinter as tk
import warnings

class DiapoListGui(object):
	def __init__(self, frame, diapoList=None, callback=None, start=0):
		self._diapoList = diapoList
		self._callback = callback
		self._listBox = tk.Listbox(frame, selectmode=tk.BROWSE, width=40)
		self._scrollBar = tk.Scrollbar(frame, command=self._listBox.yview)
		self._listBox['yscrollcommand'] = self._scrollBar.set

		self._listBox.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
		self._scrollBar.pack(side=tk.LEFT, fill=tk.Y)
		self._listBox.focus_set()

		self._listBox.bind("<KeyRelease-Up>", self.getSelect)
		self._listBox.bind("<KeyRelease-Down>", self.getSelect)
		self._listBox.bind("<ButtonRelease-1>", self.getSelect)

		self._listBox.select_set(start)
		self._listBox.activate(start)

	def getSelect(self, event=None):
		if self._diapoList:
			if self._listBox.curselection():
				self._diapoList.number = int(self._listBox.curselection()[0])
			if self._callback:
				self._callback()
		else:
			warnings.warn('No diapo list have been bind to the diapo list gui.')

	def select(self):
		if self._diapoList:
			self._listBox.select_clear(0, tk.END)
			self._listBox.select_set(self._diapoList.number)
			self._listBox.activate(self._diapoList.number)
		else:
			warnings.warn('No diapo list have been bind to the diapo list gui.')

	def write(self):
		self._listBox.delete(0,'end')
		if self._diapoList:
			for i, diapo in enumerate(self._diapoList.getList()):
				self._listBox.insert(i, diapo.title)
				if diapo.etype == 'empty':
					self._listBox.itemconfig(i, bg='green')
				elif diapo.etype == 'image':
					self._listBox.itemconfig(i, bg='blue')
			self.select()
		else:
			warnings.warn('No diapo list have been bind to the diapo list gui.')

	def width(self):
		return self._listBox.winfo_reqwidth() + self._scrollBar.winfo_reqwidth()

	def bindDiapoList(self, diapoList):
		self._diapoList = diapoList
		self._diapoList.bindGuiUpdate(self.select)
		self.write()

	def bindCallback(self, callback):
		self._callback = callback

	def unBindCallback(self):
		self._callback = None
