import string
from abc import ABC, abstractmethod
class StringOperations:
    def __init__(self):
        pass

    @abstractmethod
    def append(self, inMemoryDataStore, key, value):
        pass
    @abstractmethod
    def setKey(self, inMemoryDataStore, key, value):
        pass

    @abstractmethod
    def setKeyIfNotExists(self,inMemoryDataStore, key, value):
        pass

    @abstractmethod
    def strlenKey(self, inMemoryDataStore, key):
        pass

    @abstractmethod
    def getKey(self, inMemoryDataStore, key):
        pass

    @abstractmethod
    def incrKey(self, inMemoryDataStore, key):
        pass

    @abstractmethod
    def incrKeyBy(self, inMemoryDataStore, key,value):
        pass

    @abstractmethod
    def decrKey(self, inMemoryDataStore, key):
        pass

    @abstractmethod
    def decrKeyBy(self, inMemoryDataStore, key,value):
        pass

    @abstractmethod
    def delKey(self, inMemoryDataStore, key):
        pass

    @abstractmethod
    def exists(self, inMemoryDataStore, key):
        pass

