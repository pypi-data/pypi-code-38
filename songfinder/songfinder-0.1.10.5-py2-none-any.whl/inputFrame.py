# -*- coding: utf-8 -*-
import Tkinter as TK
import ttk

def make_method(func, instance):
	return ( lambda *args, **kwargs: func(instance, *args, **kwargs) )

class entryField(object, TK.Frame):
	def __init__(self, parentFrame, width=None, text='', packing=TK.TOP, **kwargs):
		TK.Frame.__init__(self, parentFrame, **kwargs)

		self._text = TK.Label(self, text=text)
		self._input = TK.Entry(self, state=TK.NORMAL)

		self._text.pack(side=packing)
		self._input.pack(side=packing, fill=TK.X, expand=1)

		for name in TK.Entry.__dict__.keys():
			_method = make_method(TK.Entry.__dict__[name], self._input)
			setattr(self, name, _method)
		for name in set(TK.Label.__dict__.keys()) - set(TK.Entry.__dict__.keys()):
			_method = make_method(TK.Label.__dict__[name], self._text)
			setattr(self, name, _method)

	def bind(self, *args, **kwargs):
		self._input.bind(*args, **kwargs)

	def focus_set(self, *args, **kwargs):
		self._input.focus_set(*args, **kwargs)

class TextField(object, TK.Frame):
	def __init__(self, parentFrame, width=None, text='', packing=TK.TOP, state=TK.NORMAL, **kwargs):
		TK.Frame.__init__(self, parentFrame, **kwargs)

		self._text = TK.Label(self, text=text)
		self._input = TK.Text(self, width=width, height=1, state=state)

		self._text.pack(side=packing)
		self._input.pack(side=packing, fill=TK.X, expand=1)

		for name in TK.Text.__dict__.keys():
			_method = make_method(TK.Text.__dict__[name], self._input)
			setattr(self, name, _method)
		for name in set(TK.Label.__dict__.keys()) - set(TK.Text.__dict__.keys()):
			_method = make_method(TK.Label.__dict__[name], self._text)
			setattr(self, name, _method)

	def bind(self, *args, **kwargs):
		self._input.bind(*args, **kwargs)

	def focus_set(self, *args, **kwargs):
		self._input.focus_set(*args, **kwargs)

	@property
	def state(self):
		return self._input['state']

	@state.setter
	def state(self, value):
		self._input['state'] = value
