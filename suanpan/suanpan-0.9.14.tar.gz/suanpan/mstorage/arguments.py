# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.arguments import Arg
from suanpan.mstorage import mstorage
from suanpan.utils import csv, json, npy, pickle


class MStorageArg(Arg):
    def __init__(self, *args, **kwargs):
        self.expire = kwargs.pop("expire", None)
        super(MStorageArg, self).__init__(*args, **kwargs)

    @property
    def isSet(self):
        return True

    def format(self, context):
        if self.value:
            self.value = self.getValue()
        return self.value

    def save(self, context, result):
        obj = result.value
        self.setValue(obj)
        self.logSaved(self.value)
        return self.value

    def getOutputTmpValue(self, *args):
        return "_".join(args)

    def getValue(self):
        raise NotImplementedError("Method not implemented!")

    def setValue(self, obj):
        raise NotImplementedError("Method not implemented!")


class Pickle(MStorageArg):
    def getValue(self):
        data = mstorage.mget(self.value)
        return pickle.loads(data)

    def setValue(self, obj):
        data = pickle.dumps(obj)
        return mstorage.set(self.value, data, expire=self.expire)


class Any(Pickle):
    pass


class Npy(MStorageArg):
    def getValue(self):
        data = mstorage.mget(self.value)
        params = json.loads(data["md"].decode())
        params["data"] = data["data"]
        return npy.loadjson(params)

    def setValue(self, obj):
        params = npy.dumpjson(obj)
        npybytes = params.pop("data")
        data = {"md": json.dumps(params), "data": npybytes}
        return mstorage.mset(self.value, data, expire=self.expire)


class Csv(Npy):
    def getValue(self):
        data = mstorage.get(self.value)
        return csv.loads(data)

    def setValue(self, dataframe):
        data = csv.dumps(dataframe)
        return mstorage.set(self.value, data, expire=self.expire)


class Table(Csv):
    pass
