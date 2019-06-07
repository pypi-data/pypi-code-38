# coding: utf-8

import sys

import urwid
import urwid.raw_display
import urwid.web_display
from urwid.signals import connect_signal

import tool

from globalBase import *

#g.dialog = None
#g.loop = None       # urwid

# (name, fg, bg, mono, fgHigh, bgHigh)
palette = [
	('std', 'light gray', 'black'),
	('std_f', 'black', 'dark cyan'),
	('reset', 'std'),
	("reset_f", "std_f"),
	('bold', 'light gray,bold', 'black'),
	('bold_f', 'light gray,bold', 'dark cyan'),
	('underline', 'light gray,underline', 'black'),
	('underline_f', 'light gray,underline', 'dark cyan'),

	('redfg', 'dark red', 'black'),
	('redfgb', 'bold,dark red', 'black'),
	('redfg_f', 'light red', 'dark cyan'),
	('redfgb_f', 'bold,light red', 'dark cyan'),
	('greenfg', 'dark green', 'black'),
	('greenfgb', 'bold,dark green', 'black'),
	('greenfg_f', 'black', 'dark cyan'),
	('greenfgb_f', 'bold,light green', 'dark cyan'),
	('yellowfg', 'yellow', 'black'),
	('yellowfgb', 'bold,yellow', 'black'),
	('yellowfg_f', 'yellow', 'dark cyan'),
	('yellowfgb_f', 'bold,yellow', 'dark cyan'),
	('bluefg', 'dark blue', 'black'),
	('bluefgb', 'bold,dark blue', 'black'),
	('bluefg_f', 'light blue', 'dark cyan'),
	('bluefgb_f', 'bold,light blue', 'dark cyan'),
	('cyanfg', 'dark cyan', 'black'),
	('cyanfgb', 'bold,dark cyan', 'black'),
	('cyanfg_f', 'light gray', 'dark cyan'),
	('cyanfgb_f', 'bold,light gray', 'dark cyan'),
	('grayfg', 'dark gray', 'black'),
	('grayfg_f', 'white', 'dark cyan'),

	('redbg', 'black', 'dark red'),
	('yellowbgb', 'black,bold', 'yellow'),
	('yellowbgb_f', 'black,bold', 'dark cyan'),  # it...

	('reveal focus', "black", "dark cyan", "standout"),
]


class mButton(urwid.Button):
	"""
	Button without pre/post Text
	"""

	def __init__(self, label, on_press=None, user_data=None):
		self._label = urwid.wimp.SelectableIcon(label, 0)

		super(urwid.Button, self).__init__(self._label)
		# urwid.widget.WidgetWrap.__init__(self, self._label)

		# The old way of listening for a change was to pass the callback
		# in to the constructor.  Just convert it to the new way:
		if on_press:
			connect_signal(self, 'click', on_press, user_data)

		# self.set_label(label)


class mListBox(urwid.ListBox):
	def __init__(self, body):
		super().__init__(body)
		self.isViewContent = False
		self.maxrow = 0  # for view content

		self.itemCount = 0
		self.focusCb = None

		self.maxcol = 0

		# SimpleListWalker don't have focus cb
		if getattr(self.body, 'set_focus_changed_callback', None):
			self.body.set_focus_changed_callback(lambda newFocus: self.onFocusChanged(newFocus))

	def onFocusChanged(self, newFocus):
		if self.focusCb is not None:
			ret = self.focusCb(newFocus)
			if not ret:
				return

		# general process
		widget = self.focus
		widget.base_widget.set_label(widget.base_widget.markup[0])

		widget = self.body[newFocus]
		widget.base_widget.set_label(widget.base_widget.markup[1])


	def render(self, size, focus=False):
		super.render(size, focus)
		(maxcol, maxrow) = size
		self.maxcol = maxcol
		self.maxrow = maxrow

	def focusNext(self):
		cur = self.body.get_focus()
		if cur[1] >= len(self.body) - 1:
			return

		# for
		if self.offset_rows < self.maxrow-1:
			self.offset_rows += 1

		item,pos = self.body.get_next(cur[1])
		self.body.set_focus(pos)
		return item, pos

	def focusPrevious(self):
		row,pos = self.body.get_focus()
		if pos == 0:
			return

		if self.offset_rows > 0:
			self.offset_rows -= 1

		item, pos = self.body.get_prev(pos)
		self.body.set_focus(pos)
		return item, pos

	# TODO: scroll
	# working but a little bit...
	def scrollDown(self):
		pos = self.focus_position
		if pos >= len(self.body) - 1:
			return

		row,pos = self.body.get_next(pos)
		if self.isViewContent:
			pos = min(pos, max(0, len(self.body) - self.maxrow))    # prevent
		#self.set_focus(pos) -- should use body.set_focus for scroll
		self.body.set_focus(pos)

	def scrollUp(self):
		row,pos = self.body.get_focus()
		if pos == 0:
			return

		row,pos = self.body.get_prev(pos)

		self.body.set_focus(pos)

	def render(self, size, focus=False):
		(maxcol, self.maxrow) = size
		return super().render(size, focus)

	def set_focus(self, position, coming_from=None):
		if self.isViewContent:
			position = min(position, max(0, len(self.body) - self.maxrow))

		return super().set_focus(position, coming_from)

	def mouse_event(self, size, event, button, col, row, focus):
		if event == "mouse press":
			if button == 4:  # up
				for i in range(3):
					self.scrollUp()

			elif button == 5:  # down
				for i in range(3):
					self.scrollDown()

	def setFocusCb(self, cb):
		self.focusCb = cb



class cDialog(object):
	def __init__(self):
		self.mainWidget = None
		self.onExit = None

	def init(self):
		# something to do
		return True

	def unhandled(self, key):
		pass

	def inputFilter(self, keys, raw):
		return keys

	def close(self):
		if getattr(self, "onExit") and self.onExit is not None:
			self.onExit()
		else:
			raise urwid.ExitMainLoop

#def excludeKey(keys, target):
#	return [c for c in keys if c != target]

def filterKey(keys, keyName):
	if keyName in keys:
		keys.remove(keyName)
		return True
	else:
		return False


def termianl2plainText(ss):
	# source = "\033[31mFOO\033[0mBAR"
	st = ss.find("\x1b")
	if st == -1:
		return ss

	out = ""
	items = ss.split("\x1b")
	for at in items:
		# at == "" or first string
		if at.startswith("[K"):	# it... [K:fro...
			if len(at) > 2:
				out += at[2:]
			continue

		if at.find("m") == -1:
			out += at
			continue
		attr, text = at.split("m" ,1)
		if text != "":	# skip empty string
			out += text

	return out

def terminal2markup(ss, invert=0):
	# source = "\033[31mFOO\033[0mBAR"
	table = {"[1" :"bold", "[4" :"underline",
	         "[22" :"std" ,
	         "[24" :"std",
	         "[31" :'redfg',
	         "[32" :'greenfg',
	         "[33" :'yellowfg',
	         "[36" :'cyanfg',
	         "[41" :"redbg",
	         "[1;31" :"redfgb",
	         "[1;32" :"greenfgb",
	         "[1;33" :"yellowfgb",
	         "[1;34" :"bluefgb",
	         "[1;36" :"cyanfgb",
	         "[30;43" :"yellowbgb",
	         "[0" :'std',
	         "[" :'std'}
	st = ss.find("\x1b")
	if st == -1:
		return ss

	markup = []
	items = ss.split("\x1b")
	if not ss.startswith("\x1b"):
		markup.append(items[0])

	for at in items[1:]:
		if at.startswith("[K"):	# it... [K:fro...
			if len(at) > 2:
				markup.append(('std', at[2:]))
			continue

		try:
			attr, text = at.split("m" ,1)
			if text == "":	# skip empty string
				continue

			txtAttr = table[attr]
			if invert != 0:
				txtAttr += "_f"
			markup.append((txtAttr, text))
		except Exception as e:
			#print("at - %s - %s" % (at,e))
			#sys.exit(1)
			raise e

	if len(markup) == 0:
		return ""

	return markup

def editGen(label, text, cbChange):
	w = urwid.Edit(label, text)
	urwid.connect_signal(w, 'change', cbChange)
	#cbChange(w, text)
	# w = urwid.AttrWrap(w, 'edit')
	return w

def textGenTerminal(terminalText):
	line2 = terminal2markup(terminalText)
	txt = urwid.Text(line2)
	# txt.origText = terminalText
	return txt


def textListMakeTerminal(lstStr):
	outList = []
	for line in lstStr:
		outList.append(textGenTerminal(line))
	return outList


def btnListMakeTerminal(lstTerminal, onClick, isFirstFocus=True, doApply=None):
	"""
	[31와 같은 터미널 문자열을 지원한다.
	lstTerminal = list of (termianlText, attr)
	"""
	outList = []

	if len(lstTerminal) == 0:
		return outList

	# support string only list
	if not isinstance(lstTerminal[0], tuple):
		lstTerminal = [ (x, None) for x in lstTerminal ]

	for terminalTxt, attr in lstTerminal:
		if terminalTxt.strip() == "":
			continue

		markup = terminal2markup(terminalTxt, 0)
		markupF = terminal2markup(terminalTxt, 1)
		btn = btnGen(markup, markupF, attr, onClick, isFirstFocus, doApply)
		isFirstFocus = False
		outList.append(btn)

	return outList


def btnListMakeMarkup(lstMarkup, onClick, isFirstFocus=True, doApply=None):
	"""
	lstMarkup = list of (markup, text, attr)
	"""
	outList = []
	for markup, text, attr in lstMarkup:
		btn = btnGen((markup, text), (markup + "_f", text), attr, onClick, isFirstFocus, doApply)
		isFirstFocus = False
		outList.append(btn)

	return outList

def btnGen(markup, markupF, attr, onClick, isFocus=False, doApply=None):
	text2 = markupF if isFocus else markup
	btn = btnGenMarkup(text2, onClick, doApply)
	btn.base_widget.markup = (markup, markupF)
	btn.base_widget.attr = attr
	#btn.base_widget.origTxt = terminalText

	return btn

def btnGenMarkup(markup, onClick, doApply=None):
	btn = mButton(markup, onClick)
	if doApply is not None:
		doApply(btn)

	btn = urwid.AttrMap(btn, None, "reveal focus")
	return btn

def popupMsg(title, ss, width=50):
	def onCloseBtn(btn):
		g.loop.widget = g.loop.widget.bottom_w

	txtMsg = urwid.Text(ss)
	btnClose = urwid.Button("Close", onCloseBtn)
	popup = urwid.LineBox(urwid.Pile([('pack', txtMsg), ('pack', btnClose)]), title)
	g.loop.widget = urwid.Overlay(urwid.Filler(popup), g.loop.widget, 'center', width, 'middle', 10)

def popupAsk(title, ss, onOk, onCancel = None):
	def onClickBtn(btn):
		g.loop.widget = g.loop.widget.bottom_w
		if btn == btnYes:
			onOk()
		elif btn == btnNo:
			if onCancel is not None:
				onCancel()

	txtMsg = urwid.Text(ss)
	btnYes = urwid.Button("Yes", onClickBtn)
	btnNo = urwid.Button("No", onClickBtn)
	popup = urwid.LineBox(urwid.Pile([('pack', txtMsg), ('pack', urwid.Columns([btnYes, btnNo]))]), title)
	g.loop.widget = urwid.Overlay(urwid.Filler(popup), g.loop.widget, 'center', 40, 'middle', 5)

def popupAsk3(title, ss, btnName1, btnName2, btnName3, onBtn1, onBtn2, onBtn3 = None):
	def onClickBtn(btn):
		if btn == btnB1:
			onBtn1()
		elif btn == btnB2:
			onBtn2()
		elif btn == btnB3:
			if onBtn3 is not None:
				onBtn3()

		g.loop.widget = g.loop.widget.bottom_w

	txtMsg = urwid.Text(ss)
	btnB1 = urwid.Button(btnName1, onClickBtn)
	btnB2 = urwid.Button(btnName2, onClickBtn)
	btnB3 = urwid.Button(btnName3, onClickBtn)
	popup = urwid.LineBox(urwid.Pile([('pack', txtMsg), ('pack', urwid.Columns([btnB1, btnB2, btnB3]))]), title)
	g.loop.widget = urwid.Overlay(urwid.Filler(popup), g.loop.widget, 'center', 40, 'middle', 5)

def popupInput(title, ss, onOk, onCancel = None, width=40):
	def onClickBtn(btn):
		if btn == btnOk:
			onOk(edInput.edit_text)
		elif btn == btnCancel:
			if onCancel is not None:
				onCancel()

		g.loop.widget = g.loop.widget.bottom_w

	edInput = urwid.Edit(ss)
	btnOk = urwid.Button("OK", onClickBtn)
	btnCancel = urwid.Button("Cancel", onClickBtn)
	popup = urwid.LineBox(urwid.Pile([('pack', edInput), ('pack', urwid.Columns([btnOk, btnCancel]))]), title)
	g.loop.widget = urwid.Overlay(urwid.Filler(popup), g.loop.widget, 'center', width, 'middle', 5)
