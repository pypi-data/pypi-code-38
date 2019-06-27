from squirreldb.commands.stringOperationsImpl import StringOperationsImpl
from squirreldb.persistence.jsonPersistence import JsonPersistence
from squirreldb.engine.operations import Category
from squirreldb.persistence.storageState import StorageState
from squirreldb.commands.listOperationsImpl import ListOperationsImpl
import threading

class Squirrel():
    def __init__(self, filelocation=''):
        self.inMemoryStore = {}
        self.operations = {}
        self.operations[Category.STRING] = StringOperationsImpl()
        self.operations[Category.LIST] = ListOperationsImpl()
        self.persistence = JsonPersistence()
        self.databasefilename = ''
        # Lock Reference
        self.Thread = threading.Lock()
        self.databasefilelocation = filelocation
        if self.databasefilelocation != '' and self.databasefilename == '':
            self.databasefilename = self.databasefilelocation.split("/")[-1]
            self.persistence.load(self.databasefilelocation, self.inMemoryStore, StorageState.STALE)

    def DoThreadSafeOperation(self, callbackFunction, *argv):
        self.Thread.acquire()
        toret = False
        try:
            toret = callbackFunction(*argv)
        finally:
            self.Thread.release()
        return toret

    def get(self,key):
        return self.DoThreadSafeOperation(self.operations[Category.STRING].getKey,self.inMemoryStore, key)

    def set(self, key, value):
        return self.DoThreadSafeOperation(self.operations[Category.STRING].setKey,self.inMemoryStore,key,value)

    def append(self,key, value):
        return self.DoThreadSafeOperation(self.operations[Category.STRING].append,self.inMemoryStore, key,value)

    def setIfNotExists(self, key, value):
        return self.DoThreadSafeOperation(self.operations[Category.STRING].setKeyIfNotExists, self.inMemoryStore,key, value)

    def getStrLen(self, key):
        return self.DoThreadSafeOperation(self.operations[Category.STRING].strlenKey, self.inMemoryStore, key)

    def incrKey(self, key):
        return self.DoThreadSafeOperation(self.operations[Category.STRING].incrKey, self.inMemoryStore,key)

    def decrKey(self, key):
        return self.DoThreadSafeOperation(self.operations[Category.STRING].decrKey, self.inMemoryStore,key)

    def decrKeyBy(self, key, value):
        return self.DoThreadSafeOperation(self.operations[Category.STRING].decrKeyBy, self.inMemoryStore, key, value)

    def incrKeyBy(self,key, value):
        return self.DoThreadSafeOperation(self.operations[Category.STRING].incrKeyBy, self.inMemoryStore, key, value)

    def delKey(self, key):
        return self.DoThreadSafeOperation(self.operations[Category.STRING].delKey, self.inMemoryStore,key)

    def removeAll(self):
        if self.inMemoryStore == None:
            return False
        self.Thread.acquire()
        try:
            self.inMemoryStore.clear()
        finally:
            self.Thread.release()
        return True

    def exists(self, key):
        return self.DoThreadSafeOperation(self.operations[Category.STRING].exists, self.inMemoryStore, key)

    def load(self, filepath, updatePolicy=StorageState.INMEMORY):
        return self.DoThreadSafeOperation(self.persistence.load, filepath,self.inMemoryStore, updatePolicy)

    def store(self, filepath):
        return self.DoThreadSafeOperation(self.persistence.store, self.inMemoryStore,filepath)

    def createList(self, key):
        return self.DoThreadSafeOperation(self.operations[Category.LIST].createList, self.inMemoryStore,key)

    def deleteList(self, key):
        return self.DoThreadSafeOperation(self.operations[Category.LIST].deleteList, self.inMemoryStore,key)

    def listRange(self, key, start, end):
        return self.DoThreadSafeOperation(self.operations[Category.LIST].lrange, self.inMemoryStore,key, start,end)

    def listPopRight(self, key):
        return self.DoThreadSafeOperation(self.operations[Category.LIST].rpop, self.inMemoryStore,key)

    def listSet(self, key, index, value):
        return self.DoThreadSafeOperation(self.operations[Category.LIST].lset, self.inMemoryStore, key, index, value)

    def listTrim(self, key, start, end):
        return self.DoThreadSafeOperation(self.operations[Category.LIST].ltrim, self.inMemoryStore,key, start, end)

    def listInsert(self, key, pivot, value):
        return self.DoThreadSafeOperation(self.operations[Category.LIST].linsert, self.inMemoryStore, key, pivot, value)

    def listIndex(self, key, index):
        return self.DoThreadSafeOperation(self.operations[Category.LIST].lindex, self.inMemoryStore, key, index)

    def listPopLeft(self,key):
        return self.DoThreadSafeOperation(self.operations[Category.LIST].lpop, self.inMemoryStore, key)

    def listLength(self, key):
        return self.DoThreadSafeOperation(self.operations[Category.LIST].llen, self.inMemoryStore, key)

    def listPushValueLeft(self, key, value):
        return self.DoThreadSafeOperation(self.operations[Category.LIST].lpushKey, self.inMemoryStore, key, value)

    def listPushValueRight(self, key, value):
        return self.DoThreadSafeOperation(self.operations[Category.LIST].rpushKey, self.inMemoryStore, key, value)

    def listPushValueRightIfExists(self, key, value):
        return self.DoThreadSafeOperation(self.operations[Category.LIST].rpushKeyIfExists, self.inMemoryStore, key, value)
