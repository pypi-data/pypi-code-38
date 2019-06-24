import os
import io
import sys
import subprocess
import shlex
import locale
import tempfile
from . import ALog
from . import AError

PY_HOME = os.path.dirname(sys.executable)

if os.name == 'nt':    
    PY3_COMMAND = 'py -3'    
    EXE_EXT = '.exe'
    EXE_CALL_PREFIX = ''
else:
    PY3_COMMAND = 'python3'
    EXE_EXT = ''
    EXE_CALL_PREFIX = './'


class OS_Error(AError.Error):
    pass


class OS_PathError(OS_Error):
    pass


class OS_DecorateLockError(OS_Error):
    pass


class OS_SystemError(OS_Error):
    def __init__(self, cmd, retCode):
        self.cmd = cmd
        self.retCode = retCode

    def __str__(self):
        return 'os.system(%s) return error(%d)' % (self.cmd, self.retCode)


class OS_SystemOutputError(OS_Error):
    def __init__(self, cmd, retCode, output):
        self.cmd = cmd
        self.retCode = retCode
        self.output = output

    def __str__(self):
        return 'subprocess.check_output(%s) return error(%d): %s' % (self.cmd, self.retCode, self.output)


class OS_ProcessError(OS_Error):
    def __init__(self, cmd, retCode):
        self.cmd = cmd
        self.retCode = retCode

    def __str__(self):
        return 'subprocess(%s) return error(%d)' % (self.cmd, self.retCode)


class ChangeDir:
    def __init__(self, target, echo=True):
        self.old_cwd = os.getcwd()
        self.target = target
        self.echo = echo

    def __enter__(self):
        if self.echo:
            ALog.info('>>> cd ' + self.target)
        os.chdir(self.target)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.echo:
            ALog.info('>>> cd ' + self.old_cwd)
        os.chdir(self.old_cwd)


class AddEnvPath:
    def __init__(self, path, first=True):
        """path可以是字符串或者字符串列表"""
        self.oldEnvPath = os.environ['PATH']
        self.path = [path] if isinstance(path, str) else path
        self.first = first

    def __enter__(self):
        separator = ';' if os.name == 'nt' else ':'
        
        pathStr = separator.join(self.path)
        
        if self.first:
            os.environ['PATH'] = pathStr + separator + self.oldEnvPath
        else:
            if self.oldEnvPath.endswith(separator):
                os.environ['PATH'] = self.oldEnvPath + pathStr
            else:
                os.environ['PATH'] = self.oldEnvPath + separator + pathStr

        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        os.environ['PATH'] = self.oldEnvPath


class AddSysPath:
    def __init__(self, path, first=True):
        """path可以是字符串或者字符串列表"""
        self.path = [path] if isinstance(path, str) else path
        self.first = first

    def __enter__(self):
        if self.first:
            reversePath = self.path.copy()
            reversePath.reverse()
            for path in reversePath:
                sys.path.insert(0, path)
        else:
            for path in self.path:
                sys.path.append(path)
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.first:
            for i in range(len(self.path)):
                sys.path.pop(0)
        else:
            for i in range(len(self.path)):
                sys.path.pop()


class TempFile:
    def __init__(self, content, echo=True):
        self.content = content
        self.echo = echo
        self.fp = None

    def __enter__(self):
        self.fp = tempfile.NamedTemporaryFile('w', delete=False)
        if self.echo:
            ALog.info('>>> write to temp file %s:\n%s' % (self.fp.name, self.content))
        self.fp.write(self.content)
        self.fp.close()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.echo:
            removeFile(self.path)
        else:
            os.remove(self.path)

    @property
    def path(self):
        return self.fp.name


def fixPathArg(path):
    """防止路径出现特殊符号，如‘空格’ ‘-’ 等，导致执行命令行失败"""
    if os.name == 'nt':
        if path.startswith('"') or path.endswith('"'):
            return path
        return '"' + path + '"'
    else:
        return path.replace(' ', '\\ ')


def system(cmd, echo=True, nullout=False):
    def fixRetCode(code):
        if os.name != 'nt':
            # 在Unix上，os.system返回值是一个16位整数，其中高8位为目标退出码（参考os.wait）
            return code >> 8  # 最终限制在0~255，比如目标返回-1，这里转换为255，-2转换为254...
        else:
            return code  # 没有任何限制，原封不动的返回目标退出码

    if nullout:
        if os.name == 'nt':
            cmd += ' 1>nul 2>&1'
        else:
            cmd += ' 1>/dev/null 2>&1'

    if echo:
        ALog.info('>>> ' + cmd)

    code = fixRetCode(os.system(cmd))
    if code == 0:
        return
    raise OS_SystemError(cmd, code)


def process(cmd, encoding=None, shell=False):
    ALog.info('>>> ' + cmd)
    args = cmd if (os.name == 'nt' or shell) else shlex.split(cmd)

    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell) as pipe:
        ioWrapper = io.TextIOWrapper(pipe.stdout, encoding=encoding)
        while True:
            out = ioWrapper.read(1)
            code = pipe.poll() # A None value indicates that the process hasn’t terminated yet.
            if out == '' and code != None:
                if code:  # None-Zero means error happens, subprocess不需要fixRetCode（其内部已经修正过）
                    raise OS_ProcessError(cmd, code)
                else:
                    break

            if out != '':
                with ALog.getLogFileObjectForAppend() as fp:
                    fp.write(out)
                sys.stdout.write(out)


def systemOutput(cmd, encoding=None, shell=False):
    """
    Execute command and return it's output
    raise Os_SystemOutputError on failure
    """
    if encoding is None:
        encoding = locale.getpreferredencoding(False)

    try:
        return subprocess.check_output(cmd if (os.name == 'nt' or shell) else shlex.split(cmd),
                                       stderr=subprocess.STDOUT,
                                       shell=shell).decode(encoding)
    except subprocess.CalledProcessError as e:
        raise OS_SystemOutputError(cmd, e.returncode, e.output.decode(encoding))


def removeFile(file):
    """
    :param file: 可以为普通文件或符号链接，也可包含通配符
    注意：若为只读文件或者Windows上的隐藏文件，需先将只读或隐藏属性去掉
    - Windows上用 attrib -r -h <file>
    - *nix上用 chmod
    """
    if not (os.path.isfile(file) or os.path.islink(file) or ('*' in file) or ('?' in file)):
        return

    file = os.path.normpath(file)

    if os.name == 'nt':
        try:
            system('del /f/q ' + fixPathArg(file))
        except OS_SystemError as e:
            ALog.info('"%s" failed, remove readonly & hidden attribute, then retry' % e.cmd)
            system('attrib -r -h ' + fixPathArg(file))  # 去掉只读和隐藏属性
            system('del /f/q ' + fixPathArg(file))
    else:
        system('rm -rf ' + fixPathArg(file))


def removeDir(dir):
    """
    注意：若为只读目录或者Windows上的隐藏目录，需先将只读或隐藏属性去掉
    - Windows上用 cd <dir> && attrib -r -h /d /s
    - *nix上用 chmod -R

    另外Windows不支持通配符
    """
    if not (os.path.isdir(dir) or ('*' in dir) or ('?' in dir)):
        return

    dir = os.path.normpath(dir)

    if os.name == 'nt':
        try:
            system('rd /s/q ' + fixPathArg(dir))
        except OS_SystemError as e:
            ALog.info('"%s" failed, remove readonly & hidden attribute, then retry' % e.cmd)
            with ChangeDir(dir):
                system('attrib -r -h /d /s')  # 去掉只读和隐藏属性
            system('rd /s/q ' + fixPathArg(dir))
    else:
        system('rm -rf ' + fixPathArg(dir))


def removePath(path):
    if os.path.isdir(path):
        removeDir(path)
    else:
        removeFile(path)


def makeDir(dir):
    """
    :param dir: 可包含中间目录
    """
    if not dir:
        return

    if os.path.exists(dir):
        return

    dir = os.path.normpath(dir)

    if os.name == 'nt':
        system('md ' + fixPathArg(dir))
    else:
        system('mkdir -p ' + fixPathArg(dir))


def remakeDir(dir):
    removeDir(dir)
    makeDir(dir)


def ensureFileDir(filePath):
    """确保文件所在目录已经被创建"""
    dirname = os.path.dirname(filePath)
    if dirname:
        makeDir(dirname)


def copyFile(src, dst):
    """
    拷贝一个或多个文件到另一个位置
    :param src: 一个或多个（包含通配符）文件
    :param dst: 目录或文件名（如果是目录，必须保证目录已存在）
    """

    src = os.path.normpath(src)
    dst = os.path.normpath(dst)

    if os.name == 'nt':
        system('copy /y %s %s' % (fixPathArg(src), fixPathArg(dst)))
    else:
        system('cp -P %s %s' % (fixPathArg(src), fixPathArg(dst)))  # -P 保持符号链接


def copyDir(srcDir, dstDir, excludes=None):
    """
    Copy all the files(include symbolic) from source directory to destination directory.
    If target directory does not exist, then create one.
    :param srcDir: the source directory
    :param dstDir: the destination directory
    :param excludes: if not None, must be str/tuple/list; files with the given pattern list in excludes will not be copied
        use 'xxx/' to specify a dir pattern
    """
    def _copyDirByPatterns(srcDir, dstDir, patterns):
        """递归删除目录下满足patterns的文件或者目录"""
        def match(name, patterns):
            for pattern in patterns:
                if pattern in name:
                    return True
            return False

        for name in os.listdir(srcDir):
            srcPath = os.path.join(srcDir, name)
            dstPath = os.path.join(dstDir, name)

            checkPath = srcPath
            if os.path.isdir(srcPath):
                checkPath += os.sep
                makeDir(dstPath)

            if not match(checkPath, patterns):
                if os.path.isdir(srcPath):
                    _copyDirByPatterns(srcPath, dstPath, patterns)
                elif os.path.isfile(srcPath):
                    copyFile(srcPath, dstPath)
                else:
                    pass

    if isinstance(excludes, str):
        excludes = (excludes,)

    srcDir = os.path.normpath(srcDir)
    dstDir = os.path.normpath(dstDir)

    if os.name == 'nt':
        if excludes is None:
            system('xcopy %s\\* %s /r/i/c/k/h/e/q/y' % (fixPathArg(srcDir), fixPathArg(dstDir)))
        else:
            fp = tempfile.NamedTemporaryFile('w', delete=False)
            fp.writelines('\n'.join(excludes))
            fp.close()
            system('xcopy %s\\* %s /r/i/c/k/h/e/q/y/exclude:%s' % (fixPathArg(srcDir), fixPathArg(dstDir), fp.name))
            os.remove(fp.name)
    else:
        makeDir(dstDir)
        if excludes is None:
            system('cp -R %s/* %s' % (fixPathArg(srcDir), fixPathArg(dstDir)))
        else:
            _copyDirByPatterns(srcDir, dstDir, excludes)


def copyFilesInDir(srcDir, dstDir, fileMatchRule=None):
    """
    把srcDir中满足条件的文件拷贝至dstDir对应的位置（对应目录自动创建）
    """
    for fileName in os.listdir(srcDir):
        srcPath = os.path.join(srcDir, fileName)
        dstPath = os.path.join(dstDir, fileName)

        if os.path.isfile(srcPath):
            if fileMatchRule is None or fileMatchRule(fileName, srcPath):
                makeDir(dstDir)
                copyFile(srcPath, dstPath)
        elif os.path.isdir(srcPath):
            copyFilesInDir(srcPath, dstPath, fileMatchRule)


def move(src, dst):
    """
    [文件 -> 文件]：若目标已存在，则直接覆盖之
    假设a.txt内容为a，b.txt内容为b
    move b a ==> a.txt内容为b，b.txt被删除

    [目录 -> 目录]: 若目标目录已存在，则源目录直接搬移到目标目录内
    a/a.txt
    b/b.txt
    move b a ==>
        a/a.txt
        a/b/b.txt

    a/a.txt
    b/a/b.txt
    move b/a a ==>
        a/a.txt
        a/b/a/b.txt

    move b/a . ==>
        Windows：拒绝访问
        Linux：mv: cannot move ‘b/a’ to ‘./a’: File exists
    """
    src = os.path.normpath(src)
    dst = os.path.normpath(dst)

    if os.name == 'nt':
        system('move /y %s %s' % (fixPathArg(src), fixPathArg(dst)))
    else:
        system('mv -f %s %s' % (fixPathArg(src), fixPathArg(dst)))


def moveContentsToDir(srcDir, dstDir):
    """把源目录中所有内容移到目标目录中"""
    if not os.path.isdir(srcDir):
        raise OS_PathError('src(%s) not dir' % srcDir)
    if not os.path.isdir(dstDir):
        raise OS_PathError('dst(%s) not dir' % dstDir)
    for file in os.listdir(srcDir):
        move(os.path.join(srcDir, file), dstDir)


def makeLink(src, link, soft=True, force=False):
    """
    :param force 删除已存在的链接
    """
    src = os.path.normpath(src)
    link = os.path.normpath(link)

    if os.name == 'nt':
        cmd = 'mklink'
        options = ''
        if os.path.isdir(src):
            options += '/d'
        if not soft:
            options += '/h'
        if force and os.path.islink(link):
            if os.path.isfile(src):
                removeFile(link)
            elif os.path.isdir(src):
                raise NotImplementedError('TODO删除目录的软链接')
        if options != '':
            cmd += ' ' + options
        cmd += ' %s %s' % (fixPathArg(link), fixPathArg(src))
        system(cmd)
    else:
        cmd = 'ln'
        if soft:
            cmd += ' -s'
        if force:
            cmd += ' -f'
        cmd += ' %s %s' % (fixPathArg(src), fixPathArg(link))
        system(cmd)


def walkFiles(dir, fileMatchRule=None):
    """
    递归列出目录dir所有满足fileMatchRule的文件名和路径
    fileMatchRule(fileName, filePath)是一个布尔值的函数
    """
    for parentDirPath, dirNames, fileNames in os.walk(dir):
        for fileName in fileNames:
            filePath = os.path.join(parentDirPath, fileName)
            if fileMatchRule is None or fileMatchRule(fileName, filePath):
                yield fileName, filePath


def walkDirs(dir, dirMatchRule=None):
    """
    递归列出目录dir所有满足dirMatchRule的目录名和路径
    dirMatchRule(dirName, dirPath)是一个布尔值的函数
    """
    for parentDirPath, dirNames, fileNames in os.walk(dir):
        for dirName in dirNames:
            dirPath = os.path.join(parentDirPath, dirName)
            if dirMatchRule is None or dirMatchRule(dirName, dirPath):
                yield dirName, dirPath


def dirDiff(srcDir, dstDir, excludes=None):
    """
    比较两个目录的结构差异
    :return 返回srcDir比dstDir多出的目录和文件路径列表(diffDirs, diffFiles), 注意多出目录内的内容不会列出来
    srcDir比dstDir少的部分可以通过反向比较获得
    """
    def match(name, patterns):
        for pattern in patterns:
            if pattern in name:
                return True
        return False

    def _dirDiff(srcDir, dstDir, diffDirs, diffFiles, excludes):
        for fileName in os.listdir(srcDir):
            srcPath = os.path.join(srcDir, fileName)
            dstPath = os.path.join(dstDir, fileName)

            checkPath = srcPath
            if os.path.isdir(srcPath):
                checkPath += os.sep

            if os.path.isdir(srcPath):
                if not os.path.isdir(dstPath):
                    if excludes is None or not match(checkPath, excludes):
                        diffDirs.append(srcPath)
                else:
                    _dirDiff(srcPath, dstPath, diffDirs, diffFiles, excludes)
            elif os.path.isfile(srcPath):
                if not os.path.isfile(dstPath):
                    if excludes is None or not match(checkPath, excludes):
                        diffFiles.append(srcPath)
            else:
                pass

    if isinstance(excludes, str):
        excludes = (excludes,)

    diffDirs=[]
    diffFiles=[]
    _dirDiff(srcDir, dstDir, diffDirs, diffFiles, excludes)
    return diffDirs, diffFiles


class decorate_lock:
    """
    为func的执行加锁（目前仅支持文件锁）
    若加锁失败，则抛出OS_DecorateWithLockError异常
    """
    def __init__(self, lockStrategy):
        self.lockStrategy = lockStrategy

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            self.lockStrategy.lock()
            try:
                return func(*args, **kwargs)
            finally:
                self.lockStrategy.unlock()

        return wrapper

    class FileLockStrategy:
        class LockError(OS_DecorateLockError):
            def __init__(self, lockFile):
                self.lockFile = lockFile

            def __str__(self):
                return 'Failed to get lock from file(%s)' % self.lockFile

        def __init__(self, filePath):
            self.filePath = filePath
            self.fp = None

        def lock(self):
            if os.path.exists(self.filePath):
                try:
                    os.remove(self.filePath)
                except Exception:
                    raise self.__class__.LockError(self.filePath)

            self.fp = open(self.filePath, 'w')

        def unlock(self):
            self.fp.close()
            removeFile(self.filePath)
