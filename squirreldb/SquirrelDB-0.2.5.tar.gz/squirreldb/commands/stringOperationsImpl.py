import sys
from squirreldb.commands.stringOperations  import StringOperations

class StringOperationsImpl(StringOperations):
    def __init__(self):
        super().__init__()

    def append(self, inMemoryDataStore, key, value):
        if inMemoryDataStore == None or key == None or value ==None:
            return False
        if key in inMemoryDataStore and isinstance(inMemoryDataStore[key], str) and isinstance(value, str):
            inMemoryDataStore[key] = inMemoryDataStore[key]+value
            return True
        return False

    def setKey(self, inMemoryDataStore, key, value):
        if inMemoryDataStore == None or key == None or value == None:
            return False
        if isinstance(value, str) or isinstance(value, int):
            inMemoryDataStore[key] = value
            return True
        return False

    def setKeyIfNotExists(self,inMemoryDataStore, key, value):
        if inMemoryDataStore == None or key == None or value == None:
            return False
        if isinstance(value, str) or isinstance(value, int):
            if key not in inMemoryDataStore:
                inMemoryDataStore[key] = value
                return True
        return False

    def strlenKey(self, inMemoryDataStore, key):
        if inMemoryDataStore == None or key == None:
            return False
        if key in inMemoryDataStore and isinstance(inMemoryDataStore[key], str):
            return len(inMemoryDataStore[key])
        return False

    def getKey(self, inMemoryDataStore, key):
        if inMemoryDataStore == None or key == None:
            return False
        if key in inMemoryDataStore:
            return inMemoryDataStore[key]
        return False

    def incrKey(self, inMemoryDataStore, key):
        if inMemoryDataStore == None or key == None:
            return False
        if key not in inMemoryDataStore:
            inMemoryDataStore[key] = 0
        if isinstance(inMemoryDataStore[key], int) and inMemoryDataStore[key] < sys.maxsize-1:
            inMemoryDataStore[key] = inMemoryDataStore[key] + 1
            return True
        return False

    def decrKey(self, inMemoryDataStore, key):
        if inMemoryDataStore == None or key == None:
            return False
        if key not in inMemoryDataStore:
            inMemoryDataStore[key] = 0
        if isinstance(inMemoryDataStore[key], int) and inMemoryDataStore[key] > -sys.maxsize +1:
            inMemoryDataStore[key] = inMemoryDataStore[key] - 1
            return True
        return False

    def incrKeyBy(self, inMemoryDataStore, key,value):
        if inMemoryDataStore == None or value == None or not isinstance(value, int) or value < 0 or key == None:
            return False
        if key not in inMemoryDataStore:
            inMemoryDataStore[key] = 0
        if isinstance(inMemoryDataStore[key], int) and inMemoryDataStore[key] < sys.maxsize-value:
            inMemoryDataStore[key] = inMemoryDataStore[key] + value
            return True
        return False

    def decrKeyBy(self, inMemoryDataStore, key,value):
        if inMemoryDataStore == None or value == None or not isinstance(value, int) or value < 0 or key == None:
            return False
        if key not in inMemoryDataStore:
            inMemoryDataStore[key] = 0
        if isinstance(inMemoryDataStore[key], int) and inMemoryDataStore[key] > -sys.maxsize+value:
            inMemoryDataStore[key] = inMemoryDataStore[key] - value
            return True
        return False

    def delKey(self, inMemoryDataStore, key):
        if inMemoryDataStore == None or key == None or key not in inMemoryDataStore:
            return False
        del inMemoryDataStore[key]
        return True

    def exists(self, inMemoryDataStore, key):
        if inMemoryDataStore == None or key == None or key not in inMemoryDataStore:
            return False
        return True