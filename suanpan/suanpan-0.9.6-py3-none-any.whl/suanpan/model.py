# coding=utf-8
from __future__ import absolute_import, print_function

import os
import time

from suanpan.log import logger
from suanpan.storage import storage


class ModelLoader(object):
    def __init__(self, storagePath, version="latest"):
        self.storagePath = storagePath
        self.localPath = storage.getPathInTempStore(self.storagePath)
        self.initVersion = version

        self.useLatestVersion = self.initVersion == "latest"
        if not self.useLatestVersion:
            logger.info(
                "Model is set to use a specific version: {}, model reload will not be necessary".format(
                    self.initVersion
                )
            )

        self.version = self.latestVersion if self.useLatestVersion else self.initVersion

        self.path = None
        self.updatedTime = None

        self.download(self.version)

    @property
    def latestVersion(self):
        return max(self.allVersions)

    @property
    def allVersions(self):
        return [
            int(folder.split(storage.delimiter)[-1])
            for folder in storage.listFolders(self.storagePath)
        ]

    def overdue(self, duration):
        return time.time() - self.updatedTime >= duration

    def download(self, version=None):
        version = self.version
        versionString = str(version)
        storagePath = storage.storagePathJoin(self.storagePath, versionString)
        localPath = storage.localPathJoin(self.localPath, versionString)

        if not os.path.isdir(localPath):
            storage.download(storagePath, localPath)

        self.updatedTime = time.time()
        self.version = version
        self.path = localPath

        return self.path

    def reload(self, duration=None):
        if not self.useLatestVersion:
            logger.info(
                "Model is set to use a specific version: {}, model reload is disabled".format(
                    self.initVersion
                )
            )
            return False

        if duration and not self.overdue(duration):
            logger.info("Model reload is not overdue, interval: {}s".format(duration))
            return False

        latestVersion = self.latestVersion
        if latestVersion <= self.version:
            logger.info("No new model(s) found, version: {}".format(self.version))
            return False

        logger.info("New model(s) found, use latest version: {}".format(latestVersion))
        self.download(latestVersion)
        return True

    def reset(self, version):
        if version == self.version:
            logger.info("No need to reset, version matched: {}".format(self.version))
            return False

        if version not in self.allVersions:
            raise Exception("The version: {} specified is not a valid model version")

        self.download(version)
        return True


class Model(object):
    def __init__(self, *args, **kwargs):
        self.loader = ModelLoader(*args, **kwargs)
        self.load(self.path)

    @property
    def version(self):
        return self.loader.version

    @property
    def latestVersion(self):
        return self.loader.latestVersion

    @property
    def path(self):
        return self.loader.path

    def reload(self, duration=None):
        if self.loader.reload(duration=duration):
            self.load(self.path)

    def load(self, path):
        raise NotImplementedError("Method not implemented!")

    def predict(self, features):
        raise NotImplementedError("Method not implemented!")
