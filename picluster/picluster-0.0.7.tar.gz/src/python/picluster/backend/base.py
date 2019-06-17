from enum import Enum, auto
import abc


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name


class Backends(AutoName):
    slurm = auto()


class Backend:
    @classmethod
    @abc.abstractmethod
    def queue(cls):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def submit(cls, task):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def cancel(cls, task):
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def inspect(cls, task):
        raise NotImplementedError
