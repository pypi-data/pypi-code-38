import abc


class BaseTransformer(abc.ABC):

    @abc.abstractmethod
    def humanize(self, datum):
        pass

    @abc.abstractmethod
    def machanize(self, raw_dict):
        pass

    @abc.abstractmethod
    def serialize(self):
        pass

    @classmethod
    @abc.abstractmethod
    def deserialize(cls, serialized):
        pass
