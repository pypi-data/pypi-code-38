from typing import Callable, Dict, Type
import inspect


class Typeclass:
    pass


Instances = Dict[Type, Typeclass]
Getter = Callable[[Type], Typeclass]
Adder = Callable[[Type, Typeclass], None]
Undefiner = Callable[[Type], None]


def make_getter(instances: Instances, name: str) -> Getter:
    def getter(type: Type) -> Typeclass:
        for cls in inspect.getmro(type):
            if cls in instances:
                return instances[cls]
        raise TypeError("No instance for ({} {})".format(name, type))

    return getter


def make_adder(instances: Instances) -> Adder:
    def adder(type: Type, instance: Typeclass) -> None:
        instances[type] = instance

    return adder


def make_undefiner(instances: Instances) -> Undefiner:
    def undefiner(type: Type) -> None:
        for cls in inspect.getmro(type):
            if cls in instances:
                del instances[cls]

    return undefiner
