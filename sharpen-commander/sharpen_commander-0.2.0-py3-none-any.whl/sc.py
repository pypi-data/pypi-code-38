# coding: utf-8
#!/usr/bin/env python3

import subprocess

import os
import sys
import select
import re
import stat
import json
import traceback
import shutil

from enum import Enum
from os.path import expanduser


import urwid
import urwid.raw_display
import urwid.web_display
from urwid.signals import connect_signal

from distutils.spawn import find_executable

from .globalBase import *
from .tool import * #git, system, systemSafe, systemRet, programPath
from .urwidHelper import *
from .myutil import *

from .dlgAck import DlgAck
from .dlgFind import DlgFind
from .mainGitStatus import DlgGitStatus
from .mainRegList import DlgRegList
from .mainGoto import mDlgGoto



'''
dc - devCmd

# install setting

1. append some lines to .bashrc as follows

  DEV_CMD_PATH=~/devCmdTool
  . DEV_CMD_PATH/bash-script.sh

2. write devPath.py file on ~/.devcmd

  G_PATH_LIST = [
        dict(name="ipc", path="~/ipc-linux")
  ]


# usage

1. push command
 1) print git status
 2) input target branch name
 3) git push origin master:TARGET_BRANCH
 
 
'''


Color = Enum('color', 'blue red')


def osStat(pp):
	try:
		return os.stat(pp)
	except Exception:
		return None

class Ansi:
	redBold = "\033[1;31m"
	red = "\033[0;31m"
	blueBold = "\033[1;34m"
	blue = "\033[0;34m"
	clear = "\033[0m"

class MyProgram(Program):
	def __init__(self):
		super().__init__("1.1.0", programPath("dc.log"))
		self.regList = []
		self.configPath = ""    # ~/.devcmd/path.py

		self.isPullRebase = True
		self.isPushRebase = True

		self.grepApp = "grep" # "ack"
		self.editApp = "vi"

		self.targetFile = None

		self.dialog = None 		# main dialog
		self.loop = None

	def init(self):
		pp = os.path.expanduser("~/.synapcmd")
		if not os.path.isdir(pp):
			print("No .synapcmd folder. generate it...")
			os.mkdir(pp)

		self.configPath = os.path.join(pp, "cfg.json")

		cfgPath = os.path.join(pp, "path.json")
		if os.path.exists(cfgPath):
			print("renaming old path.json file to cfg.json...")
			os.rename(cfgPath, self.configPath)

		self.configLoad()

	def configLoad(self):
		if not os.path.isfile(self.configPath):
			print("No cfg.json file. generating it...")
			print("%d" % 1 if os.path.exists(self.configPath) else 0)
			self.regList = []
			self.configSave()
			return

		#sys.path.append(pp)
		#m = __import__("path")
		#self.lstPath = [ item for item in m.pathList if len(item["names"]) > 0 ]
		with open(self.configPath, "r") as fp:
			obj = json.load(fp)
			self.regList = obj["path"]
			if "isPullRebase" in obj:
				self.isPullRebase = obj["isPullRebase"]
			if "isPushRebase" in obj:
				self.isPushRebase = obj["isPushRebase"]

			if "grepApp" in obj:
				self.grepApp = obj["grepApp"]
			else:
				if shutil.which("ag") is not None:
					self.grepApp = "ag"
				elif shutil.which("ack") is not None:
						self.grepApp = "ack"
				else:
					self.grepApp = "grep"

			if "editApp" in obj:
				self.editApp = obj["editApp"]
			else:
				if shutil.which("code") is not None:
					self.editApp = "code"
				else:
					self.editApp = "vi"

			if "debugPrintSystem" in obj:
				gCfg.debugPrintSystem = obj["debugPrintSystem"]

		for item in self.regList:
			item["path"] = os.path.expanduser(item["path"])
			name = item["names"]
			if type(name) is str:
				item["names"] = [name]

			if "groups" not in item:
				item["groups"] = []

	def configSave(self):
		obj = dict()
		obj["path"] = self.regList
		obj["isPullRebase"] = self.isPullRebase
		obj["isPushRebase"] = self.isPushRebase
		obj["grepApp"] = self.grepApp
		obj["editApp"] = self.editApp

		with open(self.configPath, "w") as fp:
			json.dump(obj, fp, indent=4)  #, separators=(',',':'))

	def savePath(self, pp):
		with open("/tmp/cmdDevpath", "wb") as f:
			f.write(os.path.expanduser(pp).encode())

	def regAdd(self, pp):
		oldPath = os.getcwd()
		os.chdir(pp)
		ss, code = systemSafe("git rev-parse --is-inside-work-tree")
		isGitRepo = False
		if code == 0:
			isGitRepo = True if ss == "true" else False

		os.chdir(oldPath)

		name = os.path.basename(pp)
		g.regList.append(dict(names=[name], path=pp, groups=[], repo=isGitRepo))
		g.configSave()
		popupMsg("Regiter", "The path is registerted successfully\n%s" % pp, 60)

	def regRemove(self, pp):
		item = g.regFindByPath(pp)
		if item is None:
			popupMsg("Unregister", "The path is not registered\n%s" % pp, 60)
			return

		def onOk():
			g.regList.remove(item)
			g.configSave()
			#self.fileRefresh()
			popupMsg("Unregister", "The path is unregisterted successfully\n%s" % pp, 60)

		popupAsk("Unregister", "Do you want to unregister the folder?\n%s" % pp, onOk)

	def regFindByName(self, target):
		for pp in self.regList:
			names = pp["names"]

			if target.lower() in map(str.lower, names):
				return pp

		raise ErrFailure("No that target[%s]" % target)

	def regFindByPath(self, pp):
		return next((x for x in g.regList if x["path"] == pp), None)

	# path list that includes sub string
	def regFindItems(self, sub):
		sub = sub.lower()
		#lst = []
		#for pp in self.regList:
		#	if self.matchItem(pp, sub):
		#		lst.append(pp)
		lst = list(filter(lambda x: self.matchItem(x, sub), self.regList))
		return lst

	@staticmethod
	def matchItem(item, sub):
		names = item["names"]
		names2 = map(str.lower, names)

		hasList = list(filter(lambda s: sub in s, names2))
		return len(hasList)

	def cd(self, target):
		if target == "~":
			self.savePath(target)
			return
	
		item = self.regFindByName(target)
		self.savePath(item["path"])

	def regListPrint(self):
		for pp in self.regList:
			print(pp)

	def printCommitLogForPush(self, currentBranch, remoteBranch):
		# commit log to push
		gap = git.commitGap(currentBranch, remoteBranch)
		if gap == 0:
			git.printStatus()
			raise ErrFailure("There is no commit to push")

		print("There are %d commits to push" % gap)
		ss = git.commitLogBetween(currentBranch, remoteBranch)
		print(ss)

	def gitPush(self):
		print("\nCurrent file status...")
		git.printStatus()

		currentBranch = git.getCurrentBranch()
		remoteBranch = git.getTrackingBranch()
		if remoteBranch is None:
			print("currentBranch:%s DONT have tracking branch")
			# todo: print latest 10 commits

		else:
			print("currentBranch:%s, remote:%s" % (currentBranch, remoteBranch))

			self.printCommitLogForPush(currentBranch, remoteBranch)

			if self.isPushRebase:
				# check if fast-forward of remoteBranch
				rev1 = git.rev(currentBranch)
				rev2 = git.rev("remotes/"+remoteBranch)
				revCommon = git.commonParentRev(currentBranch, remoteBranch)
				if revCommon.startswith(rev2):
					print("local branch is good situation")
				else:
					diffList = git.checkRebaseable(currentBranch, remoteBranch)
					if len(diffList) == 0:
						while True:
							hr = input("\n\n*** You can rebase local to remoteBranch. want? Y/n: ").lower()
							if hr == "":
								hr = 'y'

							if hr == "n":
								break
							elif hr == 'y':
								ss,st = git.rebase(remoteBranch)
								# exe result?
								print(ss)
								if st != 0:
									git.rebaseAbort()
									raise Exception("rebase failed. you should manually merge it.[err:%d]" % st)
								break
					else:
						while True:
							hr = input("\n\n*** It could be impossible to rebase onto remoteBranch. rebase/skip: ").lower()
							if hr == 'rebase':
								ss = git.rebase(remoteBranch)
								print(ss)
								break
							elif hr == 'skip':
								break

					# print commit log again
					self.printCommitLogForPush(currentBranch, remoteBranch)

		target = input("\nInput remote branch name you push to: ")
		if target == "":
			raise ErrFailure("Push is canceled")

		ss2 = remoteBranch.split("/")		

		# push it	
		ss, status = systemSafe("git push %s %s:%s" % (ss2[0], currentBranch, target))
		print(ss)
		
		if status != 0:
			while True:
				hr = input("\n\nPush failed. Do you want to push with force option?[y/N]: ").lower()
				if hr == 'y':
					ss = system("git push origin %s:%s -f" % (currentBranch, target))
					print(ss)				
					break
				elif hr == 'n' or hr == '':
					break

	def doSetMain(self, dlg):
		if not dlg.init():
			dlg.close()
			return False

		self.dialog = dlg
		g.loop.widget = dlg.mainWidget
		return True


class mDlgMainDc(cDialog):
	def __init__(self):
		super().__init__()

		# content
		self.widgetFileList = mListBox(urwid.SimpleFocusListWalker(btnListMakeTerminal([], None)))
		self.widgetCmdList = mListBox(urwid.SimpleFocusListWalker(btnListMakeTerminal([], None))) # 이거 파일목록 아래에뭔가 보여주는건데..
		self.widgetContent = urwid.Pile([self.widgetFileList, ('pack', urwid.Divider('-')), (8, self.widgetCmdList)])
		self.widgetContent.isShow = True

		# extra
		self.widgetWorkLabel = urwid.Text("< Workspace >")
		self.widgetWorkList = mListBox(urwid.SimpleFocusListWalker(btnListMakeTerminal([], None)))
		self.widgetTempLabel = urwid.Text("< Attr >")
		self.widgetTempList = mListBox(urwid.SimpleFocusListWalker(btnListMakeTerminal([], None)))
		self.widgetExtraList = urwid.Pile([("pack", self.widgetWorkLabel), self.widgetWorkList, ("pack", self.widgetTempLabel), self.widgetTempList])

		# main frame + input
		#- F(pull) P(push) L(list repo) g(goto) C(commit) h(enter) jk(up/down)
		self.title = ">> sc V%s" % g.version
		self.headerText = urwid.Text(self.title)
		self.widgetFrame = urwid.Columns([('weight', 1, self.widgetContent), (20, self.widgetExtraList)])
		self.edInput = editGen("$ ", "", lambda edit, text: self.onInputChanged(edit, text))
		self.mainWidget = urwid.Frame(self.widgetFrame, header=self.headerText, footer=self.edInput)

		self.cmd = ""
		self.mode = ""  # d면 등록된 폴더만 표시
		self.gitBranch = None
		self.dcdata = None
		self.lastPath = None

		# work space
		pp = os.getcwd()
		self.workList = [pp]
		self.workPt = 0


	def init(self):
		self.cmdShow([])  # hide extra panel
		self.changePath(os.getcwd())
		return True

	# 이거 용도가 뭔지 까먹었다. lstItem을 보여주는건데... 아마... 부가기능인듯...
	def cmdShow(self, lstItem):
		isShow = len(lstItem) > 0
		if isShow != self.widgetContent.isShow: # 이거 자체는 왼쪽 컨텐츠다.
			self.widgetContent.isShow = isShow
			if isShow:
				#self.widgetContent.contents[1] = (self.widgetContent.contents[1][0], (urwid.widget.PACK, None))
				self.widgetContent.contents[1] = (urwid.Divider('-'), (urwid.widget.PACK, None))
				self.widgetContent.contents[2] = (self.widgetContent.contents[2][0], (urwid.widget.GIVEN, 8))
			else:
				#self.widgetContent.contents[1] = (self.widgetContent.contents[1][0], (urwid.widget.GIVEN, 0))  # 이게 잘안된다. 아마 divider는 pack만 지원하는듯
				self.widgetContent.contents[1] = (urwid.Pile([]), (urwid.widget.GIVEN, 0))
				self.widgetContent.contents[2] = (self.widgetContent.contents[2][0], (urwid.widget.GIVEN, 0))

		if not isShow:
			return

		# list
		lstItem = [ ("std", x, None) for x in lstItem ]
		refreshBtnListMarkupTuple(lstItem, self.widgetCmdList, lambda btn: self.onFileSelected(btn))

	def onInputChanged(self, edit, text):
		if self.cmd == "find" or self.cmd == "goto":
			last = ""
			if len(text) > 0:
				last = text[-1]
			if last in ["R", 'J', 'K', "H", "Q"]:
				def _cb(_, data):
					edit.set_edit_text(data["text"][:-1])

				g.loop.set_alarm_in(0.00001, _cb, dict(dlg=self, edit=edit, text=text))
				self.unhandled(last)
				return

			self.fileRefresh(text)

	# not used code will be removed
	def gotoRefresh(self, newText):
		filterStr = self.edInput.get_edit_text() if newText is None else newText
		if filterStr != "":
			lstPath = g.regFindItems(filterStr)
		else:
			lstPath = g.regList[:]

		lst = [("greenfg", x["path"], x) for x in lstPath]

		self.headerText.set_text("%s - %d" % (self.title, len(lst)))
		refreshBtnListMarkupTuple(lst, self.widgetFileList, lambda btn: self.onFileSelected(btn))

	def fileRefresh(self, newText = None):
		if self.cmd == "goto":  # deprecated code
			self.gotoRefresh(newText)
			return

		# filtering
		if self.cmd == "find":
			filterStr = self.edInput.get_edit_text() if newText is None else newText
		else:
			filterStr = ""

		curPath = os.getcwd()
		# TODO: use scandir

		self.dcdata = None
		lst = []	# name, order
		for item in os.listdir(curPath):
			if item == ".dcdata":
				self.dcdataLoad()
				continue
			else:
				lst.append( (item, 0) )

		lst2 = []
		if filterStr != "":
			for x in lst:
				ss = x[0].lower()
				fil = filterStr.lower()
				if ss.startswith(fil):
					lst2.append((x[0], 2))
				elif fil in ss:
					lst2.append((x[0], 1))
				else:
					lst2.append((x[0], 0))
		else:
			# 등록된 폴더 우선
			regPathList = [ii['path'] for ii in g.regList]
			for x in lst:
				full = os.path.join(curPath, x[0])
				if full in regPathList:
					lst2.append((x[0], 1))
				else:
					lst2.append((x[0], 0))
		lst = lst2

		# name, osStat, order
		lst2 = [ (x[0], osStat(os.path.join(curPath, x[0])), x[1]) for x in lst]
		#if filterStr != "":
			#lst2.sort(key=lambda x: -1 if x[2] == 1 else 1)
		lst2.sort(key=lambda ii: -ii[2])

		# registered list only
		if self.dcdata is not None and self.mode != "":
			def _check(fname):
				dcItem = self.dcdataGet(fname)
				if dcItem is None:
					return self.mode == "d1"
				else:
					return dcItem["type"] == "S"

			lst2 = [ (x[0], x[1]) for x in lst2 if _check(x[0]) ]

		# dir sort
		def _sortStMode(stMode):
			if stMode is None:
				return 2
			elif stat.S_ISDIR(stMode.st_mode):
				return -1
			else:
				return 1
				
		lst2.sort(key=lambda x: _sortStMode(x[1]))
		lst2.insert(0, ("..", None, 0))

		# set focus on first matched fitem
		filterPos = -1
		if filterStr != "":
			for idx, ii in enumerate(lst2):
				if ii[2] == 2:
					filterPos = idx
					break
			if filterPos == -1:
				for idx, ii in enumerate(lst2):
					if ii[2] == 1:
						filterPos = idx
						break

		#itemList = [ (os.path.basename(x[0]), x[1], x[2]) for x in lst2]
		# mstd, name, fattr
		def genDisplayItem(x):
			if x[0] == "..":
				isDir = True
			elif x[1] is None:
				isDir = False
			else:
				isDir = stat.S_ISDIR(x[1].st_mode)

			mstd = None
			if filterStr != "":
				if x[2] == 0:
					mstd = "grayfg"
				elif x[2] == 1:
					mstd = "bluefg"
				elif x[2] == 2:
					mstd = "cyanfg"
			else:
				if x[2] == 1:
					mstd = 'bold'
				else:
					if isDir:
						dcItem = self.dcdataGet(x[0])
						if dcItem is not None:
							if dcItem["type"] == "S":
								mstd = "bluefgb"
							else:
								mstd = "grayfg"
					else:
						dcItem = self.dcdataGet(x[0])
						if dcItem is not None:
							if dcItem["type"] == "S":
								mstd = "bold"
							else:
								mstd = "grayfg"

					if mstd is None:
						mstd = 'greenfg' if isDir else 'std'

			return mstd, x[0], x[1]

		# status
		itemList = list(map(genDisplayItem, lst2))
		status = ""
		item = g.regFindByPath(curPath)
		if item is not None:
			status = "*"
			if "repo" in item and item["repo"]:
				status += "+"
			status = "(%s)" % status

		# git post
		gitSt = ""
		if self.gitBranch is not None:
			cntStaged = 0
			cntModified = 0
			cntUntracked = 0
			gitItemList = git.statusFileList()
			for gitItem in gitItemList:
				if gitItem[1] == "s":
					cntStaged += 1
				elif gitItem[1] == "?":
					cntUntracked += 1
				else:
					cntModified += 1

				name = termianl2plainText(gitItem[0])[3:]
				def gen2(x):
					#print("target - [%s] - %s" % (x[2], name))
					if x[1] == name:
						if gitItem[1] == "s":
							mstd = "bluefg"
						elif gitItem[1] == "?":
							mstd = "underline"
						else:
							mstd = "cyanfg"

						return mstd, x[1], x[2]
					else:
						return x

				itemList = list(map(gen2, itemList))

			ss1 = ""
			if cntStaged > 0:
				ss1 += "S:%d, " % cntStaged
			if cntModified > 0:
				ss1 += "M:%d, " % cntModified
			if cntUntracked > 0:
				ss1 += "?:%d, " % cntUntracked

			if ss1 != "":
				ss1 = ss1[:-2]

			gitSt = " - git(%s)" % ss1

		featureStr = "" if self.cmd is "" else "[%s]" % self.cmd
		featureExtra = ""
		if self.cmd == "find":
			featureExtra = ""
		ss = "%s%s - %s%s - %d%s %s" % (self.title, featureStr, curPath, status, len(itemList)-1, gitSt, featureExtra)
		self.headerText.set_text(ss)

		focusPos = 0
		if filterStr == "":
			if g.targetFile is not None:
				for idx, item in enumerate(itemList):
					if item[1] == g.targetFile:
						focusPos = idx

				g.targetFile = None

			else:
				if self.lastPath == curPath:
					focusPos = self.widgetFileList.focus_position
				elif self.lastPath is not None and os.path.dirname(self.lastPath) == curPath:
					# set focus on the last path
					targetName = os.path.basename(self.lastPath)
					for idx, item in enumerate(itemList):
						if item[1] == targetName:
							focusPos = idx
							break
		else:
			if filterPos != -1:
				focusPos = filterPos

		if focusPos >= len(itemList):
			focusPos = 0

		del self.widgetFileList.body[:]
		self.widgetFileList.body += btnListMakeMarkup(itemList, lambda btn: self.onFileSelected(btn))
		self.widgetFileList.focus_position = focusPos

		self.lastPath = curPath

		# extra
		'''
		lst = []
		if filterStr != "":
			lst += g.findItems(filterStr)
			lst = [ x["path"] for x in lst ]

		self.extraShow(lst)
		'''

	def dcdataLoad(self):
		with open(".dcdata", "r") as fp:
			self.dcdata = json.load(fp)

	def dcdataSave(self):
		if self.dcdata is None:
			os.remove(".dcdata")
			return

		with open(".dcdata", "w") as fp:
			json.dump(self.dcdata, fp)

	def dcdataGet(self, fname):
		if self.dcdata is None:
			return None

		for item in self.dcdata:
			if item["name"] == fname:
				return item
		return None

	def dcdataAdd(self, fname, obj):
		if self.dcdata is None:
			self.dcdata = []

		obj["name"] = fname
		self.dcdata.append(obj)

	def dcdataRemove(self, item):
		self.dcdata.remove(item)
		if len(self.dcdata) == 0:
			self.dcdata = None


	def onFileSelected(self, btn):
		pass

	def changePath(self, pp, newCmd=""):
		if not os.path.isdir(pp):
			return False

		pp = os.path.realpath(pp)
		os.chdir(pp)
		g.savePath(pp)  # always change folder

		# check git repo
		try:
			ss = subprocess.check_output(["git", "branch", "--color=never"], stderr=subprocess.DEVNULL).decode()
			# TODO: "* develop", "* (HEAD detached at ae4c400d)"
			name = re.search(r"^\*\s(\w+)", ss, re.MULTILINE)
			if name is None:
				self.gitBranch = None
			else:
				self.gitBranch = name.group(1)
		except subprocess.CalledProcessError:
			self.gitBranch = None

		self.workList[self.workPt] = pp
		self.workRefresh()

		self.mode = ""  # 모드도 초기화

		# filter상태도 클리어하는게 맞나?
		self.inputSet(newCmd)
		self.edInput.set_edit_text("")
		self.fileRefresh()

	def inputSet(self, status):
		"""
		:param status: filter,
		:return:
		"""
		self.cmd = status
		if status == "":
			self.mainWidget.set_focus("body")
		else:
			self.mainWidget.set_focus("footer")

		self.edInput.set_edit_text("")
		self.edInput.set_caption("%s%s$ " % ("" if self.gitBranch is None else "[%s] " % self.gitBranch, self.cmd))

	def regToggle(self, pp):
		item = g.regFindByPath(pp)
		if item is None:
			g.regAdd(pp)
		else:
			g.regRemove(pp)
		self.fileRefresh()

	# return: index
	def fileSelect(self, name):
		for idx, item in enumerate(self.widgetFileList.body):
			if name == item.base_widget.get_label():
				self.widgetFileList.focus_position = idx
				return idx
		return -1

	def fileRefreshKeepFocus(self):
		pp = self.getFocusPath()
		#self.mode = ""
		self.inputSet("")
		self.fileRefresh()

		return self.fileSelect(os.path.basename(pp))

	def inputFilter(self, keys, raw):
		if g.loop.widget != g.dialog.mainWidget:
			return keys

		if self.cmd == "find":
			# ctrl+j는 enter, alt+시리즈는 안오고.. 그냥 shift+JKH를 쓴다
			if filterKey(keys, "up"):
				self.widgetFileList.focusPrevious()
			elif filterKey(keys, "down"):
				self.widgetFileList.focusNext()
			elif filterKey(keys, "J"):
				self.widgetFileList.focusNext()
			elif filterKey(keys, "K"):
				self.widgetFileList.focusPrevious()
			elif filterKey(keys, "U"):
				self.changePath("..", "find")
			elif filterKey(keys, "H"):
				self.changePath(self.getFocusPath(), "find")
			elif filterKey(keys, "esc"):
				self.fileRefreshKeepFocus()

			elif filterKey(keys, "enter"):
				# self.mainWidget.set_focus("body")
				pp = self.getFocusPath()
				if os.path.isdir(pp):
					self.changePath(pp)  # 바로 이동 + find는 푼다
				else:
					self.fileRefreshKeepFocus()

			elif filterKey(keys, "C"):
				self.doCommit()

			elif filterKey(keys, "ctrl ^"):
				if self.mainWidget.get_focus() == "body":
					pass
				elif self.mainWidget.get_focus() == "footer":
					# find cmd
					ss = self.edInput.get_edit_text()
					self.inputSet("")
					self.doFind(ss)
					return

		elif filterKey(keys, "enter"):
			if self.mainWidget.get_focus() == "body":
				self.changePath(self.getFocusPath())
				return
			else:
				if self.cmd == "goto":
					self.changePath(self.getFocusPath())
					return
				elif self.cmd == "shell":
					ss = self.edInput.get_edit_text()
					self.inputSet("")

					arr = ss.split(" ")
					for idx, i in enumerate(arr):
						if i == "$":
							arr[idx] = self.getFocusName()
					ss = " ".join(arr)
					dlog(ss)

					g.loop.stop()
					print("cmd: %s..." % ss)
					ss,code = systemSafe(ss)
					print(ss)
					input("Enter to return...(exit code:%d)" % code) # TODO: support esc key?
					g.loop.start()
					self.fileRefresh()

				elif self.cmd == "cmd":
					ss = self.edInput.get_edit_text()
					self.inputSet("")

					if ss == "list":
						self.doRegList()
					elif ss == "reg":
						pp = os.getcwd()
						item = g.regFindByPath(pp)
						if item is not None:
							# already registered
							popupMsg("Regiter the folder", "The path is already registerted\n%s" % pp, 60)
							return

						# add
						g.regAdd(pp)
						self.fileRefresh()

						return

					elif ss == "del":
						pp = os.getcwd()
						g.regRemove(pp)
						self.fileRefresh()
						return

					elif ss == "set repo":
						pp = os.getcwd()
						item = g.regFindByPath(pp)
						if item is None:
							# no item
							popupMsg("Set repo status", "The path is no registered\n%s" % pp, 60)
							return

						# set repo
						item["repo"] = not item["repo"] if "repo" in item else True

						g.configSave()
						self.fileRefresh()
						popupMsg("Set repo status", "The path is set as %s\n%s" % ("Repo" if item["repo"] else "Not Repo", pp), 60)
						return
					else:
						if ss.startswith("find ") or ss.startswith("ff "):
							target = ss[ss.index(" ")+1:]
							self.doFind(target)
							return

						elif ss.startswith("grep ") or ss.startswith("gg "):
							target = ss[ss.index(" ")+1:]
							self.doGrep(target)
							return

						popupMsg("Command", "No valid cmd\n -- %s" % ss)

			# 이거 뭐하는 코드지?
			#item = self.widgetCmdList.focus
			#pp = item.original_widget.get_label()
			#self.changePath(pp)

		"""
		if filterKey(keys, "left"):
			pp = os.getcwd()
			pp = os.path.dirname(pp)
			os.chdir(pp)
			self.fileRefresh()
		"""

		"""
		if "down" in keys:
			self.widgetContent.scrollDown()
			return self.excludeKey(keys, "down")
		"""

		return keys

	def getFocusName(self):
		btn = self.widgetFileList.focus
		fname = btn.base_widget.get_label()
		return fname

	def getFocusPath(self):
		pp = os.getcwd()
		fname = self.getFocusName()
		return os.path.join(pp, fname)

	def workNew(self):
		pp = os.getcwd()
		self.workList.append(pp)
		self.workPt += 1
		self.workRefresh()

	def workRemove(self):
		if len(self.workList) <= 1:
			return

		del self.workList[self.workPt]
		if self.workPt >= len(self.workList)-1:
			self.workPt = len(self.workList)-1

		self.workGo()

	def workMove(self, add):
		if add == 0:
			return

		elif add < 0:
			if self.workPt == 0:
				return
			self.workPt -= 1
		else:
			if self.workPt+1 >= len(self.workList):
				return

			self.workPt += 1

		self.workGo()

	def workGo(self):
		# control refresh and go
		self.workRefresh()
		item = self.widgetWorkList.focus
		x = item.original_widget.attr
		os.chdir(x)
		self.fileRefresh()


	def workRefresh(self):
		del self.widgetWorkList.body[:]

		# std, focus, text, attr
		itemList =  [ ("std", os.path.basename(x), x) for x in self.workList ]
		self.widgetWorkList.body += btnListMakeMarkup(itemList, lambda btn: self.onFileSelected(btn))
		self.widgetWorkList.focus_position = self.workPt

	def doCommit(self):
		def onExit():
			g.doSetMain(self)

		if self.gitBranch is None:
			popupMsg("Error", "Not git repository")
			return

		dlg = DlgGitStatus(onExit)
		g.doSetMain(dlg)

	def unhandled(self, key):
		if key == 'f4' or key == "q" or key == "Q":
			if self.cmd == "find":
				self.inputSet("")
				self.fileRefresh()
				return

			#g.savePath(os.getcwd())
			raise urwid.ExitMainLoop()

		elif key == "f1":
			# help
			pass

		elif key == "f5":
			self.fileRefresh()
			return

		elif key == "f":  # filter
			self.inputSet("find")
			return

		elif key == "R":
			pp = self.getFocusPath()
			self.regToggle(pp)
			return

		elif key == "L":
			self.doRegList()

		elif key == "g":  # go
			# use separated dialog for goto feature
			#self.inputSet("goto")
			#self.fileRefresh()
			self.doGoto()
			return

		elif key == "d":
			if self.mode == "":
				self.mode = "d1"
			elif self.mode == "d1":
				self.mode = "d2"
			else:
				self.mode = ""

			self.fileRefresh()

		elif key == "/":  # cmd
			self.inputSet("cmd")
			return

		elif key == "s": # shell
			self.inputSet("shell")
			return

		elif key == "C": # git commit
			self.doCommit()
			return

		elif key == "T":
			g.loop.stop()
			systemRet("tig")
			g.loop.start()
			self.fileRefresh()
			return
		elif key == "G":    # grep
			return
		elif key == "S":    # search(find)
			return

		elif key == "F": # git update
			cur = os.getcwd()
			g.loop.stop()
			gr.actionUpdate(cur)
			input("Enter to return...")
			g.loop.start()
			self.fileRefresh()

		elif key == "P":
			g.loop.stop()
			print("Fetching first...")
			try:
				ss, code = git.fetch()
				if code != 0:
					print("Error - %s" % ss)
				else:
					g.gitPush()
			except Exception as e:
				print("Error - %s" % e)

			input("Enter to return...")
			g.loop.start()
			self.fileRefresh()

		elif key == "E":
			name = self.getFocusName()
			if name == "..":    # special case
				pp = os.getcwd()
			else:
				pp = self.getFocusPath()

			# /cygdrive/...을 제대로 인식못한다. 그냥 상대 경로로..
			#name = os.path.basename(pp)

			g.loop.stop()
			systemRet("%s %s" % (g.editApp, pp))
			g.loop.start()
			self.fileRefresh()

		elif key == "M" or key == "N":  # M is important item, N is ignorable list
			fname = self.getFocusName()
			item = self.dcdataGet(fname)

			ftype = "S" if key == "M" else "I"
			if item is None:
				self.dcdataAdd(fname, dict(type=ftype))
			else:
				if item["type"] == ftype:
					self.dcdataRemove(item)
				else:
					item["type"] = ftype

			self.dcdataSave()
			self.fileRefresh()

		#elif key == "ctrl h":
		#	popupMsg("Dc help", "Felix Felix Felix Felix\nFelix Felix")

		elif key == "meta right" or key == "meta l":
			self.workNew()
		elif key == "meta left" or key == "meta h":
			self.workRemove()

		elif key == "meta up" or key == "meta k":
			self.workMove(-1)
		elif key == "meta down" or key == "meta j":
			self.workMove(1)

		elif key == "j":   # we can't use ctrl+j since it's terminal key for enter replacement
			self.widgetFileList.focusNext()
		elif key == "k":
			self.widgetFileList.focusPrevious()
		elif key == "J":
			for i in range(10):
				self.widgetFileList.focusNext()
		elif key == "K":
			for i in range(10):
				self.widgetFileList.focusPrevious()

		elif key == "u" or key == "." or key == "U":
			self.changePath("..")

		elif key == "h" or key == "H":   # enter
			self.changePath(self.getFocusPath())

		elif key == "up":
			if self.cmd == "goto":
				self.widgetFileList.focusPrevious()
			else:
				self.mainWidget.set_focus("body")
		elif key == "down":
			if self.cmd == "goto":
				self.widgetFileList.focusNext()
			else:
				self.mainWidget.set_focus("body")

		elif key == "esc":
			self.mode = ""  # 모드도 초기화
			self.inputSet("")
			self.fileRefresh()

		'''
		elif type(key) == tuple:    # mouse
			pass
		else:
			self.mainWidget.set_focus("footer")
			#print(key)
			if len(key) == 1:
				#self.edInput.set_edit_text(self.edInput.get_edit_text()+key)
				self.edInput.insert_text(key)
		'''


	def doGoto(self):
		def onExit():
			g.doSetMain(self)
			'''
			if not self.refreshFileList():
				g.loop.stop()
				print("No modified or untracked files")
				sys.exit(0)
			'''

		dlg = mDlgGoto(onExit)
		g.doSetMain(dlg)

	def doRegList(self):
		def onExit():
			g.doSetMain(self)
			'''
			if not self.refreshFileList():
				g.loop.stop()
				print("No modified or untracked files")
				sys.exit(0)
			'''

		dlg = DlgRegList(onExit)
		g.doSetMain(dlg)

	def doFind(self, target):
		def onExit():
			g.doSetMain(self)

		dlg = DlgFind(onExit)
		g.doSetMain(dlg)
		cmds = [find_executable("find"), ".", "-name", target]

		#g.loop.stop()
		#print(cmds)
		#sys.exit(1)

		subMake(dlg, cmds)

	def doGrep(self, target):
		def onExit():
			g.doSetMain(self)

		dlg = DlgAck(onExit)
		g.doSetMain(dlg)

		cmds = [find_executable(g.grepApp), "--group", "--color", target]
		subMake(dlg, cmds)


def subMake(dlg, cmds):
	writeFd = g.loop.watch_pipe(lambda data: dlg.recvData(data))
	g.subProc = subprocess.Popen(cmds, bufsize=0, stdout=writeFd, close_fds=True)

	def subCheck(_handle, _userData):
		if g.subProc.poll() is not None:
			#dlg.headerText.set_text(dlg.header + "!!!")
			dlg.recvData(None)
		# g.loop.remove_alarm(handle)
		else:
			g.subTimerHandler = g.loop.set_alarm_in(0.1, subCheck, None)

	subCheck(None, None)

def uiMain(dlgClass, cmds=None):
	try:
		dlg = dlgClass()
	except urwid.ExitMainLoop:
		return

	if not dlg.init():
		return

	#def urwidUnhandled(key):
	#	g.dialog.unhandled(key)

	def urwidInputFilter(keys, raw):
		op = getattr(g.dialog, "inputFilter", None)
		if not callable(op):
			return keys

		return g.dialog.inputFilter(keys, raw)

	g.dialog = dlg
	g.loop = urwid.MainLoop(dlg.mainWidget, palette, urwid.raw_display.Screen(),
							unhandled_input=lambda key: g.dialog.unhandled(key),
							input_filter=urwidInputFilter)

	if cmds is not None:
		subMake(dlg, cmds)

	g.loop.run()

# workItemIdx: 지정되면 해당 번째 다음께 target이 된다.
def doSubCmd(cmds, dlgClass, targetItemIdx=-1):
	if targetItemIdx != -1 and len(sys.argv) == targetItemIdx:
		target = cmds[targetItemIdx]
		item = g.regFindByName(target)
		os.chdir(item["path"])
		cmds = cmds[:targetItemIdx] + cmds[targetItemIdx+1:]

	uiMain(dlgClass, cmds)

# git action - update...
class GitActor(object):
	def __init__(self):
		self.isInit = False
		self.repoList = [dict(name=["test"], path="")]
		
	def init(self):
		self.repoList = [repo for repo in g.regList if "repo" in repo and repo["repo"]]
		self.isInit = True
		
	def repoAllName(self):
		return [repo["names"][0] for repo in self.repoList]
		
	def action(self, action, target):
		if not self.isInit:
			self.init()

		if target is not None:
			return action(self, target)

		else:
			for comp in self.repoAllName():
				hr = action(self, comp)
				if not hr:
					return False
		return True

	def log(self, lv, msg):
		if lv == 0:
			print("%s%s%s" % (Ansi.redBold, msg, Ansi.clear))
		elif lv == 1:
			print("%s%s%s" % (Ansi.blueBold, msg, Ansi.clear))
		else:
			print("%s" % msg)
			
	def log2(self, color, name, msg):
		ansiBold = Ansi.blueBold if Color.blue == color else Ansi.redBold
		ansiNor = Ansi.blue if Color.blue == color else Ansi.red
		print("%s%s -> %s%s%s" % (ansiBold, name, ansiNor, msg, Ansi.clear))

	def getRepo(self, name):
		for repo in self.repoList:
			if name in repo["names"]:
				return repo
				
		raise Exception("Can't find repo[name:%s]" % name)

	def getRepoPath(self, name):
		repo = self.getRepo(name)
		path = repo["path"]
		return path
				
	def changePath(self, name):
		if name.startswith("/"):
			path = name
		else:
			path = self.getRepoPath(name)
			if not os.path.isdir(path):
				raise FileNotFoundError(path, "%s(%s) -> doesn't exist"  % (name, path))

		os.chdir(path)
		ss = "path:%s" % path
		return ss

	def checkSameWith(self, name, branchName, remoteBranch):
		rev = git.rev(branchName)
		rev2 = git.rev("remotes/"+remoteBranch)
		isSame = rev == rev2
		if isSame:
			self.log2(Color.blue, name, "%s is same to %s"  % (branchName, remoteBranch))
			return True
		else:
			commonRev = git.commonParentRev(branchName, remoteBranch)
			#print("common - %s" % commonRev)
			if commonRev != rev2:
				self.log2(Color.red, name, "%s(%s) - origin/master(%s) -->> Different" % (branchName, rev, rev2))
				return False
		
			# 오히려 앞선경우다. True로 친다.
			gap = git.commitGap(branchName, remoteBranch)
			self.log2(Color.red, name, "Your local branch(%s) is forward than %s[%d commits]" % (branchName, remoteBranch, gap))
			
			# print commit log
			#ss = system("git log --oneline --graph --all --decorate --abbrev-commit %s..%s" % (remoteBranch, branchName))
			ss = git.commitLogBetween(branchName, remoteBranch)
			print(ss)
			
			return True

	def stashCheck(self, name):
		uname = "###groupRepo###"
		stashName = git.stashGetNameSafe(uname)
		if stashName is not None:
			self.log2(Color.red, name, "YOU HAVE STASH ITEM. PROCESS IT FIRST")
			return False

		return True

	def actStatusComponent(self, name):
		try:
			path = self.changePath(name)
		except ErrNoExist as e:
			self.log2(Color.red, name, "%s DOESN'T exist" % e.path)
			return

		if not self.stashCheck(name):
			return

		branchName = git.getCurrentBranch()
		remoteBranch = git.getTrackingBranch()
		if remoteBranch is None:
			self.log2(Color.red, name, "%s DONT'T HAVE TRACKING branch" % branchName)
			return

		isSame = self.checkSameWith(name, branchName, remoteBranch)
		if isSame:
			# check staged file and untracked file
			ss = system("git status -s")
			if ss != "":
				print(ss)
		else:
			diffList = git.checkRebaseable(branchName, remoteBranch)
			if len(diffList) == 0:
				self.log2(Color.blue, name, "Be able to fast-forward... - %s" % path)
			else:
				self.log2(Color.red, name, "NOT be able to fast forward - %s" % path)
			
			#ss = system("git st")
			#print(ss)

	def actionUpdate(self, target):
		#print("fetch......")
		#self.action(GitActor.actFetch, target)

		#print("merge......")
		#self.action(GitActor.actMergeSafe, target)

		print("pull......")
		if not self.action(GitActor.actPull, target):
			return

		print("status......")
		self.action(GitActor.actStatusComponent, target)

	def actMergeSafe(self, name):
		try:
			path = self.changePath(name)
		except ErrNoExist as e:
			self.log2(Color.red, name, "%s DOESN'T exist" % e.path)
			return False

		if not self.stashCheck(name):
			return False

		branchName = git.getCurrentBranch()
		remoteBranch = git.getTrackingBranch()
		if remoteBranch is None:
			self.log2(Color.red, name, "%s DONT'T HAVE TRACKING branch" % branchName)
			return False
		
		isSame = self.checkSameWith(name, branchName, remoteBranch)
		if isSame:
			return True

		# allow the repo that no registerted
		if not name.startswith("/"):
			repo = self.getRepo(name)
			if "type" in repo and repo["type"] == "bin":
				self.log2(Color.blue, name, "merge with %s - %s - bin type" % (remoteBranch, path))

				uname = "###groupRepo###"
				ss = system("git stash save -u \"%s\"" % uname)
				print(ss)
				ss = system("git merge %s" % remoteBranch)
				print(ss)
				stashName = git.stashGetNameSafe(uname)
				ss = system("git stash pop %s" % stashName)
				print(ss)
	
		diffList = git.checkRebaseable(branchName, remoteBranch)
		if len(diffList) != 0:
			self.log2(Color.red, name, "NOT be able to fast forward - %s" % path)
		else:			
			self.log2(Color.blue, name, "merge with %s - %s" % (remoteBranch, path))
			ss = system("git rebase %s" % remoteBranch)
			print(ss)

		return True

	def actFetch(self, name):
		try:
			path = self.changePath(name)
		except ErrNoExist as e:
			self.log2(Color.red, name, "%s DOESN'T exist" % e.path)
			return False

		self.log2(Color.blue, name, "fetch --prune - %s" % path)
		system("git fetch --prune")

		return True

	def actPull(self, name):
		try:
			path = self.changePath(name)
		except ErrNoExist as e:
			self.log2(Color.red, name, "%s DOESN'T exist" % e.path)
			return False

		cmd = "pull"
		if g.isPullRebase:
			cmd += " -r"
		self.log2(Color.blue, name, "%s - %s" % (cmd, path))
		ss, code = systemSafe("git %s" % cmd)
		if code != 0:
			self.log2(Color.red, name, "pull is failed\n%s" % ss)
			return False

		return True

gr = GitActor()


def winTest():
	ss = system("c:\\cygwin64\\bin\\git.exe diff --color dc.py")

	kk = terminal2markup(ss)
	st = ss.find("\x1b")
	print("%d %x %x %x %x" % (st, ss[0], ss[1], ss[2], ss[3]))
	sys.exit(0)

def getNonblocingInput(timeout=0):
	if select.select([sys.stdin], [], [], timeout) == ([sys.stdin], [], []):
		return sys.stdin.read(10240)

def removeEmptyArgv():		
	#cmds = shlex.split(cmdLine)
	# find with shell=true not working on cygwin
	for idx,data in reversed(list(enumerate(sys.argv))):
		if data != "":
			sys.argv = sys.argv[:idx+1]
			break

l1 = "### sharpen-commander script ###"
def setupSc():
	if os.getenv('SC_OK', 0) != 0:
		return

	ok = False
	pp = os.path.join(expanduser("~"), ".bashrc")
	if os.path.exists(pp):
		with open(pp, "r") as fp:
			for line in fp:
				m = re.search(l1, line)
				if m is not None:
					ok = True
					break

		if not ok:
			with open(pp, "a") as fp:
				print("Appending script-bash.sh into bashrc")
				dir = os.path.dirname(__file__)
				fp.write("\n%s\n. %s/script-bash.sh\n\n" % (l1, dir))
				print("Please 'source ~/.bashrc' then type 'sc' to run.")
				sys.exit(1)

	print("SC_OK is not set.")
	sys.exit(1)


def main():
	setupSc()
	#winTest()
	try:
		os.remove("/tmp/cmdDevpath")
	except OSError:
		pass

	prog = MyProgram()

	isTty = os.isatty(sys.stdin.fileno())
	if not isTty:
		ss = getNonblocingInput()
		lines = ss.splitlines()
		lines = (line.rstrip() for line in lines)
		lines = list(line for line in lines if line)

		if len(lines) == 1:
			pp = lines[0]
			print("path - %s" % pp)
			if os.path.isfile(pp):
				pp = os.path.dirname(pp)
			g.savePath(pp)
			return

		return

	# under pipe line
	'''
	ss = getNonblocingInput()
	if ss != None:
		ss = ss.strip("\n")
		if ss == "":
			print("Empty path in pipe")
			return
		else:
			#ss = os.path.dirname(ss)
			#print("goto: " + ss)
			#g.savePath(ss)
			pass
		return
	'''
	prog.init()

	argc = len(sys.argv)
	cmd = "" # basic cmd
	if argc > 1:
		cmd = sys.argv[1]
		
	removeEmptyArgv()

	target = None
	if len(sys.argv) >= 3:
		target = sys.argv[2]
		if target == ".":
			# current repo
			cur = os.getcwd() + "/"

			# allow the repo that isn't registerted
			target = cur

			'''
			for repo in gr.repoList:
				repoPath = os.path.realpath(repo["path"])
				if cstartswith(repoPath+"/"):
					second = repo["names"][0]
					break
			if second == ".":
				self.log(0, "Current path[%s] is not git repo." % cur)
				return
			'''

	if cmd == "":
		uiMain(mDlgMainDc)
		return

	elif cmd == "push":
		print("Fetching first...")
		git.fetch()
		g.gitPush()
		return
		
	elif cmd == "ci":
		uiMain(DlgGitStatus)
		return
		
	elif cmd == "list":
		g.regListPrint()
		return
		
	elif cmd == "config":
		g.savePath("~/.synapcmd")
		return
		
	elif cmd == "which":
		ss, status = systemSafe(" ".join(['"' + c + '"' for c in sys.argv[1:]]))
		print(ss)
		print("goto which path...")
		g.savePath(os.path.dirname(ss))
		return
	
	elif cmd == "find":
		# dc find -name "*.py"
		cmds = sys.argv[1:]
		cmds[0] = find_executable(cmds[0])
		doSubCmd(cmds, DlgFind)
		return
		
	elif cmd == "grep":
		# dc ack printf
		cmds = sys.argv[1:]
		cmds[0] = find_executable(g.grepApp)
		cmds.insert(1, "--group")
		cmds.insert(1, "--color")
		doSubCmd(cmds, DlgAck)
		return

	# -- deprecated
	# elif cmd == "findg":
	# 	pp = sys.argv[2]
	# 	if "*" not in pp:
	# 		pp = "*" + pp + "*"
	#
	# 	cmds = ["find", ".", "-name", pp]
	# 	doSubCmd(cmds, mDlgMainFind, 4)
	# 	return
	#
	# elif cmd == "ackg":
	# 	# dc ack printf
	# 	cmds = ["ack"] + sys.argv[2:]
	# 	cmds.insert(1, "--group")
	# 	cmds.insert(1, "--color")
	# 	doSubCmd(cmds, mDlgMainAck, 4)
	# 	return

	elif cmd == "st":
		gr.action(GitActor.actStatusComponent, target)
		return
		
	elif cmd == "fetch":
		gr.action(GitActor.actFetch, target)
		return
		
	elif cmd == "merge":
		gr.action(GitActor.actMergeSafe, target)
		return
		
	elif cmd == "update":
		gr.actionUpdate(target)
		return

	elif cmd == "test":
		branch, rev, upstream, remoteRev, ahead, behind = git.getBranchStatus()
		print("%s[%s] - %s[%s] - %d - %d" % (branch, rev, upstream, remoteRev, ahead, behind))
		return 1

	#print("target - %s" % target)
	g.cd(cmd)
	return 1

"""
if __name__ == "__main__":
	try:
		ret = main()
	except ErrFailure as e:
		print(e)
		sys.exit(1)
"""	

