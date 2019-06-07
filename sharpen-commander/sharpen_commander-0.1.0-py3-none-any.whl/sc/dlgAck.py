
import os
import urwid

from globalBase import *
import urwidHelper as ur

import tool


class AckFile:
	def __init__(self, fnameTerminal):
		self.fname = ur.termianl2plainText(fnameTerminal)
		# self.fnameMarkup = Urwid.terminal2markup(fnameTerminal, 0)
		# self.fnameOrig = fnameTerminal

		self.lstLine = []

	# return title(cnt) in color
	def getTitleMarkup(self, focus=False):
		themeTitle = "greenfg" if not focus else "greenfg_f"
		themeCount = "std" if not focus else "std_f"
		return [(themeTitle, self.fname), (themeCount, "(%d)" % len(self.lstLine))]


class DlgAck(ur.cDialog):
	def __init__(self, onExit=None):
		super().__init__()

		self.onExit = onExit
		self.widgetFileList = ur.mListBox(urwid.SimpleFocusListWalker(ur.btnListMakeTerminal([], None)))
		self.widgetFileList.setFocusCb(lambda newFocus: self.onFileFocusChanged(newFocus))

		#self.widgetContent = ur.mListBox(urwid.SimpleListWalker(ur.textListMakeTerminal([])))
		self.widgetContent = ur.mListBox(urwid.SimpleFocusListWalker(ur.btnListMakeTerminal([], None)))
		self.widgetContent.setFocusCb(lambda newFocus: self.onLineFocusChanged(newFocus))

		self.header = ">> dc V%s - ack-grep - q/F4(Quit),<-,->/[,](Prev/Next file),Enter(goto),E(edit)..." % g.version
		self.headerText = urwid.Text(self.header)
		self.widgetFrame = urwid.Pile(
			[(15, urwid.AttrMap(self.widgetFileList, 'std')), ('pack', urwid.Divider('-')), self.widgetContent])
		self.mainWidget = urwid.Frame(self.widgetFrame, header=self.headerText)

		self.buf = ""
		self.lstContent = []

	def btnUpdate(self, btn, focus):
		btn.original_widget.set_label(btn.afile.getTitleMarkup(focus))
		return btn

	def onFileFocusChanged(self, newFocus):
		self.btnUpdate(self.widgetFileList.focus, False)
		newBtn = self.btnUpdate(self.widgetFileList.body[newFocus], True)

		self.widgetContent.focus_position = newBtn.afile.position
		return False

	def onLineFocusChanged(self, newFocus):
		btn = self.widgetContent.focus
		btn.original_widget.set_label(btn.markup[0])
		btn = self.widgetContent.body[newFocus]
		btn.original_widget.set_label(btn.markup[1])

		#self.btnUpdate(self.widgetContent.focus, False)
		#newBtn = self.btnUpdate(self.widgetContent.body[newFocus], True)

		#self.widgetContent.focus_position = newBtn.afile.position
		return False

	def onFileSelected(self, btn):
		if not hasattr(btn, "afile"):  # no result
			self.close()
			return

		itemPath = os.path.join(os.getcwd(), btn.afile.fname)
		pp = os.path.dirname(itemPath)
		os.chdir(pp)
		g.savePath(pp)
		g.targetFile = os.path.basename(itemPath)
		#raise urwid.ExitMainLoop()
		self.close()

	def onLineSelected(self, btn):
		pp = os.path.dirname(os.path.join(os.getcwd(), btn.afile.fname))
		g.savePath(pp)
		raise urwid.ExitMainLoop()

	def inputFilter(self, keys, raw):
		if g.loop.widget != g.dialog.mainWidget:
			return keys

		if ur.filterKey(keys, "down"):
			#self.widgetContent.scrollDown()
			self.widgetContent.focusNext()

		if ur.filterKey(keys, "up"):
			#self.widgetContent.scrollUp()
			self.widgetContent.focusPrevious()

		if ur.filterKey(keys, "enter"):
			self.onFileSelected(self.widgetFileList.focus)

		return keys

	def recvData(self, data):
		if data is None:
			self.headerText.set_text(self.header + "!!!")
			if len(self.widgetFileList.body) == 0:
				self.widgetFileList.body += ur.btnListMakeTerminal(["< No result >"], None)
			return

		ss = data.decode("UTF-8", "ignore")
		self.buf += ss
		pt = self.buf.rfind("\n")
		if pt == -1:
			return True

		ss = self.buf[:pt]
		self.buf = self.buf[pt:]

		#g.loop.stop()

		for line in ss.splitlines():
			line = line.strip()

			if line != "" and ":" not in line:  # file name
				# new file
				afile = AckFile(line)
				self.lstContent.append(afile)

				isFirst = len(self.widgetFileList.body) == 0
				btn = ur.btnGenMarkup(afile.getTitleMarkup(isFirst), lambda bb: self.onFileSelected(bb))
				btn.afile = afile
				afile.btn = btn
				afile.position = len(self.widgetContent.body)
				self.widgetFileList.body.append(btn)

				#txt = urwid.Text(afile.getTitleMarkup(isFirst))
				markup = (afile.getTitleMarkup(False), afile.getTitleMarkup(True))
				btn2 = ur.btnGenMarkup(markup[1] if isFirst else markup[0], lambda bb: self.onLineSelected(bb))
				btn2.isFile = True
				btn2.afile = afile
				btn2.markup = markup
				self.widgetContent.body.append(btn2)

			else:
				afile = self.lstContent[len(self.lstContent) - 1]
				line = line.replace("\t", "    ")
				afile.lstLine.append(line)

				# update content
				#txt = ur.textGenTerminal(line)
				markup = (ur.terminal2markup(line, 0), ("std_f", ur.termianl2plainText(line)))
				btn2 = ur.btnGenMarkup(markup[0], lambda bb: self.onLineSelected(bb))
				btn2.isFile = False
				btn2.afile = afile
				btn2.markup = markup
				self.widgetContent.body.append(btn2)

				# we need it???
				#self.btnUpdate(afile.btn, afile.position == 0)

		return True

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
			#self.widgetContent.scrollUp()
			item, pos = self.widgetContent.focusPrevious()
			if item.original_widget.get_label() == "":
				self.widgetContent.focusPrevious()

		elif key == "j":
			#self.widgetContent.scrollDown()
			item, pos = self.widgetContent.focusNext()
			if item.original_widget.get_label() == "":
				_, pos = self.widgetContent.focusNext()

		elif key == "e" or key == "E":
			btn = self.widgetFileList.focus
			g.loop.stop()
			tool.systemRet("%s %s" % (g.editApp, btn.afile.fname))
			g.loop.start()

		elif key == "h":
			ur.popupMsg("Dc help", "Felix Felix Felix Felix\nFelix Felix")

