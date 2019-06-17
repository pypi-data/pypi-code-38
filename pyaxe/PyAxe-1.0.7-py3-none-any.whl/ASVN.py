import os
import xml.etree.ElementTree as ET
import sqlite3
import tempfile
from . import (AError, ACommandLineTool, AOS)


_commandlineTool = ACommandLineTool.CommandLineTool('svn')
_commandlineTool.checkExistence()
def getCommandLineTool():
    return _commandlineTool


class SVN_Error(AError.Error):
    pass

class SVN_SubCommandError(SVN_Error):
    def __init__(self, cmd):
        self.cmd = cmd

    def __str__(self):
        return 'svn: execute sub command(%s) failed' % self.cmd

class SVN_NoMessageError(SVN_SubCommandError):
    def __init__(self, cmd):
        SVN_SubCommandError.__init__(self, cmd)

    def __str__(self):
        return SVN_SubCommandError.__str__(self) + ": message(with -m) can't be empty"

class SVN_AlreadyLockedError(SVN_Error):
    def __init__(self, path, lockOwner, lockComment, lockDate):
        self.path = path
        self.lockOwner = lockOwner
        self.lockComment = lockComment
        self.lockDate = lockDate

    def __str__(self):
        return "svn: path '%s' already locked by user '%s' at %s%s" % (
            self.path, self.lockOwner, self.lockDate, '' if self.lockComment == '' else ': ' + self.lockComment
        )

class SVN_BranchDestinationAlreadyExistError(SVN_Error):
    def __init__(self, dst):
        self.dst = dst

    def __str__(self):
        return "svn: branch destination '%s' already exist" % self.dst


RESOLVE_ACCEPT_BASE = 'base'
RESOLVE_ACCEPT_WORKING = 'working'
RESOLVE_ACCEPT_MINE_CONFLICT = 'mine-conflict'
RESOLVE_ACCEPT_THEIRS_CONFLICT = 'theirs-conflict'
RESOLVE_ACCEPT_MINE_FULL = 'mine-full'
RESOLVE_ACCEPT_THEIRS_FULL = 'theirs-full'


def makeUserPassOptionStr(userpass):
    s = ''
    if userpass:
        s += '--username ' + userpass[0]
        s += ' --password ' + userpass[1]
        s += ' --no-auth-cache'
    return s

def makeRevisionOptionStr(revision):
    """
    :param revision: a revision number, or string('HEAD', 'BASE', 'COMMITTED', 'PREV'), or revision range tuple
    """
    if not revision:
        return ''
    # some command(svn log...) support revision range
    if isinstance(revision, tuple) or isinstance(revision, list):
        return '-r %s:%s' % (revision[0], revision[1])
    return '-r %s' % revision

def makeMessageOptionStr(message):
    s = ''
    if message:
        s += '-m "%s"' % message
    return s


def execSubCommand(cmdline):
    cmdline += ' --non-interactive'
    _commandlineTool.execCommand(cmdline)

def execOutputSubCommand(cmdline):
    cmdline += ' --non-interactive'
    return _commandlineTool.execOutputCommand(cmdline)


def isURL(url):
    for prefix in ('file:\\\\\\', 'svn://', 'http://', 'https://'):
        if url.startswith(prefix):
            return True
    return False

def isSVNPath(path, userpass=None):
    cmd = 'info'
    cmd += ' ' + path
    cmd += makeUserPassOptionStr(userpass)
    try:
        execOutputSubCommand(cmd)
    except AOS.OS_SystemOutputError:
        return False
    return True


def infoDict(pathOrURL, revision=None, userpass=None):
    """
    :param pathOrURL: working copy path or remote url
    """
    cmd = 'info'
    cmd += ' ' + pathOrURL
    cmd += ' --xml'
    cmd += ' ' + makeRevisionOptionStr(revision)
    cmd += ' ' + makeUserPassOptionStr(userpass)
    result = execOutputSubCommand(cmd)
    root = ET.fromstring(result)
    entryNode = root.find('entry')

    ret = {}
    ret['#kind'] = entryNode.attrib['kind']
    ret['#path'] = entryNode.attrib['path']
    ret['#revision'] = int(entryNode.attrib['revision'])  # 整个工作拷贝的版本号
    ret['url'] = entryNode.find('url').text
    
    repoNode = entryNode.find('repo')
    repo = {}
    ret['repo'] = repo
    repo['root'] = repoNode.find('root').text
    repo['uuid'] = repoNode.find('uuid').text

    relativeURLNode = entryNode.find('relative-url')
    if relativeURLNode is None:  # relative-url not supported by svn 1.7.14(installed by yum in CentOS-7)
        ret['relative-url'] = '^' + ret['url'][len(repo['root']):]
    else:
        ret['relative-url'] = relativeURLNode.text
        
    wcInfoNode = entryNode.find('wc-info')
    if wcInfoNode is not None:  # svn info url has no wc-info node
        wcInfo = {}
        ret['wc-info'] = wcInfo
        wcInfo['wcroot-abspath'] = wcInfoNode.find('wcroot-abspath').text
        wcInfo['uuid'] = wcInfoNode.find('schedule').text
        wcInfo['depth'] = wcInfoNode.find('depth').text

    commitNode = entryNode.find('commit')
    commit = {}
    ret['commit'] = commit
    commit['#revision'] = int(commitNode.attrib['revision'])   # 当前目录或文件的版本号

    commitAuthorNode = commitNode.find('author')  # author can be None if the repo has revision 0
    if commitAuthorNode != None:
        commit['author'] = commitAuthorNode.text
    commit['date'] = commitNode.find('date').text

    lockNode = entryNode.find('lock')
    if lockNode is not None:
        lock = {}
        ret['lock'] = lock
        lock['token'] = lockNode.find('token').text
        lock['owner'] = lockNode.find('owner').text
        lockCommentNode = lockNode.find('comment')
        lock['comment'] = '' if lockCommentNode is None else lockCommentNode.text
        lock['created'] = lockNode.find('created').text

    return ret

def checkout(url, path, revision=None, userpass=None):
    cmd = 'checkout'
    cmd += ' ' + url + ' ' + path
    cmd += ' ' + makeRevisionOptionStr(revision)
    cmd += ' ' + makeUserPassOptionStr(userpass)
    execSubCommand(cmd)

def update(path, revision=None, userpass=None):
    cmd = 'update'
    cmd += ' ' + path
    cmd += ' ' + makeRevisionOptionStr(revision)
    cmd += ' ' + makeUserPassOptionStr(userpass)
    execSubCommand(cmd)

def checkoutOrUpdate(url, path, revision=None, userpass=None):
    if os.path.exists(path):
        update(path, revision, userpass)
    else:
        checkout(url, path, revision, userpass)

def export(pathOrURL, path, revision=None, userpass=None):
    cmd = 'export'
    cmd += ' ' + pathOrURL + ' ' + path
    cmd += ' ' + makeRevisionOptionStr(revision)
    cmd += ' ' + makeUserPassOptionStr(userpass)
    execSubCommand(cmd)

def resolve(path, acceptOption, recursive=True, quiet=True):
    """
    :param acceptOption: RESOLVE_ACCEPT_XXX
    """
    cmd = 'resolve'
    cmd += ' ' + path
    if recursive:
        cmd += ' -R'
    if quiet:
        cmd += ' -q'
    cmd += ' --accept ' + acceptOption
    execSubCommand(cmd)

def clearWorkQueue(path):
    """
    Do this action maybe useful if cleanup failed
    :param path: must be a working-copy root dir
    """
    conn = sqlite3.connect(os.path.join(path, '.svn', 'wc.db'))
    conn.execute('DELETE FROM work_queue')

def cleanup(path):
    execSubCommand('cleanup %s' % path)

def revert(path, recursive=True):
    cmd = 'revert ' + path
    if recursive:
        cmd += ' -R'
    execSubCommand(cmd)

def easyClearEverything(path):
    clearWorkQueue(path)
    cleanup(path)
    revert(path)

def add(path, force=True):
    """
    :param path: can be file or dir
    """
    cmd = 'add'
    cmd += ' ' + path
    if force:
        cmd += ' --force'
    execSubCommand(cmd)

def commit(path, includeExternals=False, message=None, userpass=None):
    cmd = 'commit'
    cmd += ' ' + path
    if includeExternals:
        cmd += ' --include-externals'
    cmd += ' ' + makeMessageOptionStr(message)
    cmd += ' ' + makeUserPassOptionStr(userpass)
    execSubCommand(cmd)

def log(pathOrURL, limit=None, verbose=False, searchPattern=None, revision=None, userpass=None):
    """
    :param pathOrURL: working copy path or remote url
    :param limit: when the revision is a range, limit the record count
    :param verbose:
    :param searchPattern:
        - search in the limited records(by param limit)
        - matches any of the author, date, log message text, if verbose is True also a changed path
        - The search pattern use "glob syntax" wildcards
          ?      matches any single character
          *      matches a sequence of arbitrary characters
          [abc]  matches any of the characters listed inside the brackets
    example:
        revision=(5, 10) limit=2 output: 5, 6
        revision=(10, 5) limit=2 output: 10, 9
    :param commonOptions.revision: single revision number or revision range tuple/list
        - if range specified, format as (5, 10) or (10, 50) are both supported
            - for (5, 10): return list ordered by 5 -> 10
            - for (10, 5): return list ordered by 10 -> 5
            - the bound revision 5 or 10 also included
    """
    cmd = 'log'
    cmd += ' ' + pathOrURL
    cmd += ' --xml'
    if limit is not None:
        cmd += ' -l %s' % limit
    if verbose:
        cmd += ' -v'
    if searchPattern is not None:
        cmd += ' --search %s' % searchPattern
    cmd += ' ' + makeRevisionOptionStr(revision)
    cmd += ' ' + makeUserPassOptionStr(userpass)

    result = execOutputSubCommand(cmd)
    root = ET.fromstring(result)

    ret = []
    for logentryNode in root.iterfind('logentry'):
        logentry = {}
        ret.append(logentry)
        logentry['#revision'] = logentryNode.attrib['revision']
        logentry['author'] = logentryNode.find('author').text
        logentry['date'] = logentryNode.find('date').text
        logentry['msg'] = logentryNode.find('msg').text
        pathsNode = logentryNode.find('paths')
        if pathsNode is not None:
            paths = []
            logentry['paths'] = paths
            for path_node in pathsNode.iterfind('path'):
                path = {}
                paths.append(path)
                path['#'] = path_node.text
                path['#prop-mods'] = True if path_node.attrib['prop-mods']=='true' else False
                path['#text-mods'] = True if path_node.attrib['text-mods']=='true' else False
                path['#kind'] = path_node.attrib['kind']
                path['#action'] = path_node.attrib['action']
    return ret

def removeNotVersioned(path):
    for line in execOutputSubCommand('status ' + path).splitlines():
        if len(line) > 0 and line[0] == '?':
            AOS.removePath(line[8:])

def propset(path, key, value):
    execSubCommand('propset svn:%s %s %s' % (key, value, path))

def propsetByTempFile(path, key, value):
    with AOS.TempFile(value) as f:
        execSubCommand('propset svn:%s -F %s %s' % (key, f.path, path))

def propsetExternals(dir, externalPairs):
    """
    设置dir下的子目录外联到其他地方
    :param dir: the externals to set on
    :param externalPairs: list of(subDir, externalDir[, 可选的版本号])
        externalDir可以是URL，也可以是工作拷贝中相对于dir的位置
    """
    value = ''
    for pair in externalPairs:
        if len(pair) == 3:
            value += '-r%s %s %s\n' % (pair[2], pair[1], pair[0])
        elif len(pair) == 2:
            value += '%s %s\n' % (pair[1], pair[0])
        else:
            raise SVN_Error("invalid externalPairs")

    propsetByTempFile(dir, 'externals', value)

def lock(filePath, message=None, userpass=None):
    """
    :except:
        SVN_AlreadyLockedError: if lock failure
    """
    cmd = 'lock'
    cmd += ' ' + filePath
    cmd += ' ' + makeMessageOptionStr(message)
    cmd += ' ' + makeUserPassOptionStr(userpass)
    result = execOutputSubCommand(cmd)
    if result[0:4] == 'svn:':
        if isURL(filePath):
            raise SVN_AlreadyLockedError(filePath, 'None', 'None', 'None')
        else:
            info = infoDict(filePath, userpass=userpass)['lock']
            raise SVN_AlreadyLockedError(filePath, info['owner'], info['comment'], info['created'])

def unlock(filePath, userpass=None):
    cmd = 'unlock'
    cmd += ' ' + filePath
    cmd += ' --force'
    cmd += ' ' + makeUserPassOptionStr(userpass)
    execSubCommand(cmd)

def move(src, dst, message=None, userpass=None):
    cmd = 'move'
    cmd += ' ' + src + ' ' + dst
    cmd += ' --force'
    cmd += ' --parents'
    cmd += ' ' + makeMessageOptionStr(message)
    cmd += ' ' + makeUserPassOptionStr(userpass)
    execSubCommand(cmd)

def branch(src, dst, message=None, revision=None, userpass=None):
    try:
        infoDict(dst)
        raise SVN_BranchDestinationAlreadyExistError(dst)
    except AOS.OS_SystemOutputError:
        pass

    cmd = 'copy ' + src + ' ' + dst
    cmd += ' ' + src + ' ' + dst
    cmd += ' --parents'
    cmd += ' ' + makeMessageOptionStr(message)
    cmd += ' ' + makeRevisionOptionStr(revision)
    cmd += ' ' + makeUserPassOptionStr(userpass)
    execSubCommand(cmd)

def rollback(path, revision):
    """
    rollback path changes made by commits in revision
    """
    if isinstance(revision, tuple) or isinstance(revision, list):
        startRevision = infoDict(path, revision[0])['#revision']
        endRevision = infoDict(path, revision[1])['#revision']
        if startRevision < endRevision:
            startRevision, endRevision = endRevision, startRevision
        revision = (startRevision, endRevision-1) if isinstance(revision, tuple) else [startRevision, endRevision-1]
    else:
        revision = infoDict(path, revision)['#revision']
        revision = '-%d' % revision

    cmd = 'merge '
    cmd += ' ' + makeRevisionOptionStr(revision)
    cmd += ' ' + path
    cmd += ' ' + path
    execSubCommand(cmd)
