import functools
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class factory:
    """Caches classes

    Attributes:
        names: names of class fields to use for caching
        repository: cache dictionary
        capture_subclasses: also cache subclasses

    """
    names: List[str] = field(default_factory=list)
    repository: Dict[Any, Any] = field(repr=False, default_factory=dict)
    capture_subclasses: bool = False

    def __repr__(self):
        return f'{self.__class__.__name__}(names={self.names}, count={len(self.repository)})'

    def generate_key(self, cls, *args, **kwds):
        cls_key = {}
        for index, name in enumerate(self.names):
            if name in kwds:
                value = kwds.get(name)
            elif len(args) > index:
                value = args[index]
            elif hasattr(cls, name):

                value = getattr(cls, name)
            else:
                # Guard for programming errors during development
                raise KeyError(f'Could not find `{name}` in {cls} `__new__` invocation: args={args} kwds={kwds}')
            cls_key[name] = value
        vals = tuple(cls_key.values())
        return vals

    def get_instance(self, cls, *args, **kwds):
        """Looks up instance if possible, creates a new one if the key
        doesn't exist.

        """
        vals = self.generate_key(cls, *args, **kwds)
        if vals not in self.repository:
            instance = object.__new__(cls)
            self.repository[vals] = instance
        instance = self.repository[vals]
        return instance

    def __call__(self, cls, *args, **kwds):
        # print(f'self={self} cls={cls}, args={args}, kwds={kwds}')

        @functools.wraps(cls.__new__)
        def new(cls, *args, **kwds):
            return self.get_instance(cls, *args, **kwds)

        # this works with one decorator but not multiple
        #  TODO: make this wrap factories and other classes
        #        so we can stack factories based on different
        #        attributes
        cls.__new__ = new
        return cls
