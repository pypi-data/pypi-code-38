import abc


class Taggable(abc.ABC):
    tag = abc.abstractmethod()
    tags = abc.abstractproperty()
