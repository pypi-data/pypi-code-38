
import os
import urwid

from globalBase import *

import urwidHelper as ur
import tool

#import dc
import myutil


class DlgFind(ur.cDialog):
	def __init__(self, onExit=None):
		super().__init__()

		self.onExit = onExit
		self.widgetFileList = ur.mListBox(urwid.SimpleFocusListWalker(ur.btnListMakeTerminal([], None)))
		self.widgetFileList.setFocusCb(lambda newFocus: self.onFileFocusChanged(newFocus))
		self.widgetContent = ur.mListBox(urwid.SimpleListWalker(ur.textListMakeTerminal(["< Nothing to display >"])))
		self.widgetContent.isViewContent = True

		self.header = ">> dc find - q/F4(Quit) </>,h/l(Prev/Next file) Enter(goto) E(edit)..."
		self.headerText = urwid.Text(self.header)
		self.widgetFrame = urwid.Pile(
			[(15, urwid.AttrMap(self.widgetFileList, 'std')), ('pack', urwid.Divider('-')), self.widgetContent])
		self.mainWidget = urwid.Frame(self.widgetFrame, header=self.headerText)

		self.cbFileSelect = lambda btn: self.onFileSelected(btn)
		self.content = ""
		self.selectFileName = ""

		self.lstFile = []

	def onFileFocusChanged(self, newFocus):
		# old widget
		# widget = self.widgetFileList.focus
		# markup = ("std", widget.base_widget.origTxt)
		# widget.base_widget.set_label(markup)

		# widget = self.widgetFileList.body[newFocus]
		# markup = ("std_f", widget.base_widget.origTxt)
		# widget.base_widget.set_label(markup)
		widget = self.widgetFileList.focus
		widget.original_widget.set_label(widget.base_widget.markup[0])

		widget = self.widgetFileList.body[newFocus]
		widget.base_widget.set_label(widget.base_widget.markup[1])

		self.widgetFileList.set_focus_valign("middle")
		self.selectFileName = myutil.fileBtnName(widget)

		try:
			with open(self.selectFileName, "r", encoding="UTF-8") as fp:
				ss = fp.read()
		except UnicodeDecodeError:
			ss = "No utf8 file[size:%d]" % os.path.getsize(self.selectFileName)

		ss = ss.replace("\t", "    ")

		del self.widgetContent.body[:]
		self.widgetContent.body += ur.textListMakeTerminal(ss.splitlines())
		self.widgetFrame.set_focus(self.widgetContent)
		return True

	def onFileSelected(self, btn):
		if btn.original_widget.attr is None:
			self.close()
			return

		self.selectFileName = myutil.gitFileBtnName(btn)
		itemPath = os.path.join(os.getcwd(), self.selectFileName)
		pp = os.path.dirname(itemPath)
		os.chdir(pp)
		g.savePath(pp)
		g.targetFile = os.path.basename(itemPath)
		#raise urwid.ExitMainLoop()
		self.close()

	def inputFilter(self, keys, raw):
		if ur.filterKey(keys, "down"):
			self.widgetContent.scrollDown()

		if ur.filterKey(keys, "up"):
			self.widgetContent.scrollUp()

		if ur.filterKey(keys, "enter"):
			self.onFileSelected(self.widgetFileList.focus)

		return keys

	def recvData(self, data):
		if data is None:
			self.headerText.set_text(self.header + "!!!")
			if len(self.widgetFileList.body) == 0:
				self.widgetFileList.body += ur.btnListMakeTerminal(["< No result >"], None)
			return

		ss = data.decode("UTF-8")
		self.content += ss
		pt = self.content.rfind("\n")
		if pt == -1:
			return True

		ss = self.content[:pt]
		self.content = self.content[pt:]

		for line in ss.splitlines():
			line = line.strip()
			if line == "":
				continue

			self.lstFile.append(line)

		self.fileShow()

		return True

	def fileShow(self):
		del self.widgetFileList.body[:]

		for line in self.lstFile:
			# TODO: filter

			# markup = ur.terminal2markup(line, 0)
			# markupF = ur.terminal2markup(line, 1)
			markup = ("std", line)
			markupF = ('std_f', line)

			btn = ur.btnGen(markup, markupF, self.cbFileSelect, len(self.widgetFileList.body) == 0)
			self.widgetFileList.body.append(btn)
			if len(self.widgetFileList.body) == 1:
				self.onFileFocusChanged(0)

	def unhandled(self, key):
		if key == 'f4' or key == "q":
			#raise urwid.ExitMainLoop()
			self.close()

		elif key == 'left' or key == "[" or key == "h":
			self.widgetFileList.focusPrevious()
		elif key == 'right' or key == "]" or key == "l":
			self.widgetFileList.focusNext()

		elif key == "H":
			for i in range(10):
				self.widgetFileList.focusPrevious()
		elif key == "L":
			for i in range(10):
				self.widgetFileList.focusNext()

		elif key == "k":
			self.widgetContent.scrollUp()
		elif key == "j":
			self.widgetContent.scrollDown()

		elif key == "K":
			for i in range(15):
				self.widgetContent.scrollUp()
		elif key == "J":
			for i in range(15):
				self.widgetContent.scrollDown()

		elif key == "e" or key == "E":
			btn = self.widgetFileList.focus
			fname = myutil.gitFileBtnName(btn)

			g.loop.stop()
			tool.systemRet("%s %s" % (g.editApp, fname))
			g.loop.start()

		elif key == "H":
			ur.popupMsg("Dc help", "Felix Felix Felix Felix\nFelix Felix")
