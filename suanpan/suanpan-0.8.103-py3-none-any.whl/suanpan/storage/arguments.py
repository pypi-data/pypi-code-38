# coding=utf-8
from __future__ import absolute_import, print_function

import numpy as np
from sklearn.externals import joblib

from suanpan import path
from suanpan.arguments import Arg
from suanpan.components import Result
from suanpan.storage import storage
from suanpan.utils import csv, json


class StorageArg(Arg):
    def getOutputTmpValue(self, *args):
        return storage.delimiter.join(args)


class File(StorageArg):
    FILENAME = "file"
    FILETYPE = None

    def __init__(self, key, **kwargs):
        fileName = kwargs.pop("name", self.FILENAME)
        fileType = kwargs.pop("type", self.FILETYPE)
        self.fileName = (
            "{}.{}".format(fileName, fileType.lower()) if fileType else fileName
        )
        self.objectPrefix = None
        self.objectName = None
        self.filePath = None
        super(File, self).__init__(key, **kwargs)

    @property
    def isSet(self):
        return True

    def load(self, args):
        self.objectPrefix = super(File, self).load(args)
        if self.objectPrefix:
            self.objectName = storage.storagePathJoin(self.objectPrefix, self.fileName)
            self.filePath = storage.getPathInTempStore(self.objectName)
            path.safeMkdirsForFile(self.filePath)
        self.value = self.filePath
        return self.filePath

    def format(self, context):
        if self.filePath:
            storage.download(self.objectName, self.filePath)
        return self.filePath

    def clean(self, context):
        if self.filePath:
            path.remove(self.filePath)
        return self.filePath

    def save(self, context, result):
        filePath = result.value
        storage.upload(self.objectName, filePath)
        self.logSaved(self.objectName)
        return self.objectPrefix


class Folder(StorageArg):
    def __init__(self, key, **kwargs):
        super(Folder, self).__init__(key, **kwargs)
        self.folderName = None
        self.folderPath = None

    @property
    def isSet(self):
        return True

    def load(self, args):
        self.folderName = super(Folder, self).load(args)
        if self.folderName:
            self.folderPath = storage.getPathInTempStore(self.folderName)
        if self.folderPath:
            path.safeMkdirs(self.folderPath)
        self.value = self.folderPath
        return self.folderPath

    def format(self, context):
        if self.folderPath:
            storage.download(self.folderName, self.folderPath)
        return self.folderPath

    def clean(self, context):
        if self.folderPath:
            path.empty(self.folderPath)
        return self.folderPath

    def save(self, context, result):
        folderPath = result.value
        storage.upload(self.folderName, folderPath)
        self.logSaved(self.folderName)
        return self.folderName


class Data(File):
    FILENAME = "data"


class Json(Data):
    FILETYPE = "json"

    def format(self, context):
        super(Json, self).format(context)
        if self.filePath:
            self.value = json.load(self.filePath)
        return self.value

    def save(self, context, result):
        json.dump(result.value, self.filePath)
        return super(Json, self).save(context, Result.froms(value=self.filePath))


class Csv(Data):
    FILETYPE = "csv"

    def format(self, context):
        super(Csv, self).format(context)
        if self.filePath:
            self.value = csv.load(self.filePath)
        return self.value

    def save(self, context, result):
        csv.dump(result.value, self.filePath)
        return super(Csv, self).save(context, Result.froms(value=self.filePath))


class Table(Csv):
    pass


class Npy(Data):
    FILETYPE = "npy"

    def format(self, context):
        super(Npy, self).format(context)
        if self.filePath:
            self.value = np.load(self.filePath)
        return self.value

    def save(self, context, result):
        np.save(self.filePath, result.value)
        return super(Npy, self).save(context, Result.froms(value=self.filePath))


class Model(File):
    FILENAME = "model"


class H5Model(Model):
    FILETYPE = "h5"


class Checkpoint(Model):
    FILETYPE = "ckpt"


class JsonModel(Model):
    FILETYPE = "json"


class SklearnModel(Model):
    FILETYPE = "model"

    def format(self, context):
        super(SklearnModel, self).format(context)
        if self.filePath:
            self.value = joblib.load(self.filePath)

        return self.value

    def save(self, context, result):
        joblib.dump(result.value, self.filePath)

        return super(SklearnModel, self).save(
            context, Result.froms(value=self.filePath)
        )
