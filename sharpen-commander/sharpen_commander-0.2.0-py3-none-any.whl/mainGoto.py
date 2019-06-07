
import os
import urwid
import subprocess
import time

from multiprocessing import Pool

from .urwidHelper import *
from .tool import *
from .myutil import *

from .globalBase import *
from .mainRegList import DlgRegFolderSetting


def repoGetStatus(item):
	status  = dict(M=0, E=None)
	if not item["repo"]:
		return status

	try:
		ss = system("git status -s")
		if ss != "":
			status["M"] = 1
	except subprocess.CalledProcessError as e:
		status["E"] = str(e)

	return status

class mDlgGoto(cDialog):
	def __init__(self, onExit):
		super().__init__()

		self.onExit = onExit
		self.widgetFileList = mListBox(urwid.SimpleFocusListWalker(ur.btnListMakeTerminal([], None)))
		#self.widgetFileList.setFocusCb(lambda newFocus: self.onFileFocusChanged(newFocus))
		#self.widgetContent = ur.mListBox(urwid.SimpleListWalker(ur.makeTextList(["< Nothing to display >"])))
		#self.widgetContent.isViewContent = True

		self.header = ">> dc V%s - folder list - JK(move), E(modify), del" % g.version
		self.headerText = urwid.Text(self.header)

		#self.widgetFrame = urwid.Pile(
		#	[(15, urwid.AttrMap(self.widgetFileList, 'std')), ('pack', urwid.Divider('-')), self.widgetContent])
		self.widgetFrame = urwid.AttrMap(self.widgetFileList, 'std')
		self.edInput = editGen("$ ", "", lambda edit, text: self.onInputChanged(edit, text))
		self.mainWidget = urwid.Frame(self.widgetFrame, header=self.headerText, footer=self.edInput)

		self.itemList = None
		#self.cbFileSelect = lambda btn: self.onFileSelected(btn)

		self.mainWidget.set_focus("footer")

	def init(self):
		self.refreshFile()
		return True

	def onInputChanged(self, edit, text):
		last = ""
		if len(text) > 0:
			last = text[-1]
		if last in ["E", 'J', 'K', "H", 'D', 'Q', "P"]:
			def _cb(self, data):
				#data["dlg"].edInput.set_edit_text(data["text"][:-1])
				edit.set_edit_text(data["text"][:-1])

			g.loop.set_alarm_in(0.00001, _cb, dict(dlg=self, edit=edit, text=text))
			self.unhandled(last)

			#traceback.print_stack()
			return #text

		self.refreshFile(text)

	def onFileSelected(self, btn):
		if btn.attr is None:
			return

		pp = btn.attr["path"]
		os.chdir(pp)
		self.close()

	def refreshFile(self, filterStr=None):
		#oldPath = os.getcwd()
		filterStr = self.edInput.get_edit_text() if filterStr is None else filterStr
		if filterStr != "":
			lstPath = g.regFindItems(filterStr)
		else:
			lstPath = g.regList[:]

		lst = [("greenfg", x["path"], x) for x in lstPath]

		self.headerText.set_text("folder list - %d" % (len(lst)))
		idx = 0
		if self.widgetFileList.body.focus is not None:
			idx = self.widgetFileList.body.focus
		refreshBtnListMarkupTuple(lst, self.widgetFileList, lambda btn: self.onFileSelected(btn))
		if idx >= len(self.widgetFileList.body):
			idx = len(self.widgetFileList.body)-1
		self.widgetFileList.set_focus(idx)

	def unhandled(self, key):
		#print("key - %s" % key)
		if key == 'f4' or key == "Q" or key == "esc":
			self.close()
		elif key == "H" or key == "enter":
			self.onFileSelected(self.widgetFileList.body.get_focus()[0].original_widget)

		elif key == "J":  # we can't use ctrl+j since it's terminal key for enter replacement
			self.widgetFileList.focusNext()
		elif key == "K":
			self.widgetFileList.focusPrevious()

		elif key == "up":
			self.widgetFileList.focusPrevious()
		elif key == "down":
			self.widgetFileList.focusNext()

		elif key == "esc":
			self.edInput.set_edit_text("")
			self.refreshFile()

		elif key == "E":
			item = self.widgetFileList.focus
			self.doEdit(item.original_widget.attr)
			self.refreshFile()

		elif key == "D" or key == "delete":
			deleteItem = self.widgetFileList.focus.original_widget.attr
			g.regRemove(deleteItem["path"])
			self.refreshFile()

		elif key == "P":
			# 모든 repo udpate
			g.loop.stop()

			oldPath = os.getcwd()
			cnt = len(self.widgetFileList.body)
			for idx, item in enumerate(self.widgetFileList.body):
				attr = item.original_widget.attr
				pp = attr["path"]
				#os.chdir(pp)

				repoStatus = attr["repoStatus"]
				if attr["repo"]:
					if "M" in repoStatus:
						isModified = repoStatus["M"]
						try:
							print("[%d/%d] - %s" % (idx + 1, cnt, pp))
							if isModified:
								print("  git fetch")
								system("cd '%s'; git fetch" % pp)
								# 수정내역이 있으면 어차피 최신으로 못만든다.
							else:
								print("  git pull -r")

								# TODO: no has tracking branch
								system("cd '%s'; git pull -r" % pp)
						except subprocess.CalledProcessError as e:
							repoStatus["E"] = e

			os.chdir(oldPath)
			input("Enter to return...")
			g.loop.start()

	def doEdit(self, item):
		def onExit():
			g.doSetMain(self)

		dlg = DlgRegFolderSetting(onExit, item)
		g.doSetMain(dlg)