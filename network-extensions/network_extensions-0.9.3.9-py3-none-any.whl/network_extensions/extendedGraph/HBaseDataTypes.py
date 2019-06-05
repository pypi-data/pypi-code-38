import bz2
import uuid
from collections import defaultdict
#from memory_profiler import profile
import redis
import json
import pickle

from bz2 import BZ2Compressor,BZ2Decompressor
import happybase
CACHE = 0
HBASE_MODE = 1
HBASE  = happybase.Connection('localhost',table_prefix="GEN_GRAPH")
class RedisConnect:

    instance = None
    class __rc:
        def __init__(self):
            #self.redis = HBASE
            self.uuid = uuid.uuid4().urn
            self.dictCache = defaultdict(dict)
            self.listCache = defaultdict(list)
            self.valueCache = {}
            self.mode = HBASE_MODE
            self.HBASE = HBASE
        def saveCaches(self):
            print("SAVE CACHES (DICT %s, LIST %s, VALUES %s)"%(len(self.dictCache),len(self.listCache),len(self.valueCache)))

            for k,cache_dict in self.dictCache.items():

                if isinstance(cache_dict,dict):

                    table = self.HBASE.table(k)
                    for k,v in table.s
                    pipe.hmset(k,cache_dict)
                else: #is already a key
                    pipe.set(k,cache_dict)
            self.dictCache = defaultdict(dict)
            for k,cache_list in self.listCache.items():
                for cl in cache_list:
                    pipe.lpush(k,cl)
            self.listCache = defaultdict(list)
            for k,value in self.valueCache.items():
                pipe.set(k,value)
            self.valueCache = {}


        def deleteCaches(self):
            self.dictCache = defaultdict(dict)
            self.listCache = defaultdict(list)
            self.valueCache = {}




    def __init__(self):
        if not RedisConnect.instance:
            RedisConnect.instance = RedisConnect.__rc()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def __setattr__(self, name, value):
        return setattr(self.instance, name, value)





class RedisBase(object):
    def __init__(self):
        self.redis = RedisConnect().redis
        self.caches = RedisConnect()
        #self.mode = mode

    def start_pipeline(self):
        RedisConnect().start_pipeline()

    def execute(self,reset=False):
        RedisConnect().execute(reset=reset)

    def setMode(self,mode):
        self.caches.mode = mode

    @property
    def mode(self):
        return self.caches.mode


class RList(RedisBase):
    """
    List Struktur saved in redis
    """

    def __init__(self,values=None,key_int=None,valueFunc=lambda x:x):
        """

        :param values: Initial list can be empty
        :param key_int: If set then RList will connect to an existing structure in redis if None then a new key will be generated
        :param valueFunc: function which shall be applied when a value is returned from the list, normally the return value is of type bytes
        :param mode: REDIS_MODE or CACHE
        """
        RedisBase.__init__(self)
        if key_int is None:
            self.key_int = uuid.uuid4().urn
        else:
            self.key_int = key_int
        if values is not None:
            self.__add__(values)

        self.valueFunc = valueFunc
        #self.mode = mode

    def __add__(self,other):
        for v in other:
            self.append(v)

    def __getitem__(self, item):
        if self.mode == CACHE:
           return BZ2Decompressor().decompress(self.valueFunc(self.caches.listCache[self.key_int][item]))

        return self.valueFunc(self.redis.lindex(self.key_int,item))

    def __setitem__(self, key, value):
        if self.mode == CACHE:
            value = BZ2Compressor().compress(value)
            self.caches.listCache[self.key_int][key] = value
        else:
            return self.redis.lindex(self.key_int,key,value)

    def append(self,value):
        if isinstance(value,bytes):
            if self.mode == CACHE:
                value = BZ2Compressor().compress(value)
                self.caches.listCache[self.key_int].append(value)
            else:
                self.redis.lpush(self.key_int,value)
        else:
            if self.mode == CACHE:
                value = bz2.compress(json.dumps(value).encode("utf-8"))
                self.caches.listCache[self.key_int].append(value)
            else:
                self.redis.lpush(self.key_int, json.dumps(value))


    def __iter__(self):
        if self.mode == CACHE and len(self.caches.listCache[self.key_int]) > 0:
            return self.caches.listCache[self.key_int]
        else:
            for i in self.redis.lrange(self.key_int,0,self.__len__()):
                try:
                    i = bz2.decompress(i)
                except OSError:
                    pass #i not compressed
                yield json.loads(i.decode("utf-8"))




    def __len__(self):
        if self.mode == CACHE:
            l = len(self.caches.listCache[self.key_int])
            if l > 0:
                return l #if zero try if cached

        l = self.redis.llen(self.key_int)
        return l

    @property
    def __call__(self, *args, **kwargs):
        return self.__iter__()



class RedisDictKey(RedisBase):
    def __init__(self,key_int=None,val_type="json",keyFunc=lambda x:x,valueFunc=lambda x:x):
        """

        :param key_int:
        :param val_type:
        :param keyFunc:
        :param valueFunc:
        :param mode:
        """
        if key_int is None:
            self.key_int = uuid.uuid4().urn
        else:
            self.key_int = key_int
        self.val_type = val_type
        RedisBase.__init__(self)
        self.valueFunc = valueFunc
        self.keyFunc = keyFunc


    def __iter__(self):
        if self.mode == CACHE and len(self.caches.dictCache.keys()) > 0:
            return self.caches.dictCache.keys()

        for k in self.redis.hkeys(self.key_int):
            yield self.keyFunc(k)

    def __getitem__(self, item):
        #if self.mode == REDIS_MODE:
        #    self.redis.watch(self.key_int)
        if self.mode == CACHE:
            key = self.caches.dictCache[self.key_int][item]
        else:
            key = self.redis.hget(self.key_int, item)
            if key is not None:
                key = key.decode("utf-8")
        if self.val_type == "json":
            return json.loads(key)
        elif self.val_type == "hlist":
            if key is None:
                ret = RList(valueFunc=self.valueFunc)
            else:
                ret =  RList(key_int = key,valueFunc=self.valueFunc)

            if self.mode == CACHE:
                self.caches.dictCache[self.key_int][item] = ret.key_int
            else:
                self.redis.hset(self.key_int,item,ret.key_int)

            return ret

    def keys(self):
        return self.__iter__()

    def items(self):
        if self.mode == CACHE and len(self.caches.dictCache[self.key_int].items()) > 0:
            iter = self.caches.dictCache[self.key_int].items()
        else:
            iter = self.redis.hgetall(self.key_int).items()

        if self.val_type == "json":
            for x,v in iter:
                yield (self.keyFunc(x),json.loads(v))
        elif self.val_type == "hlist":
            for x,v in iter:
                if not isinstance(v,str):
                    v = v.decode("utf-8")


                #key = self.redis.hget(self.key_int, v).decode("utf-8")
                rl = RList(key_int=v,valueFunc=self.valueFunc)
                yield (self.keyFunc(x),rl)

    def values(self):
        for k,v in self.items():
            yield v

    def __len__(self):
        return len(self.keys())

    def __setitem__(self, key, values):
        if self.val_type == "json":
            if self.mode == CACHE:
                values = BZ2Compressor().compress(values)
                self.caches.cacheDict[self.key][key] = json.dumps(values)
            else:
                self.redis.hset(self.key_int,key,json.dumps(values))

        elif self.val_type == "hlist":
            if isinstance(values,RList):
                x = values
            else:
                x = RList(values=values,valueFunc=self.valueFunc)
            if self.mode == CACHE:
                self.caches.dictCache[self.key_int][key] = x.key_int
            else:
                self.redis.hset(self.key_int, key,x.key_int)

class RedisDictDict(RedisBase):
    def __init__(self,keyFunc=lambda x:x,valueFunc=lambda x:x):
        """
        can be used like defaultdict

        :param keyFunc: function which shall be applied when a key is returned from the list, normally the return value is of type bytes
        :param valueFunc: function which shall be applied when a value is returned from the list, normally the return value is of type bytes
        """
        self._data = {}
        RedisBase.__init__(self)
        self.valueFunc = valueFunc
        self.keyFunc = keyFunc


    def __getitem__(self, item):

        if not item in self._data:
            self._data[item] = uuid.uuid4().urn
            rd = RedisDictKey(keyFunc=self.keyFunc,valueFunc=self.valueFunc)

            if self.mode == CACHE:
                self.caches.valueCache[self._data[item]] = rd.key_int
            else:
                self.redis.set(self._data[item],rd.key_int)
            return rd


        key1 = self._data[item]
        if self.mode == CACHE:
            key2 = self.caches.valueCache[key1]
        else:
            key2 = self.redis.get(key1).decode("utf-8")
        return RedisDictKey(key2,keyFunc=self.keyFunc,valueFunc=self.valueFunc)

    def __setitem__(self,key,keyDict):
        key1 = uuid.uuid4().urn
        key2 = keyDict.key_int
        if self.mode == CACHE:
            self.caches.valueCache[key1] = key2
        else:
            self.redis.set(key1,key2)
        self._data[key] = key1

    def keys(self):
        return self._data.keys()

    def values(self):
        for k in self._data.keys():
            yield self.__getitem__(k)

    def items(self):
        for k in self._data.keys():
            yield (k,self.__getitem__(k))

    def __len__(self):
        return len(self.keys())


class RedisDictList(RedisBase):

    def __init__(self,keyFunc=lambda x:x,valueFunc=lambda x:x):
        """

        :param keyFunc:
        :param valueFunc:
        """
        self._data = {}
        RedisBase.__init__(self)
        self.valueFunc = valueFunc
        self.keyFunc = keyFunc


    def __getitem__(self, item):

        if not item in self._data:
            self._data[item] = uuid.uuid4().urn
            rd = RedisDictKey(val_type="hlist",keyFunc=self.keyFunc,valueFunc=self.valueFunc)
            if self.mode == CACHE:
                self.caches.valueCache[self._data[item]] = rd.key_int
            else:
                self.redis.set(self._data[item],rd.key_int)
            return rd

        key1 = self._data[item]
        key2 = None

        if self.mode == CACHE:
            key2 = self.caches.valueCache.get(key1,None)

        if key2 is None:
            key2 = self.redis.get(key1).decode("utf-8")
        return RedisDictKey(key2,val_type="hlist",keyFunc=self.keyFunc,valueFunc=self.valueFunc)

    def __setitem__(self,key,keyDict):
        key1 = uuid.uuid4().urn
        key2 = keyDict.key_int
        if self.mode == CACHE:
            self.caches.valueCache[key1] = key2
        else:
            self.redis.set(key1,key2)
        self._data[key] = key1

    def keys(self):
        return self._data.keys()

    def values(self):
        for k in self._data.keys():
            yield self.__getitem__(k)

    def items(self):
        for k in self._data.keys():
            yield (k,self.__getitem__(k))

    def dump(self,fn):
        pickle.dump(self._data,fn)

    def __len__(self):
        return len(self.keys())

    @classmethod
    def load(cls,fn,keyFunc=lambda x:x):
        data = pickle.load(fn)
        ret = RedisDictList(keyFunc=keyFunc)
        ret._data = data

        return ret


class DynamicEdgeListLong(RedisBase):

    def __init__(self,key_int = None):
        #self._data = [] #haelt die keys
        RedisBase.__init__(self)
        if key_int is None:
            self.key_int = uuid.uuid4().urn
        else:
            self.key_int = key_int

    def __iter__(self):
        iter = None
        if self.mode == CACHE and len(self.caches.listCache[self.key_int]) > 0:
            iter = self.caches.listCache[self.key_int]
        else:
            iter = self.redis.lrange(self.key_int,0,-1)

        for val in iter:
            #val = self.redis.lindex(i)
            s,e,k =json.loads(val)
            if isinstance(k,dict):
                yield (s,e,k)

            data = {}
            if self.mode == CACHE:
                data = self.caches.dictCache[k]
            if len(data) == 0:
                data = self.redis.hgetall(k)

            try:
                yield (s,e,json.loads(data))
            except TypeError:
                try:
                    data = {k.decode("utf-8"):v.decode("utf-8") for k,v in data.items()} #get all is binary
                except:
                    pass # keep data is not binary
                yield (s,e,data)

    def __getitem__(self, item):
        val = self.redis.lindex(self.key_int,item)
        s, e, k = json.loads(val)
        data = self.redis.hgetall(k)
        return (s,e,json.loads(data))


    def append(self,value):
        cnt = self.__len__()
        self.__setitem__(cnt,value)


    def __len__(self):
        if self.mode == CACHE:
            l = len(self.caches.listCache[self.key_int])
            if l > 0:
                return l  # if zero try if cached

        l = self.redis.llen(self.key_int)
        return l

    def __add__(self,list):
        for k in list:
                #Annahme k ist triple
                self.append(k)

    def __setitem__(self, key, value):
        s,e, k = value

        if isinstance(k,dict):
            key_int = uuid.uuid4().urn
            if len(k) > 0:

                if self.mode == CACHE:
                    k = bz2.compress(json.dumps(k).encode("utf-8"))
                    self.caches.dictCache[key_int] = k
                else:
                    self.redis.hmset(key_int,k)
                value_with_key = (s,e,key_int)
            else:
                if not self.redis.exists(k) and not k in self.caches.listCache :
                    raise Exception("Key doesn't exist")
                value_with_key = value
        value_with_key_json = json.dumps(value_with_key)
        if key == self.__len__():
            if self.mode == CACHE:
                self.caches.listCache[self.key_int].append(value_with_key_json)
            else:
                self.redis.lpush(self.key_int,value_with_key_json)
        else:
            if self.mode == CACHE:
                self.chaches.listCache[self.key_int][key] = value_with_key_json
            else:
                self.redis.lset(self.key_int,key,value_with_key_json)









