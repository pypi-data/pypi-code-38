import os
import zipfile
import tarfile
from . import ALog

__all__ = ['zip', 'unzip', 'untar', 'tar']


def zip(dir, zipPath, keepTopDir=True):
    """
    :param keepTopDir: 是否在压缩包中保留顶层目录
    """
    ALog.info('-=> zip(%s, %s)', dir, zipPath)
    dirName = os.path.basename(os.path.normpath(dir))
    skipLen = (len(dir)-len(dirName)) if keepTopDir else len(dir)+1
    zipObj = zipfile.ZipFile(zipPath, 'w', zipfile.zlib.DEFLATED)
    for root, dirs, files in os.walk(dir):
        for name in files:
            path = os.path.join(root, name)
            zipObj.write(path, path[skipLen:])
    zipObj.close()

def unzip(zipPath, dir='.'):
    ALog.info('-=> unzip(%s, %s)', zipPath, dir)
    if not os.path.exists(dir):
        os.makedirs(dir)
    zipObj = zipfile.ZipFile(zipPath)
    for name in zipObj.namelist():
        name = name.replace('\\', '/')
        if name.endswith('/'):
            extDir = os.path.join(dir, name)
            if not os.path.exists(extDir):
                os.makedirs(extDir)
        else:
            extFileName = os.path.join(dir, name)
            extDir = os.path.dirname(extFileName)
            if not os.path.exists(extDir):
                os.makedirs(extDir)
            outfile = open(extFileName, 'wb')
            outfile.write(zipObj.read(name))
            outfile.close()


def tar(dir, tarPath, mode='gz', keepTopDir=True):
    """
    :param keepTopDir: 是否在压缩包中保留顶层目录
    """
    ALog.info('-=> tar(%s, %s, %s)', dir, tarPath, mode)
    dirName = os.path.basename(os.path.normpath(dir))
    skipLen = (len(dir)-len(dirName)) if keepTopDir else len(dir)+1
    tarObj = tarfile.open(tarPath, 'w:%s' % mode)
    for root, dirs, files in os.walk(dir):
        for name in files:
            path = os.path.join(root, name)
            tarObj.add(path, path[skipLen:])
    tarObj.close()

def untar(tarPath, dir='.', mode='gz'):
    ALog.info('-=> untar(%s, %s, %s)', tarPath, dir, mode)
    tarObj = tarfile.open(tarPath, 'r:%s' % mode)
    fileNames = tarObj.getnames()
    for fileName in fileNames:
        tarObj.extract(fileName, dir)
    tarObj.close()
    
