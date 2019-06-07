import os
import sys
import re
import subprocess

class Config:
	def __init__(self):
		self.debugPrintSystem = False
	
g = Config()

def dlog(ss):
	with open("/tmp/debug.log", "a") as fp:
		fp.write(ss+"\n")


def system(args, stderr=subprocess.STDOUT):
	if g.debugPrintSystem:
		print("system command - %s" % args)
	rr = subprocess.check_output(args, stderr=stderr, shell=True).decode("UTF-8")
	rr = rr.rstrip(' \r\n')
	return rr

# result, exitcode
def systemSafe(args):
	if g.debugPrintSystem:
		print("system command - %s" % args)
	# stderr를 지원못한다. getstatusoutput은 쓰면안된다. stderr는 output에 같이 온다.
	status,output = subprocess.getstatusoutput(args)
	#rr = output.decode("UTF-8")
	rr = output
	rr = rr.rstrip(' \r\n')
	return rr,status

def systemRet(args):
	if g.debugPrintSystem:
		print("system command - %s" % args)
		
	ret = subprocess.call(args, shell=True)
	return ret


def programPath(sub=None):
	pp = os.path.dirname(os.path.realpath(sys.argv[0]))
	if sub is not None:
		pp = os.path.join(pp, sub)
	return pp


class git:
	# if remote branch, insert "remotes/"
	@staticmethod
	def rev(branch):
		ss = system("git branch -va")
		m = re.search(r'^[*]?\s+%s\s+(\w+)' % branch, ss, re.MULTILINE)
		rev = m.group(1)
		return rev

	@staticmethod
	def getCurrentBranch():
		return system("git rev-parse --abbrev-ref HEAD")

	@staticmethod
	def getTrackingBranch():
		try:
			return system("git rev-parse --abbrev-ref --symbolic-full-name @{u}")
		except subprocess.CalledProcessError:
			return None

	@staticmethod
	def commonParentRev(br1, br2):
		commonRev = system("git merge-base %s %s" % (br1, br2))
		return commonRev

	@staticmethod
	def printStatus():
		ss = system("git -c color.status=always status -s")
		print(ss+"\n")

	@staticmethod
	def commitGap(brNew, brOld):
		#gap = system("git rev-list %s ^%s --count" % (brNew, brOld))
		gap = system("git rev-list --count %s..%s" % (brOld, brNew))
		return int(gap)

	@staticmethod
	def commitLogBetween(brNew, brOld):
		# color print
		ss = system("git log --color --oneline --graph --decorate --abbrev-commit %s^..%s" % (brOld, brNew))
		return ss

	# return: branch, rev, upstream, remoteRev, ahead, behind
	@staticmethod
	def getBranchStatus():
		#* master                1fbf5de [origin/master: ahead 2] dc: rebase before push is option, print fetch err
		#  remotes/origin/master 688d414 dc: cfg - isPullRebase flag
		branchStatus = system("LANG=en_US git -c color.branch=false branch -avv")
		out = re.search(r"^\*\s(\w+)\s+(\w+)\s(.+)", branchStatus, re.MULTILINE)
		if out is None:
			return None

		branch = out.group(1)
		rev = out.group(2)
		line = out.group(3)

		remoteRev = ""
		upstream = ""
		ahead = 0
		behind = 0
		info = re.search(r"^\[(.+)\]", line)
		if info is not None:
			infos = info.group(1).split(":")
			upstream = infos[0]
			if len(infos) > 1:
				plus = infos[1].split(",")
				for ss2 in plus:
					kk = ss2.strip().split(" ")
					if kk[0] == "ahead":
						ahead = int(kk[1])
					elif kk[0] == "behind":
						behind = int(kk[1])

		out = re.search(r"\s\sremotes/%s\s+(\w+)" % upstream, branchStatus)
		if out is not None:
			remoteRev = out.group(1)

		# upstrea있고, ahead + behind == 0이면 루트랑 동일한건데...
		return branch, rev, upstream, remoteRev, ahead, behind


	@staticmethod
	def checkRebaseable(br1, br2):
		commonRev = git.commonParentRev(br1, br2)
		
		br1Diff = system("git diff --name-only %s %s" % (commonRev, br1))
		br2Diff = system("git diff --name-only %s %s" % (commonRev, br2))
		
		br1 = br1Diff.split()
		br2 = br2Diff.split()
		
		# check same file
		lst2 = []
		for ss in br1:
			if ss in br2:
				lst2.append(ss)
				
		return lst2

	@staticmethod
	def fetch():
		return systemSafe("git fetch --prune")
		
	@staticmethod
	def rebase(branch):
		return systemSafe("git rebase %s" % branch)

	@staticmethod
	def rebaseAbort():
		return system("git rebase --abort")
	
	@staticmethod
	def stashGetNameSafe(name):
		ss = system("git stash list")
		print(ss)
		m = re.search(r'^(stash@\{\d+\}):\s(\w|\s).+: %s$' % name, ss)
		if not m:
			return None

		return m.group(1)
	
	@staticmethod
	def stashPop(name):
		ss = system("git stash pop %s" % name)
		print
		
	@staticmethod
	def statusFileList():
		"""
		file list(staged, modified) in current folder by terminal character
		(terminal name, s or "")
		:return:
		"""
		fileList,ret = systemSafe("git -c color.status=always status -s")   #, stderr=subprocess.DEVNULL)

		# quoted octal notation to utf8
		fileList = bytes(fileList, "utf-8").decode("unicode_escape")
		bb = fileList.encode("ISO-8859-1")
		fileList = bb.decode()

		# remove "" in file name
		fileList2 = []
		for line in fileList.splitlines():
			fileType, fileName = line.split(" ", 1)
			if fileName.startswith("\"") and fileName.endswith("\""):
				fileName = fileName[1:-1]
			fileList2.append(fileType + " " + fileName)

		def getStatus(terminal):
			if "[32m" in terminal:
				return "s"
			elif "??" in terminal:
				return "?"
			else:   # modification
				return ""

		itemList = [(x, getStatus(x)) for x in fileList2 if len(x) > 0]
		return itemList