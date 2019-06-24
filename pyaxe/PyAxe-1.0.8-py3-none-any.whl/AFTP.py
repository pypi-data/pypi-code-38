import os
import ftplib
import re
from . import ALog

ANONYMOUS_USERPASS = ('', '')


class FileStat:
    def __init__(self):
        self.isDir = False
        self.permissionBits = ''  #　'rwxrwxrwx'
        self.name = ''
        self.size = 0


def dir(host, targetDir='/', userpass=ANONYMOUS_USERPASS):
    ret = []

    def parseLine(line):
        """
        drwxr-xr-x 1 ftp ftp              0 Nov 02 15:47 TestDir
        -rw-r--r-- 1 ftp ftp              0 Nov 02 14:51 test.txt
        -rwxr-xr-x 1 ftp ftp        2943704 Aug 02  2016 cpuz_x32.exe
        -rw-r--r-- 1 ftp ftp      463451034 Jul 25  2016 exe_7v7_20160725_130231_master_a1b66ed_svn1206.rar
        """
        pattern = re.compile(r'([d\-])([r\-][w\-][x\-][r\-][w\-][x\-][r\-][w\-][x\-])\s+?1\s+?(.+?)\s+?(\d+)\s([a-zA-Z]{3}\s\d{2}\s+.+?)\s(.*)')
        result = pattern.match(line)
        dir, permissionBits, user_group, size, date, name = result.groups()

        stat = FileStat()
        stat.isDir = dir == 'd'
        stat.permissionBits = permissionBits
        stat.name = name
        stat.size = int(size)
        ret.append(stat)

    with ftplib.FTP(host) as ftp:
        ftp.login(userpass[0], userpass[1])
        ftp.cwd(targetDir)
        ftp.dir(parseLine)

    return ret


def upload(host, localFilePath, targetDir='/', userpass=ANONYMOUS_USERPASS):
    """
    本地文件上传到目标目录
    目标目录必须已经存在
    eg. upload('192.168.3.250', 'C:\\test\\a.txt', 'A/B') ==> A/B/a.txt
    """
    ALog.info('-=> ftp upload(%s, %s, %s)', host, localFilePath, targetDir)
    with ftplib.FTP(host) as ftp:
        ftp.login(userpass[0], userpass[1])
        ftp.cwd(targetDir)
        ftp.storbinary('STOR %s' % os.path.basename(localFilePath), open(localFilePath, 'rb'))


def download(host, targetFilePath, localDir='.', userpass=ANONYMOUS_USERPASS):
    """
    目标文件下载到本地目录
    本地目录必须已经存在
    """
    ALog.info('-=> ftp download(%s, %s, %s)', host, targetFilePath, localDir)
    targetDir = os.path.dirname(targetFilePath)
    targetFileName = os.path.basename(targetFilePath)
    with ftplib.FTP(host) as ftp:
        ftp.login(userpass[0], userpass[1])
        ftp.cwd(targetDir)
        ftp.retrbinary('RETR %s' % targetFileName, open(os.path.join(localDir, targetFileName), 'wb').write)


def moveFile(host, srcPath, dstPath, userpass=ANONYMOUS_USERPASS):
    """
    把文件从源路径移到目标路径
    """
    ALog.info('-=> ftp move(%s, %s, %s)', host, srcPath, dstPath)
    with ftplib.FTP(host) as ftp:
        ftp.login(userpass[0], userpass[1])
        ftp.rename(srcPath, dstPath)


def isDir(host, path, userpass=ANONYMOUS_USERPASS):
    """
    目标目录是否存在于FTP
    """
    try:
        with ftplib.FTP(host) as ftp:
            ftp.login(userpass[0], userpass[1])
            ftp.cwd(path)
            return True
    except:
        return False


def isFile(host, path, userpass=ANONYMOUS_USERPASS):
    """
    目标文件是否存在于FTP
    """
    targetDir = os.path.dirname(path)
    targetName = os.path.basename(path)
    try:
        files = dir(host, targetDir, userpass)
    except:
        return False
    for file in files:
        if not file.isDir and file.name == targetName:
            return True
    return False


def exists(host, path, userpass=ANONYMOUS_USERPASS):
    """
    目标是否存在于FTP
    """
    return isDir(host, path, userpass) or isFile(host, path, userpass)
