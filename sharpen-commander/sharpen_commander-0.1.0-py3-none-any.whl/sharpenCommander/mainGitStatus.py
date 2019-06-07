import os
import sys

import urwid
import subprocess
from multiprocessing import Pool


from globalBase import *

import urwidHelper as ur
import myutil

import tool
from tool import git, system, systemSafe, systemRet, programPath


"""
itemList = list of (terminal, attr)
"""
def refreshBtnListTerminal(terimalItemList, listBox, onClick):
	del listBox.body[:]
	listBox.itemCount = len(terimalItemList)
	if listBox.itemCount == 0:
		terimalItemList = [("< Nothing > ", None)]

	listBox.body += ur.btnListMakeTerminal(terimalItemList, onClick)


class DlgGitCommit(ur.cDialog):
	themes = [("greenfg", "greenfg_f"), ("std", "std_f")]

	def __init__(self, onExit):
		super().__init__()

		self.selectFileName = ""

		self.onExit = onExit
		self.edInput = ur.editGen("Input commit message => ", "", lambda edit, text: self.onMsgChanged(edit, text))
		self.widgetFileList = ur.mListBox \
			(urwid.SimpleFocusListWalker(ur.btnListMakeTerminal([("< No files >", None)], None)))
		self.widgetContent = ur.mListBox(urwid.SimpleListWalker(ur.textListMakeTerminal(["< Nothing to display >"])))

		self.headerText = urwid.Text(">> Commit - f9/f10(Prev/Next file) f4(cancel operation)")
		self.widgetFrame = urwid.Pile \
			([("pack", self.edInput), (8, urwid.AttrMap(self.widgetFileList, 'std')), ('pack', urwid.Divider('-')), self.widgetContent])
		self.mainWidget = urwid.Frame(self.widgetFrame, header=self.headerText)

		self.refreshFileList()
		self.widgetFrame.set_focus(self.edInput)

	def onMsgChanged(self, edit, text):
		pass

	def _applyFileColorTheme(self, widget, isFocus=0):
		theme = self.themes[0 if widget.original_widget.attr == "s" else 1]
		widget.original_widget.set_label((theme[isFocus], widget.original_widget.origTxt))

	def onFileSelected(self, btn):
		# why btn.get_label() is impossible?
		label = btn.original_widget.get_label()
		self.selectFileName = btn.original_widget.get_label()
		# g.headerText.set_text("file - " + label)

		# display
		btnType = btn.original_widget.attr
		pp = os.path.join(g.relRoot, self.selectFileName)
		try:
			ss = system("git diff --color %s \"%s\"" % ("" if btnType == "c" else "--staged", pp))
		except subprocess.CalledProcessError as e:
			ss = "failed to print diff for %s\n  %s" % (pp, e)

		ss = ss.replace("\t", "    ")

		del self.widgetContent.body[:]
		self.widgetContent.body += ur.textListMakeTerminal(ss.split("\n"))
		self.widgetFrame.set_focus(self.widgetContent)

	def refreshFileContentCur(self):
		self.onFileSelected(self.widgetFileList.focus)

	def refreshFileList(self):
		del self.widgetFileList.body[:]

		# staged file list
		fileList = system("git diff --name-only --cached")
		itemList = [ (self.themes[0][0], x, "s") for x in fileList.split("\n") if x.strip() != "" ]
		self.widgetFileList.body += ur.btnListMakeMarkup(itemList, lambda btn: self.onFileSelected(btn))

		# general file list
		fileList = system("git diff --name-only")
		itemList = [ (self.themes[1][0], x, "c") for x in fileList.split("\n") if x.strip() != ""  ]
		self.widgetFileList.body += ur.btnListMakeMarkup(itemList, lambda btn: self.onFileSelected(btn), False)

		# for widget in self.widgetFileList.body:
		#	self._applyFileColorTheme(widget, 0)

		if len(self.widgetFileList.body) == 0:
			self.widgetFileList.body += ur.btnListMakeTerminal([("< Nothing >", None)], None, False)

		# self.onFileFocusChanged(self.widgetFileList.focus_position)
		self.onFileSelected(self.widgetFileList.focus)	# auto display

	def inputFilter(self, keys, raw):
		if g.loop.widget != g.dialog.mainWidget:
			return keys

		if ur.filterKey(keys, "down"):
			self.widgetContent.scrollDown()

		if ur.filterKey(keys, "up"):
			self.widgetContent.scrollUp()

		return keys

	def unhandled(self, key):
		if key == "q" or key == "Q" or key == "f4":
			self.close()
		elif key == 'k':
			self.widgetContent.scrollUp()
		elif key == 'j':
			self.widgetContent.scrollDown()
		elif key == "left" or key == "[" or key == "f9" or key == "h":
			self.widgetFileList.focusPrevious()
			self.refreshFileContentCur()

			if key == "f9":
				self.widgetFrame.set_focus(self.edInput)

		elif key == "right" or key == "]" or key == "f10" or key == "l":
			self.widgetFileList.focusNext()
			self.refreshFileContentCur()

			if key == "f10":
				self.widgetFrame.set_focus(self.edInput)

		elif key == "A":
			def onAdd():
				system("git add \"%s\"" % fname)
				self.refreshFileList()

			def onPrompt():
				g.loop.stop()
				systemRet("git add -p \"%s\"" % fname)
				g.loop.start()
				self.refreshFileList()

			btn = self.widgetFileList.focus
			fname = myutil.gitFileBtnName(btn)
			ur.popupAsk3("Git add", "Do you want to add a file[%s]?" % fname, "Add", "Prompt", "Cancel", onAdd, onPrompt)

		elif key == "R":
			def onReset():
				system("git reset \"%s\"" % fname)
				self.refreshFileList()

			btn = self.widgetFileList.focus
			fname = myutil.gitFileBtnName(btn)
			ur.popupAsk("Git reset", "Do you want to reset a file[%s]?" % fname, onReset)

		elif key == "D":
			def onDrop():
				system("git checkout -- \"%s\"" % fname)
				self.refreshFileList()

			btn = self.widgetFileList.focus
			fname = myutil.gitFileBtnName(btn)
			ur.popupAsk("Git reset(f)", "Do you want to drop file[%s]s modification?" % fname, onDrop)

		elif key == "E":
			btn = self.widgetFileList.focus
			fname = myutil.gitFileBtnName(btn)

			g.loop.stop()
			systemRet("vim %s" % fname)
			g.loop.start()

			self.refreshFileContentCur()

		elif key == "esc":
			self.widgetFrame.set_focus(self.edInput)

		elif key == "ctrl a":
			# commit all
			def onCommit():
				tt = self.edInput.get_edit_text()
				ss = system("git commit -a -m \"%s\"" % tt[:-1])
				self.close()

			ur.popupAsk("Git Commit", "Do you want to commit all modification?", onCommit)

		elif key == "enter":
			# commit
			tt = self.edInput.get_edit_text()
			ss = system("git commit -m \"%s\"" % tt)
			# print(ss)
			self.close()

		elif key == "C":
			def onCommit():
				g.loop.stop()
				systemRet("git commit -a")
				g.loop.start()
				self.refreshFileList()

			ur.popupAsk("Git commit(all)", "Do you want to commit all content?", onCommit)

		#elif key == "h":
		#	ur.popupMsg("Dc help", "Felix Felix Felix Felix\nFelix Felix")



class DlgGitStatus(ur.cDialog):
	def __init__(self, onExit=None):
		super().__init__()

		self.onExit = onExit
		self.selectFileName = ""

		self.widgetFileList = ur.mListBox(
			urwid.SimpleFocusListWalker(ur.btnListMakeTerminal([("< No files >", None)], None)))
		self.widgetContent = ur.mListBox(urwid.SimpleListWalker(ur.textListMakeTerminal(["< Nothing to display >"])))

		self.headerText = urwid.Text(
			">> sc stage - q/F4(Quit) J/K,h/l(Prev/Next file) j/k(scroll) A(Add) P(Prompt) R(Reset) D(drop) C(Commit) I(Ignore)")
		self.widgetFrame = urwid.Pile(
			[(8, urwid.AttrMap(self.widgetFileList, 'std')), ('pack', urwid.Divider('-')), self.widgetContent])
		self.mainWidget = urwid.Frame(self.widgetFrame, header=self.headerText)

		try:
			g.gitRoot = system("git rev-parse --show-toplevel")
		except subprocess.CalledProcessError:
			print("Current folder is no git repo")
			raise urwid.ExitMainLoop

		g.curPath = os.getcwd()
		g.relRoot = "./"
		if g.gitRoot != g.curPath:
			g.relRoot = os.path.relpath(g.gitRoot, g.curPath)

	def init(self):
		if not self.refreshFileList():
			print("No modified or untracked files")
			return False

		return True

	def onFileSelected(self, btn):
		# why btn.get_label() is impossible?
		label = btn.original_widget.get_label()
		# self.selectFileName = gitFileBtnName(btn)
		self.selectFileName = myutil.gitFileLastName(btn)
		# g.headerText.set_text("file - " + label)

		# display
		if label == "< Nothing >":
			ss = label
		elif label.startswith("?? "):
			if os.path.isdir(self.selectFileName):
				ss = "%s is folder" % self.selectFileName
			else:
				try:
					with open(self.selectFileName, "r", encoding="UTF-8") as fp:
						ss = fp.read()
				except UnicodeDecodeError:
					# ur.popupMsg("Encoding", "Encoding error[%s]" % self.selectFileName);
					ss = "No utf8 file[size:%d]" % os.path.getsize(self.selectFileName)

		else:
			try:
				ss = system("git diff --color \"%s\"" % self.selectFileName)
			except subprocess.CalledProcessError as e:
				ss = "failed to print diff for %s\n  %s" % (self.selectFileName, e)

		ss = ss.replace("\t", "    ")

		del self.widgetContent.body[:]
		self.widgetContent.body += ur.textListMakeTerminal(ss.splitlines())
		self.widgetFrame.set_focus(self.widgetContent)

	def refreshFileContentCur(self):
		self.onFileSelected(self.widgetFileList.focus)

	def refreshFileList(self, focusMove=0):
		itemList = git.statusFileList()
		if len(itemList) <= 0:
			return False

		focusIdx = self.widgetFileList.focus_position
		refreshBtnListTerminal(itemList, self.widgetFileList, lambda btn: self.onFileSelected(btn))
		size = len(self.widgetFileList.body)

		focusIdx += focusMove
		if focusIdx >= size:
			focusIdx = size - 1
		# self.widgetFileList.focus_position = focusIdx
		self.widgetFileList.set_focus(focusIdx)
		self.onFileSelected(self.widgetFileList.focus)  # auto display
		return True

	def gitGetStagedCount(self):
		cnt = 0
		for item in self.widgetFileList.body:
			if "s" in item.original_widget.attr:  # greenfg
				cnt += 1

		return cnt

	def inputFilter(self, keys, raw):
		if g.loop.widget != g.dialog.mainWidget:
			return keys

		if ur.filterKey(keys, "down"):
			self.widgetContent.scrollDown()

		if ur.filterKey(keys, "up"):
			self.widgetContent.scrollUp()

		return keys

	def unhandled(self, key):
		if key == 'f4' or key == "q":
			self.close()
		elif key == 'k':
			self.widgetContent.scrollUp()
		elif key == 'j':
			self.widgetContent.scrollDown()
		elif key == "left" or key == "[" or key == "f9" or key == "h" or key == "K":
			self.widgetFileList.focusPrevious()
			self.refreshFileContentCur()
		elif key == "right" or key == "]" or key == "f10" or key == "l" or key == "J":
			self.widgetFileList.focusNext()
			self.refreshFileContentCur()

		elif key == "A":
			btn = self.widgetFileList.focus
			# fname = gitFileBtnName(btn)
			fname = myutil.gitFileLastName(btn)
			system("git add \"%s\"" % fname)
			self.refreshFileList(1)

		elif key == "P":
			def onPrompt():
				g.loop.stop()
				systemRet("git add -p \"%s\"" % fname)
				g.loop.start()
				self.refreshFileList()

			btn = self.widgetFileList.focus
			fname = myutil.gitFileBtnName(btn)
			ur.popupAsk("Git add", "Do you want to add a file via prompt[%s]?" % fname, onPrompt)

		elif key == "R":
			btn = self.widgetFileList.focus
			fname = myutil.gitFileBtnName(btn)
			system("git reset \"%s\"" % fname)
			self.refreshFileList()

		elif key == "D":
			def onDrop():
				system("git checkout -- \"%s\"" % fname)
				self.refreshFileList()

			def onDelete():
				os.remove(fname)
				self.refreshFileList()

			btn = self.widgetFileList.focus
			fname = myutil.gitFileBtnName(btn)
			if myutil.gitFileBtnType(btn) == "??":
				ur.popupAsk("Git reset(f)", "Do you want to delete file[%s]?" % fname, onDelete)
			else:
				ur.popupAsk("Git reset(f)", "Do you want to drop file[%s]s modification?" % fname, onDrop)

		elif key == "E":
			btn = self.widgetFileList.focus
			fname = myutil.gitFileBtnName(btn)

			g.loop.stop()
			systemRet("vim %s" % fname)
			g.loop.start()

			self.refreshFileContentCur()

		elif key == "c_old":
			def onCommit():
				g.loop.stop()
				systemRet("git commit")
				g.loop.start()
				self.refreshFileList()

			ur.popupAsk("Git commit", "Do you want to commit?", onCommit)

		elif key == "C":
			def onExit():
				if not self.refreshFileList():
					if getattr(self, "onExit") and self.onExit is not None:
						self.close()
						return
					else:
						g.loop.stop()
						print("No modified or untracked files")
						sys.exit(0)

				g.doSetMain(self)

			# check staged data
			n = self.gitGetStagedCount()
			if n == 0:
				ur.popupMsg("Alert", "There is no staged file to commit")
				return

			dlg = DlgGitCommit(onExit)
			g.doSetMain(dlg)

		elif key == "h":
			ur.popupMsg("Dc help", "Felix Felix Felix Felix\nFelix Felix")
