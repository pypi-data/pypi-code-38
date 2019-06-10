# coding=utf-8
from __future__ import absolute_import, division, print_function

import os
import tempfile

from suanpan import path as spath
from suanpan.log import logger
from suanpan.storage.objects import Storage


class LocalStorage(Storage):
    def __init__(self, localTempStore=tempfile.gettempdir(), **kwargs):
        super(LocalStorage, self).__init__(
            delimiter=os.sep, tempStore=localTempStore, **kwargs
        )

    def download(self, name, path):
        logger.info(
            "Downloading: {} -> {} - ({}) Nothing to do!".format(
                self.storageUrl(name), path, self.name
            )
        )
        return self.getPathInTempStore(path)

    def upload(self, name, path):
        logger.info(
            "Uploading: {} -> {} - ({}) Nothing to do!".format(
                self.storageUrl(name), path, self.name
            )
        )
        return path

    def copy(self, path, dist):
        pathUrl = self.storageUrl(path)
        distUrl = self.storageUrl(dist)
        logger.info("Copying: {} -> {}".format(pathUrl, distUrl))
        _path = self.getPathInTempStore(path)
        _dist = self.getPathInTempStore(dist)
        spath.ccopy(_path, _dist)
        logger.info("Copied: {} -> {}".format(pathUrl, distUrl))
        return dist

    def remove(self, path):
        spath.cremove(self.getPathInTempStore(path))
        logger.info("Removed: {}".format(self.storageUrl(path)))
        return path

    def walk(self, folderName):
        root = self.getPathInTempStore(folderName)
        return os.walk(root)

    def listAll(self, folderName):
        root = self.getPathInTempStore(folderName)
        return (self.storagePathJoin(root, p) for p in os.listdir(root))

    def listFolders(self, folderName):
        return (p for p in self.listAll(folderName) if os.path.isdir(p))

    def listFiles(self, folderName):
        return (p for p in self.listAll(folderName) if os.path.isfile(p))

    def isFolder(self, folderName):
        folder = self.getPathInTempStore(folderName)
        return os.path.isdir(folder)

    def isFile(self, objectName):
        file = self.getPathInTempStore(objectName)
        return os.path.isfile(file)

    def storagePathJoin(self, *paths):
        return self.localPathJoin(*paths)

    def storageRelativePath(self, path, base):
        return self.localRelativePath(path, base)

    def storageUrl(self, path):
        return "file://" + self.getPathInTempStore(path)

    def getStorageMd5(self, objectName):
        return self.getLocalMd5(self.getPathInTempStore(objectName))

    def getStorageSize(self, objectName):
        return self.getLocalSize(self.getPathInTempStore(objectName))
