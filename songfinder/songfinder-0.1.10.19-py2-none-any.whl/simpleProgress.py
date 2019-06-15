# -*- coding: utf-8 -*-
from __future__ import division

import Tkinter as tk
import ttk

class SimpleProgress(object):
	def __init__(self, papa, title, mode='determinate', screens=None, **kwargs):
		self._fen = tk.Toplevel(papa)
		self._fen.withdraw()
		self._fen.title('Progression')
		self._fen.lift()
		self._fen.focus_set()
		self._fen.resizable(False,False)
		self._mode = mode
		if screens:
			width = self._fen.winfo_width()
			height = self._fen.winfo_height()
			Xpos = (screens[0][1].w - width) // 2
			Ypos = (screens[0][1].h - height) // 2
			self._fen.geometry('+{}+{}'.format(Xpos, Ypos))

		self.prog = tk.Label(self._fen, text=title, justify='left')
		self.prog_bar = ttk.Progressbar(self._fen, orient="horizontal",
											length=200, mode=self._mode, \
											value=0.0)
		self.cancel = tk.Button(self._fen, text='Annuler', command=self._cancel)
		self.prog.pack(side=tk.TOP)
		self.prog_bar.pack(side=tk.TOP)
		self.cancel.pack(side=tk.TOP)
		self._counter = 0

	def start(self, total=100, steps=100):
		self._fen.deiconify()
		self._total = total
		self._ratio = (total+steps-1)//steps
		self.prog_bar["value"] = 0.0
		self.prog_bar["maximum"] = self._total
		self.prog_bar.start()

	def update(self):
		if self._mode == 'determinate':
			self._counter += 1
			self.prog_bar["value"] = self._counter
		if self._counter%self._ratio==0: # Lowers the graphical overhead
			self._fen.update()
			self._fen.lift()

	def stop(self):
		self.prog_bar.stop()
		self._fen.destroy()

	def _cancel(self):
		self.stop()
