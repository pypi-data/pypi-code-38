from abc import ABC, abstractmethod


class BaseBuilder(ABC):

    @abstractmethod
    def build(self, layers):
        pass

    @abstractmethod
    def create_layer(self, layer):
        pass
