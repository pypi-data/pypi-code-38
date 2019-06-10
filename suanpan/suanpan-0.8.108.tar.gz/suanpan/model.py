# coding=utf-8
from __future__ import absolute_import, print_function

import os
import time

from suanpan.log import logger
from suanpan.storage import storage


class Model(object):
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

        self.download(self.version)

    @property
    def latestVersion(self):
        return max(
            int(folder.split(storage.delimiter)[-1])
            for folder in storage.listFolders(self.storagePath)
        )

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

        # TODO: No such version case

        self.download(version)
        return True
