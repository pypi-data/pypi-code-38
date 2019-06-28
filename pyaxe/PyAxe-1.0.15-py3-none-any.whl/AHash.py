import os, hashlib
from . import AOS, AError

class Hash_Error(AError.Error):
    pass


def _updateByFile(m, filePath):
        with open(filePath, 'rb') as fp:
            while True:
                bytes = fp.read(8192)
                if not bytes:
                    break
                m.update(bytes)


class Hasher:
    def __init__(self, cls):
        self.cls = cls

    def ofBuffer(self, buffer):
        m = self.cls()
        m.update(buffer)
        return m.hexdigest()

    def ofStr(self, s):
        return self.ofBuffer(s.encode('UTF-8'))

    def ofFile(self, filePath):
        if not os.path.isfile(filePath):
            raise Hash_Error("%s is not file" % filePath)
        m = self.cls()
        _updateByFile(m, filePath)
        return m.hexdigest()

    def ofDir(self, dirPath):
        if not os.path.isdir(dirPath):
            raise Hash_Error("%s is not dir" % dirPath)
        m = self.cls()
        for _, filePath in AOS.walkFiles(dirPath):
            _updateByFile(m, filePath)
        return m.hexdigest()


MD5Hasher = Hasher(hashlib.md5)
getMD5OfStr = MD5Hasher.ofStr
getMD5OfFile = MD5Hasher.ofFile
getMD5OfDir = MD5Hasher.ofDir
