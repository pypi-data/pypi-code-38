from abc import ABC, abstractmethod


class Builder(ABC):

    def __init__(self, data):
        self.data = data

    @abstractmethod
    def create_object(self, data):
        pass
