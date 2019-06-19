# -*- coding: utf-8 -*-

import tkMessageBox
import tkFileDialog
import _tkinter
import traceback

from songfinder import globalvar

def showerror(title, message, **kwargs):
	if globalvar.unittest is True:
		warnings.warn(message)
	else:
		try:
			tkMessageBox.showerror(title, message, **kwargs)
		except _tkinter.TclError:
			print('Error %s: %s'%(title, message))
			print('%s'%traceback.format_exc())

def showinfo(title, message, **kwargs):
	if globalvar.unittest is True:
		warnings.warn(message)
	else:
		try:
			tkMessageBox.showinfo(title, message, **kwargs)
		except _tkinter.TclError:
			print('Info %s: %s'%(title, message))
			print('%s'%traceback.format_exc())

def askyesno(title, message, **kwargs):
	if globalvar.unittest is True:
		warnings.warn(message)
		return False
	else:
		try:
			return tkMessageBox.askyesno(title, message)
		except _tkinter.TclError:
			print('Askyesno %s: %s'%(title, message))
			answer = None
			while answer not in ['y', 'Y', 'n', 'N']:
				answer = raw_input(message + ' (y/n)')
				if answer in ['y', 'Y']:
					return True
				elif answer in ['n', 'N']:
					return False
			print('%s'%traceback.format_exc())

def askdirectory(**kwargs):
	if globalvar.unittest is True:
		warnings.warn('askdirectory')
		return None
	else:
		try:
			return tkFileDialog.askdirectory(**kwargs)
		except _tkinter.TclError:
			print('Erro with askdirectory:\n%s'%traceback.format_exc())
			return None

def askopenfilename(**kwargs):
	if globalvar.unittest is True:
		warnings.warn('askopenfilename')
		return None
	else:
		try:
			return tkFileDialog.askopenfilename(**kwargs)
		except _tkinter.TclError:
			print('Erro with askopenfilename:\n%s'%traceback.format_exc())
			return None

def askopenfilenames(**kwargs):
	if globalvar.unittest is True:
		warnings.warn('askopenfilenames')
		return None
	else:
		try:
			return tkFileDialog.askopenfilenames(**kwargs)
		except _tkinter.TclError:
			print('Erro with askopenfilenames:\n%s'%traceback.format_exc())
			return None

def asksaveasfilename(**kwargs):
	if globalvar.unittest is True:
		warnings.warn('asksaveasfilename')
		return None
	else:
		try:
			return tkFileDialog.asksaveasfilename(**kwargs)
		except _tkinter.TclError:
			print('Erro with asksaveasfilename:\n%s'%traceback.format_exc())
			return None
