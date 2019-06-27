import os, hashlib
from . import AOS, AError

class Hash_Error(AError.Error):
    pass


def _updateMD5ByFile(m, filePath):
    with open(filePath, 'rb') as fp:
        while True:
            bytes = fp.read(8192)
            if not bytes:
                break
            m.update(bytes)


def getMD5OfStr(s):
    m = hashlib.md5()
    m.update(s)
    return m.hexdigest()


def getMD5OfFile(filePath):
    if not os.path.isfile(filePath):
        raise Hash_Error("%s is not file" % filePath)
    m = hashlib.md5()
    _updateMD5ByFile(m, filePath)
    return m.hexdigest()


def getMD5OfDir(dirPath):
    if not os.path.isdir(dirPath):
        raise Hash_Error("%s is not dir" % dirPath)
    m = hashlib.md5()
    for _, filePath in AOS.walkFiles(dirPath):
        _updateMD5ByFile(m, filePath)
    return m.hexdigest()
