from abc import ABC, abstractmethod
from random import sample

from pymongo import MongoClient

class BaseCardStorage(ABC):

    @abstractmethod
    def sample(self):
        pass

class InMemoryCardStorage():

    def __init__(self):
        self._cards = []

    def sample(self, k):
        return sample(self._cards, k)

class MongoDbCardStorage():

    def __init__(self, database, **kwargs):
        self._collection = MongoClient(**kwargs)[database].cards

    def sample(self, k):
        return list(self._collection.aggregate([
            {'$sample': {'size': k}},
            {'$project': {'_id': 0}}
        ]))

class BaseResultStorage(ABC):

    @abstractmethod
    def insert_one(self, result):
        pass

    @abstractmethod
    def find(self):
        pass

class InMemoryResultStorage(BaseResultStorage):
    '''
    An in memory storage backend for use in testing. This is not fully
    compatible with mongoclient, for example the find method does not accept
    queries.
    '''

    def __init__(self):
        self._results = []

    def insert_one(self, result):
        self._results.append(result)

    def find(self):
        return self._results

class MongoDbResultStorage(BaseResultStorage):

    def __init__(self, database, **kwargs):
        self._collection = MongoClient(**kwargs)[database].results

    def insert_one(self, result):
        return self._collection.insert_one(result)

    def find(self):
        return list(self._collection.find({}, {'_id': 0}))
