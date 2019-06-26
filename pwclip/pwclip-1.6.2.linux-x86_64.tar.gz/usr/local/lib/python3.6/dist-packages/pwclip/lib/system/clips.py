#!/usr/bin/env python3
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
#
"""
clips - clipboard for various systems
"""
from os import environ, name as osname

from platform import system

from time import sleep, time

from subprocess import Popen, PIPE, DEVNULL

def clips():
	"""return `copy`, `paste` as system independent functions"""
	def winclips():
		global HGLOBAL, LPVOID, DWORD, LPCSTR, \
			   INT, HWND, HINSTANCE, HMENU, BOOL, UINT, HANDLE
		import contextlib
		from ctypes import \
			c_size_t, sizeof, c_wchar_p, \
			get_errno, c_wchar, windll, CDLL, memmove
		from ctypes.wintypes import \
			HGLOBAL, LPVOID, DWORD, \
			LPCSTR, INT, HWND, HINSTANCE, HMENU, BOOL, UINT, HANDLE
		class CheckedCall(object):
			def __init__(self, f):
				super(CheckedCall, self).__setattr__("f", f)
			def __call__(self, *args):
				ret = self.f(*args)
				if not ret and get_errno():
					raise PyperclipWindowsException(
						"Error calling " + self.f.__name__)
				return ret
			def __setattr__(self, key, value):
				setattr(self.f, key, value)
		msvcrt = CDLL('msvcrt')
		mkwin = CheckedCall(windll.user32.CreateWindowExA)
		mkwin.argtypes = [
                                        DWORD, LPCSTR, LPCSTR,
                                        DWORD, INT, INT, INT, INT,
                                        HWND, HMENU, HINSTANCE, LPVOID]
		mkwin.restype = HWND
		rmwin = CheckedCall(windll.user32.DestroyWindow)
		rmwin.argtypes = [HWND]
		rmwin.restype = BOOL
		mkclip = windll.user32.OpenClipboard
		mkclip.argtypes = [HWND]
		mkclip.restype = BOOL
		doclip = CheckedCall(windll.user32.CloseClipboard)
		doclip.argtypes = []
		doclip.restype = BOOL
		noclip = CheckedCall(windll.user32.EmptyClipboard)
		noclip.argtypes = []
		noclip.restype = BOOL
		isclip = CheckedCall(windll.user32.GetClipboardData)
		isclip.argtypes = [UINT]
		isclip.restype = HANDLE
		onclip = CheckedCall(windll.user32.SetClipboardData)
		onclip.argtypes = [UINT, HANDLE]
		onclip.restype = HANDLE
		alloc = CheckedCall(windll.kernel32.GlobalAlloc)
		alloc.argtypes = [UINT, c_size_t]
		alloc.restype = HGLOBAL
		dolock = CheckedCall(windll.kernel32.GlobalLock)
		dolock.argtypes = [HGLOBAL]
		dolock.restype = LPVOID
		unlock = CheckedCall(windll.kernel32.GlobalUnlock)
		unlock.argtypes = [HGLOBAL]
		unlock.restype = BOOL
		wcslen = CheckedCall(msvcrt.wcslen)
		wcslen.argtypes = [c_wchar_p]
		wcslen.restype = UINT
		GMEM_MOVEABLE = 0x0002
		CF_UNICODETEXT = 13
		@contextlib.contextmanager
		def window():
			hwnd = mkwin(0, b"STATIC", None, 0, 0, 0, 0, 0,
									   None, None, None, None)
			try:
				yield hwnd
			finally:
				rmwin(hwnd)
		@contextlib.contextmanager
		def clipboard(hwnd):
			t = time() + 0.5
			success = False
			while time() < t:
				success = mkclip(hwnd)
				if success:
					break
				time.sleep(0.01)
			if not success:
				raise PyperclipWindowsException("Error calling mkclip")
			try:
				yield
			finally:
				doclip()
		def _copy(text, mode='pb'):
			with window() as hwnd:
				with clipboard(hwnd):
					noclip()
					if text:
						count = wcslen(text) + 1
						handle = alloc(GMEM_MOVEABLE,
												 count * sizeof(c_wchar))
						locked_handle = dolock(handle)
						memmove(
							c_wchar_p(locked_handle),
							c_wchar_p(text), count * sizeof(c_wchar))
						unlock(handle)
						onclip(CF_UNICODETEXT, handle)
		def _paste(_=None):
			with clipboard(None):
				handle = isclip(CF_UNICODETEXT)
				if not handle:
					__clp = ""
				__clp = c_wchar_p(handle).value, c_wchar_p(handle).value
			return __clp
		return _copy, _paste

	def osxclips():
		""""OSX clipboards"""
		def _copy(text, mode=None):
			"""osx copy function"""
			text = text if text else ''
			if mode != 'b':
				with Popen(['pbcopy'], stdin=PIPE, close_fds=True) as prc:
					prc.communicate(input=str(text).encode('utf-8'))
			return False
		def _paste(_=None):
			"""osx paste function"""
			with Popen(['pbpaste'], stdout=PIPE, close_fds=True) as prc:
				out, _ = prc.communicate()
				return out.decode('utf-8'), None
		
		return _copy, _paste

	def linclips():
		"""linux clipboards"""
		dsp = ':0'
		if 'DISPLAY' in environ.keys():
			dsp = '%s'%(environ['DISPLAY'])
		environ['DISPLAY'] = dsp
		def _copy(text, mode='p'):
			"""linux copy function"""
			xsel = 'xsel -l /dev/null -i'
			text = text if text else ''
			for m in mode:
				xsel = '%s %s'%(xsel, '-%s'%m)
				with Popen(
                      xsel, stdin=PIPE, stderr=DEVNULL,
                      stdout=DEVNULL, shell=True) as prc:
					prc.communicate(input=str(text).encode('utf-8'))
					prc.terminate()
		def _paste(mode='p'):
			"""linux paste function"""
			if mode == 'p':
				out, _ = Popen(
                   'xsel -l /dev/null -n -p',
                   stdout=PIPE, stderr=DEVNULL, shell=True).communicate()
				ret = out.decode()
			elif mode == 'b':
				out, _ = Popen(
                   'xsel -l /dev/null -n -b',
                   stdout=PIPE, stderr=DEVNULL, shell=True).communicate()
				ret = out.decode()
			else:
				pout, _ = Popen(
                   'xsel -l /dev/null -n -p',
                   stdout=PIPE, stderr=DEVNULL, shell=True).communicate()
				bout, _ = Popen(
                   'xsel -l /dev/null -n -b',
                   stdout=PIPE, stderr=DEVNULL, shell=True).communicate()
				ret = pout.decode(), bout.decode()
			return ret
		return _copy, _paste
	# decide which copy, paste functions to return [windows|mac|linux] mainly
	if osname == 'nt' or system() == 'Windows':
		return winclips()
	elif osname == 'mac' or system() == 'Darwin':
		return osxclips()
	return linclips()

copy, paste = clips()
