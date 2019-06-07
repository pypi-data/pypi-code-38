
import os
import urwid
import subprocess

from multiprocessing import Pool

from .urwidHelper import *
from .tool import *
from .myutil import *

from .globalBase import *


def _repoGetStatus(item):
	status = dict(M=0, E=None)
	if not item["repo"]:
		return status

	try:
		ss = system("git status -s")
		if ss != "":
			status["M"] = 1
	except subprocess.CalledProcessError as e:
		status["E"] = str(e)

	return status

# pool.map에 줄꺼라 local func이면 안된다.
def _genRepoItem(item):
	pp = item["path"]
	try:
		os.chdir(pp)
		item["repoStatus"] = _repoGetStatus(item)
	except FileNotFoundError:
		item["repoStatus"] = dict(E="Not found")

	item["title"] = getTitle(item)
	return item


def getTitle(item):
	ss = os.path.basename(item["path"])

	ss += "("
	for n in item["names"]:
		ss += n + ", "
	ss = ss[:-2]
	ss += ")"

	if item["repo"]:
		ss += " ==> ["

		branch = ""
		upstream = ""
		repoStatus = item["repoStatus"]
		isSame = True
		if repoStatus is None:
			ss += "Not found"
		else:
			if repoStatus["E"] is not None:
				ss += "err: " + str(repoStatus["E"])
			else:
				if repoStatus["M"] != 0:
					ss += "M"
					isSame = False

				try:
					out = tool.git.getBranchStatus()
					if out is None:
						ss += "no branch"
					else:
						branch, rev, upstream, remoteRev, ahead, behind = out
						#print(branch, rev, upstream, ahead, behind)
						if ahead:
							ss += "+%d" % ahead
							isSame = False
						if behind:
							ss += "-%d" % behind
							isSame = False
				except subprocess.CalledProcessError as e:
					ss += "Err - %s" % e

		ss += "]"
		ss += " %s -> %s" % (branch, upstream)
		repoStatus["same"] = isSame

	return ss

# 두칸씩 작은 오버레이로 띄우자
class DlgRegFolderSetting(cDialog):
	def __init__(self, onExit, item):
		super().__init__()
		self.onExit = onExit
		self.item = item

		self.header = ">> dc V%s - folder setting" % g.version
		self.headerText = urwid.Text(self.header)

		self.lbPath = urwid.Text("Path: %s" % item["path"])
		self.lbRepo = urwid.Text("Repo: ..")

		self.lbNames = urwid.Text("Names -----------")
		self.lbGroups = urwid.Text("Groups -----------")
		self.widgetListName = mListBox(urwid.SimpleFocusListWalker(btnListMakeTerminal([], None)))
		self.widgetListGroup = mListBox(urwid.SimpleFocusListWalker(btnListMakeTerminal(["< No group >"], None)))

		#urwid.SimpleFocusListWalker(ur.makeBtnListTerminal([], None)))
		self.lbHelp = urwid.Text("Insert: new name/group, Delete: remove name/group, R: toggle repo status")

		self.widgetFrame = urwid.LineBox(urwid.Pile(
			[("pack", self.headerText),
			("pack", self.lbPath),
			("pack", self.lbRepo),
            ("pack", self.lbNames), (8, self.widgetListName),
			('pack', urwid.Divider('-')),
            ("pack", self.lbGroups), (8, self.widgetListGroup),
			("pack", self.lbHelp)]))

		self.mainWidget = urwid.Overlay(urwid.Filler(self.widgetFrame), g.loop.widget, 'center', 80, 'middle', 30)

	def init(self):
		self.showInfo()
		return True

	def showInfo(self):
		self.lbRepo.set_text("Repo: %s" % ("O" if self.item["repo"] else "X"))

		names = self.item["names"]
		del self.widgetListName.body[:]
		self.widgetListName.body += btnListMakeTerminal(names, None)

		groups = self.item["groups"]
		if len(groups) > 0:
			del self.widgetListGroup.body[:]
			self.widgetListGroup.body += btnListMakeTerminal(groups, None)

		#self.widgetFrame.set_focus(self.widgetContent)

	def unhandled(self, key):
		if key == 'f4' or key == "q" or key == "esc":
			self.close()
		elif key == "r" or key == "R":
			self.item["repo"] = not self.item["repo"]

			ii = g.regFindByPath(self.item["path"])
			ii["repo"] = self.item["repo"]
			g.configSave()

			self.showInfo()

		elif key == "insert":
			focusWidget = self.widgetFrame.original_widget.get_focus()
			if focusWidget == self.widgetListName:
				def onOk(ss):
					self.item["names"].append(ss)
					g.configSave()
					self.showInfo()

				popupInput("Input new name", "", onOk, width=60)

			elif focusWidget == self.widgetListGroup:
				def onOk(ss):
					self.item["groups"].append(ss)
					g.configSave()
					self.showInfo()

				popupInput("Input new group", "", onOk, width=60)

		elif key == "delete":
			focusWidget = self.widgetFrame.original_widget.get_focus()
			if focusWidget == self.widgetListName:
				ss = self.widgetListName.focus.original_widget.get_label()
				def onOk():
					self.item["names"].remove(ss)
					g.configSave()
					self.showInfo()

				popupAsk("Remove Name", "[%s] will be deleted. Are you sure?" % ss, onOk)

			elif focusWidget == self.widgetListGroup:
				ss = self.widgetListGroup.focus.original_widget.get_label()
				def onOk():
					self.item["groups"].remove(ss)
					g.configSave()
					self.showInfo()

				popupAsk("Remove Group", "[%s] will be deleted. Are you sure?" % ss, onOk)


class DlgRegList(cDialog):
	def __init__(self, onExit):
		super().__init__()

		self.onExit = onExit
		self.widgetFileList = mListBox(urwid.SimpleFocusListWalker(btnListMakeTerminal([], None)))
		#self.widgetFileList.setFocusCb(lambda newFocus: self.onFileFocusChanged(newFocus))
		self.widgetContent = mListBox(urwid.SimpleListWalker(textListMakeTerminal(["< Nothing to display >"])))
		#self.widgetContent.isViewContent = True

		self.header = ">> dc repo list - J/K(move) E(modify) P(pull all) del Q/esc(quit)"
		self.headerText = urwid.Text(self.header)

		#self.widgetFrame = urwid.Pile(
		#	[(15, urwid.AttrMap(self.widgetFileList, 'std')), ('pack', urwid.Divider('-')), self.widgetContent])
		self.widgetFrame = urwid.AttrMap(self.widgetFileList, 'std')
		self.edInput = editGen("$ ", "", lambda edit, text: self.onInputChanged(edit, text))
		self.mainWidget = urwid.Frame(self.widgetFrame, header=self.headerText, footer=self.edInput)

		self.itemList = None
		#self.cbFileSelect = lambda btn: self.onFileSelected(btn)

		self.mainWidget.set_focus("footer")

		#self.content = ""
		#self.selectFileName = ""

	def init(self):
		self.refreshFile()
		return True

	def onInputChanged(self, edit, text):
		last = ""
		if len(text) > 0:
			last = text[-1]
		if last in ["E", 'J', 'K', "H", 'D', 'Q', "P"]:
			def _cb(self, data):
				data["dlg"].edInput.set_edit_text(data["text"][:-1])

			g.loop.set_alarm_in(0.00001, _cb, dict(dlg=self, text=text))
			self.unhandled(last)

			#traceback.print_stack()
			return #text

		self.refreshList(text)

	def onFileSelected(self, btn):
		widget = btn
		pp = widget.attr["path"]
		os.chdir(pp)
		self.close()

	def refreshFile(self):
		oldPath = os.getcwd()

		# title, item
		# itemList = []
		# for x in g.regList:
		# 	# todo: multi thread
		# 	itemList.append(genRepoItem(x))


		pool = Pool(10)
		lst = filter(lambda x: x["repo"], g.regList)
		self.itemList = pool.map(_genRepoItem, lst)
		#itemList = [ (item["title"], item) for item in itemList]

		#itemList = [ (getTitle(x), x) for x in g.regList ]
		os.chdir(oldPath)

		# mstd, title, item
		def _gen(item):
			mstd = "std"
			if "repo" in item and item["repo"]:
				if item["repoStatus"]["same"]:
					mstd = "grayfg"
				else:
					mstd = "greenfg"

			return mstd, item["title"], item

		# status
		self.itemList = list(map(_gen, self.itemList))
		self.refreshList("")

	def refreshList(self, filterStr):

		# TODO: names?
		def _filterList(item):
			if filterStr == "":  return True

			for name in item[2]["names"]:
				if filterStr.lower() in name.lower():
					return True

		itemList = list(filter(_filterList, self.itemList))

		#self.headerText.set_text("%s - %s%s - %d" % (self.title, pp, status, len(itemList)))
		idx = 0
		if self.widgetFileList.body.focus is not None:
			idx = self.widgetFileList.body.focus
		refreshBtnListMarkupTuple(itemList, self.widgetFileList, lambda btn: self.onFileSelected(btn))
		if idx >= len(self.widgetFileList.body):
			idx = len(self.widgetFileList.body)-1
		self.widgetFileList.set_focus(idx)
		#del self.widgetFileList.body[:]
		#self.widgetFileList.itemCount = len(lst2)
		#self.widgetFileList.body += ur.makeBtnListTerminal( , None)

	def unhandled(self, key):
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
