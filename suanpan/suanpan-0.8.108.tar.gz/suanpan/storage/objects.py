# coding=utf-8
from __future__ import absolute_import, print_function

import abc
import functools
import os
import tempfile
import zipfile

from suanpan import path as spath
from suanpan.log import logger
from suanpan.objects import HasName


class Storage(HasName):
    __metaclass__ = abc.ABCMeta

    DEFAULT_IGNORE_KEYWORDS = ("__MACOSX", ".DS_Store")
    CONTENT_MD5 = "Content-MD5"
    PBAR_FORMAT = "{l_bar}{bar}"

    def __init__(
        self, delimiter=os.sep, tempStore=tempfile.gettempdir(), **kwargs
    ):  # pylint: disable=unused-argument
        self.delimiter = delimiter
        self.tempStore = tempStore

    @abc.abstractmethod
    def download(self, name, path, **kwargs):
        pass

    @abc.abstractmethod
    def upload(self, name, path, **kwargs):
        pass

    @abc.abstractmethod
    def copy(self, name, dist, **kwargs):
        pass

    @abc.abstractmethod
    def remove(self, name, **kwargs):
        pass

    @abc.abstractmethod
    def walk(self, folder, **kwargs):
        pass

    @abc.abstractmethod
    def listAll(self, folder, **kwargs):
        pass

    @abc.abstractmethod
    def listFolders(self, folder, **kwargs):
        pass

    @abc.abstractmethod
    def listFiles(self, folder, **kwargs):
        pass

    @abc.abstractmethod
    def isFolder(self, path, **kwargs):
        pass

    @abc.abstractmethod
    def isFile(self, path, **kwargs):
        pass

    def compress(self, zipFilePath, path, ignores=DEFAULT_IGNORE_KEYWORDS):
        compressFunc = self.compressFolder if os.path.isdir(path) else self.compressFile
        return compressFunc(zipFilePath, path, ignores=ignores)

    def compressFolder(self, zipFilePath, folderPath, ignores=DEFAULT_IGNORE_KEYWORDS):
        if folderPath in ignores:
            logger.info(
                "Ignore compressing folder: {} -> {}".format(folderPath, zipFilePath)
            )
            return zipFilePath

        logger.info("Compressing folder: {} -> {}".format(folderPath, zipFilePath))
        with zipfile.ZipFile(zipFilePath, "w") as zip:
            for root, _, files in os.walk(folderPath):
                for file in files:
                    filePath = os.path.join(root, file)
                    zip.write(
                        filePath, arcname=self.localRelativePath(filePath, folderPath)
                    )
        logger.info("Compressed folder: {} -> {}".format(folderPath, zipFilePath))
        return zipFilePath

    def compressFile(self, zipFilePath, filePath, ignores=DEFAULT_IGNORE_KEYWORDS):
        if filePath in ignores:
            logger.info(
                "Ignore compressing File: {} -> {}".format(filePath, zipFilePath)
            )
            return zipFilePath

        logger.info("Compressing File: {} -> {}".format(filePath, zipFilePath))
        with zipfile.ZipFile(zipFilePath, "w") as zip:
            _, filename = os.path.split(filePath)
            zip.write(filePath, arcname=filename)
        logger.info("Compressed File: {} -> {}".format(filePath, zipFilePath))
        return zipFilePath

    def extract(self, zipFilePath, distPath, ignores=DEFAULT_IGNORE_KEYWORDS):
        logger.info("Extracting zip: {} -> {}".format(zipFilePath, distPath))
        with zipfile.ZipFile(zipFilePath, "r") as zip:
            zip.extractall(distPath)
        self.removeIgnores(distPath, ignores=ignores)
        logger.info("Extracted zip: {} -> {}".format(zipFilePath, distPath))

    def getPathInTempStore(self, path, tempStore=None):
        tempStore = tempStore or self.tempStore
        return self.localPathJoin(tempStore, path)

    def completePath(self, path, delimiter=None):
        delimiter = delimiter or self.delimiter
        return path if path.endswith(delimiter) else path + delimiter

    def toLocalPath(self, path, delimiter=None):
        delimiter = delimiter or self.delimiter
        return path.replace(delimiter, os.sep)

    def toStoragePath(self, path, delimiter=None):
        delimiter = delimiter or self.delimiter
        return path.replace(os.sep, delimiter)

    def localPathJoin(self, *paths):
        path = os.path.join(*paths)
        return self.toLocalPath(path)

    def storagePathJoin(self, *paths):
        path = os.path.join(*[self.toLocalPath(path) for path in paths])
        return self.toStoragePath(path)

    def localRelativePath(self, path, base):
        return self._relativePath(path, base, delimiter=os.sep)

    def storageRelativePath(self, path, base, delimiter=None):
        delimiter = delimiter or self.delimiter
        return self._relativePath(path, base, delimiter=delimiter)

    def _relativePath(self, path, base, delimiter):
        base = base if base.endswith(delimiter) else base + delimiter
        return path[len(base) :] if path.startswith(base) else path

    @abc.abstractmethod
    def getStorageMd5(self, name, **kwargs):
        pass

    def getLocalMd5(self, path, **kwargs):  # pylint: disable=unused-argument
        return spath.md5(path) if os.path.isfile(path) else None

    def checkMd5(self, md5a, md5b, **kwargs):  # pylint: disable=unused-argument
        return md5a if md5a == md5b and md5a is not None else False

    @abc.abstractmethod
    def getStorageSize(self, name, **kwargs):  # pylint: disable=unused-argument
        pass

    def getLocalSize(self, path, **kwargs):  # pylint: disable=unused-argument
        return os.path.getsize(path)

    def storageUrl(self, path, **kwargs):  # pylint: disable=unused-argument
        return "storage://" + path

    def removeIgnores(self, path, ignores=None):
        ignores = ignores or self.DEFAULT_IGNORE_KEYWORDS

        def _ignore(_path):
            spath.remove(_path)
            logger.info("Removed ignored: {}".format(_path))
            return _path

        def _getIgnores(path):
            for root, folders, files in os.walk(path):
                for folder in folders:
                    if folder in ignores:
                        yield os.path.join(root, folder)
                for file in files:
                    if file in ignores:
                        yield os.path.join(root, file)

        return [_ignore(_path) for _path in _getIgnores(path)]

    def pathSplit(self, path, delimiter=None):
        delimiter = delimiter or self.delimiter
        return path.rsplit(delimiter, 1)

    def pathSplitExt(self, path, extDelimiter="."):
        return path.rsplit(extDelimiter, 1)

    def pbarRunner(self, pbar, quantity=1):
        def _dec(runner):
            @functools.wraps(runner)
            def _runner(*args, **kwargs):
                result = runner(*args, **kwargs)
                pbar.update(quantity)
                return result

            return _runner

        return _dec
