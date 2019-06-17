import os
from . import (AError, AOS, ACommandLineTool)


def _systemOutput(cmd):
    return AOS.systemOutput(cmd, encoding='UTF-8')
_commandlineTool = ACommandLineTool.CommandLineTool('git', execOutputFunc=_systemOutput)
_commandlineTool.checkExistence()
def getCommandLineTool():
    return _commandlineTool


class Git_Error(AError.Error):
    pass


class Git_ParseMetaDataError(Git_Error):
    def __init__(self, msg):
        Git_Error.__init__(self, "git meta data error: %s" % msg)


class Git_ExportError(Git_Error):
    def __init__(self, msg):
        Git_Error.__init__(self, "git export error: %s" % msg)

class Git_CommitMessageEmptyError(Git_Error):
    def __init__(self):
        Git_Error.__init__(self, "git commit message can't be empty")


def execSubCommand(cmdline, **kwargs):
    _commandlineTool.execCommand(cmdline)

def execOutputSubCommand(cmdline, **kwargs):
    return _commandlineTool.execOutputCommand(cmdline)


RESET_TYPE_SOFT = 'soft'
RESET_TYPE_MIXED = 'mixed'
RESET_TYPE_HARD = 'hard'


class Repository:
    def __init__(self, path):
        """
        :param path: the working copy root path
        """
        self.workDir = path
        self.metaDir = os.path.join(self.workDir, '.git')

    def execSubCommand(self, cmdline, **kwargs):
        with AOS.ChangeDir(self.workDir):
            execSubCommand(cmdline, **kwargs)

    def execOutputSubCommand(self, cmdline, **kwargs):
        with AOS.ChangeDir(self.workDir):
            return execOutputSubCommand(cmdline, **kwargs)

    def getCurrentBranch(self):
        """
        return a tuple(branch, revision)
        """
        filePath = os.path.join(self.metaDir, 'HEAD')
        with open(filePath) as fp:
            try:
                line = fp.readline().rstrip('\n')
                if line.startswith('ref: refs/heads/'):
                    branch = line[len('ref: refs/heads/'):]
                    revision = None
                else:
                    branch = ''  # 处于头指针分离状态
                    revision = line
            except Exception as e:
                raise Git_ParseMetaDataError("Can't parse branch name from HEAD file %s: %s" % (filePath, str(e)))

        if branch != '':
            filePath = os.path.normpath(os.path.join(self.metaDir, 'refs', 'heads', branch))
            with open(filePath) as fp:
                try:
                    revision = fp.readline().rstrip('\n')
                except Exception as e:
                    raise Git_ParseMetaDataError("Can't parse revision from %s: %s" % (filePath, str(e)))

        return branch, revision

    def export(self, path):
        """
        The packing format is decided auto from the ext of <path>
        only support .zip .tar.gz
        """
        fileName = os.path.basename(path)
        prefix = None
        exts = ('.zip', '.tar.gz')
        for ext in exts:
            if fileName.endswith(ext):
                prefix = fileName[:-len(ext)]
        if prefix is None:
            raise Git_ExportError("%s can't packing with %s" % (path, ' or '.join(exts)))

        path = os.path.abspath(path)
        self.execSubCommand('archive --output="%s" --prefix=%s/ --verbose HEAD --' % (path, prefix))

    def reset(self, revision='HEAD', resetType=RESET_TYPE_MIXED):
        self.execSubCommand('reset --%s %s --' % (resetType, revision))

    def clone(self, url, recursive=True, depth=-1, branch='master'):
        cmd = 'clone'
        if recursive:
            cmd += ' --recursive'
        if depth > 0:
            cmd += ' --depth %d' % depth
        if branch != 'master':
            cmd += ' --branch %s' % branch
        cmd += ' %s %s' % (url, self.workDir)
        execSubCommand(cmd)

    def updateSubModule(self, init=True):
        cmd = 'submodule update'
        if init:
            cmd += ' --init'
        self.execSubCommand(cmd)

    def pull(self, prune=True):
        cmd = 'pull'
        if prune:
            cmd += ' -p'
        self.execSubCommand(cmd)

    def push(self, setUpstream=False):
        """
        :param setUpstream: 新建的本地分支需要设置一次上游分支
        """
        currentBranch, _ = self.getCurrentBranch()
        cmd = 'push'
        if setUpstream:
            cmd += ' --set-upstream origin %s' % currentBranch
        self.execSubCommand(cmd)

    def checkout(self, branch, force=False):
        """"
        :param force: Overrite working tree changes
        """
        cmd = 'checkout'
        if force:
            cmd += ' -f'
        cmd += ' %s --' % branch
        self.execSubCommand(cmd)

    def cloneOrPull(self, url, recursive=True, depth=-1, branch='master'):
        if os.path.exists(self.workDir):
            self.pull()
        else:
            self.clone(url, recursive, depth, branch)
        
    def add(self, path, force=True):
        """"
        :param force: Allow adding ignored files
        """
        cmd = 'add'
        if force:
            cmd += ' -f'
        cmd += ' %s' % path
        self.execSubCommand(cmd)

    def status(self, modified=True, deleted=True, untracked=False, ignored=False):
        """
        返回修改的文件列表
        :param modified: True则显示修改的文件
        :param deleted: True则显示删除的文件
        :param untracked: True则显示未跟踪的文件
        :param ignored: True则显示忽略的文件
        """
        cmd = 'status -s'
        if not untracked:
            cmd += ' -uno'
        if ignored:
            cmd += ' --ignored'

        ret = []
        for line in self.execOutputSubCommand(cmd).split('\n'):
            if line == '':
                continue
            if line.startswith(' M '):
                if modified:
                    ret.append(line[3:])
            elif line.startswith(' D '):
                if deleted:
                    ret.append(line[3:])
            elif line.startswith('?? '):
                if untracked:
                    ret.append(line[3:])
            elif line.startswith('!! '):
                if ignored:
                    ret.append(line[3:])
        return ret

    def commit(self, msg, all=False):
        """
        :param msg: 提交时的备注信息
        :param all: 自动 stage 修改和删除的文件, 但未跟踪的文件不受影响
        """
        if not msg:
            raise Git_CommitMessageEmptyError()

        cmd = 'commit'
        if all:
            cmd += ' -a'
        cmd += ' -m "%s"' % msg
        self.execSubCommand(cmd)
