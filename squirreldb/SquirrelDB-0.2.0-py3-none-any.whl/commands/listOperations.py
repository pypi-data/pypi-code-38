from abc import ABC, abstractmethod

class ListOperations(ABC):
    def __init__(self):
        pass
    @abstractmethod
    def rpushKey(self, inMemoryReference, key, value):
        pass
    @abstractmethod
    def rpushKeyIfExists(self, inMemoryReference, key, value):
        pass
    @abstractmethod
    def lpushKey(self, inMemoryReference, key, value):
        pass
    @abstractmethod
    def llen(self, inMemoryReference, key):
        pass
    @abstractmethod
    def lpop(self, inMemoryReference, key):
        pass
    @abstractmethod
    def lindex(self, inMemoryReference, key,index):
        pass
    @abstractmethod
    def linsert(self, inMemoryReference,key, pivot, value):
        pass
    @abstractmethod
    def ltrim(self,inMemoryReference, key, start, stop):
        pass
    @abstractmethod
    def lset(self, inMemoryReference, key, index, value):
        pass
    @abstractmethod
    def rpop(self, inMemoryReference, key):
        pass

    @abstractmethod
    def lrange(self, inMemoryReference, key, start, end):
        pass

    @abstractmethod
    def createList(self, inMemoryReference, key):
        pass

    @abstractmethod
    def deleteList(self, inMemoryReference, key):
        pass
