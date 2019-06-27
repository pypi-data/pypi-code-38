from abc import ABC, abstractmethod
class Persistence(ABC):
    def __init__(self):
        self.filename = ""
        self.filePath = ""
        self.timeofcreation = ""
        self.timeofupdation = ""
        pass
    @abstractmethod
    def load(self, databaseFilePath, inMemoryReference):
        pass
    @abstractmethod
    def store(self, inMemoryReference, databaseFilePath):
        pass
    @abstractmethod
    def close(self):
        pass
