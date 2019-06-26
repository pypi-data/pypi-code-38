from typing import Union
from abc import ABC, abstractmethod


class ReprMixin(ABC):
    """Adds a useful string representation to subclasses"""
    def __init__(self):
        self._to_repr = {}

    # TODO: replace all _to_repr[name] = attr lines with these shortcuts
    def _add_repr(self, name, attr=None, check=False):
        if attr is None:
            attr = name
        if (not check) or getattr(self, attr):
            self._to_repr[name] = attr

    def _add_reprs(self, names, check=False):
        for name in names:
            self._add_repr(name, check=check)

    def __repr__(self):
        attr_list = [f'{attr_name}={repr(getattr(self, attr))}'
                     for attr_name, attr in self._to_repr.items()]
        return f'{self.__class__.__name__}({", ".join(attr_list)})'


class IOBase(ReprMixin, ABC):
    """Base class for inputs, objectives and constraints.

    `name` is used for generating DataFrame column titles."""

    def __init__(self, name=''):
        super().__init__()
        self._name = name
        if name:
            self._to_repr['name'] = '_name'

    @property
    def name(self):
        return self._name or self._default_name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def _default_name(self):
        return ''


def get_name(x: Union[str, int, IOBase]):
    if isinstance(x, str):
        return x
    if isinstance(x, int):
        return str(x)
    return x.name


class Descriptor(ReprMixin, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.platypus_type = NotImplemented

    @abstractmethod
    def validate(self, value) -> bool:
        """Checks if value is a valid value for this parameter.

        :param value:
        :return: True if the value is valid False otherwise
        """

    # consider a pandas type to improve DataFrame generation
    @abstractmethod
    def sample(self, value):
        """Takes a value in the range 0-1 and returns a valid value for this parameter"""
        pass


class AnyValue(Descriptor):
    """A descriptor that can take on any possible value.
    Intended to be used as a placeholder."""
    def validate(self, value):
        return True

    def sample(self, value):
        raise NotImplementedError

    def __bool__(self):
        """Marks this as a 'missing' piece"""
        # ReprMixin will detect this as something to not include when checking
        return False


class Selector(ReprMixin, ABC):
    """Base Class for Selectors, which describe what attribute of the building is read or modified"""
    @abstractmethod
    def get(self, building):
        pass

    @abstractmethod
    def set(self, building, value):
        pass

    def setup(self, building) -> None:
        """Modifies the building so that it is ready for this selector"""
        pass


class DummySelector(Selector):
    """A selector that does not modify the building.
    Intended to be used as a placeholder."""
    def get(self, building):
        raise NotImplementedError

    def set(self, building, value):
        pass

    def __bool__(self):
        """Marks this as a 'missing' piece"""
        # ReprMixin will detect this as something to not include when checking
        return False


class Objective(IOBase):
    """Base class for objectives."""

    def __call__(self, *args, **kwargs) -> float:
        """Return the objective's value on the instance represented by *args and **kwargs"""
        raise NotImplementedError
