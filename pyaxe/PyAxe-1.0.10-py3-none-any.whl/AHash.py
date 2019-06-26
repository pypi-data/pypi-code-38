import hashlib
from . import AOS


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
    m = hashlib.md5()
    _updateMD5ByFile(m, filePath)
    return m.hexdigest()


def getMD5OfDir(dirPath):
    m = hashlib.md5()
    for _, filePath in AOS.walkFiles(dirPath):
        _updateMD5ByFile(m, filePath)
    return m.hexdigest()
