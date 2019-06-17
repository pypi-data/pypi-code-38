"""
@author: Julian Sobott
@brief:
@description:

@external_use:

@internal_use:
"""
import pynetworking as net

from pynetworking.Logging import logger


class _DummyServerFunctions(net.ServerFunctions):
    @staticmethod
    def no_arg_no_ret() -> None:
        return no_arg_no_ret()

    @staticmethod
    def no_arg_ret() -> bool:
        return no_arg_ret()

    @staticmethod
    def incrementer(number: int) -> int:
        return incrementer(number)

    @staticmethod
    def immutable_args_ret(name: str, age: int, children: tuple) -> str:
        return immutable_args_ret(name, age, children)

    @staticmethod
    def args_ret_object(name, age) -> 'DummyPerson':
        return args_ret_object(name, age)

    @staticmethod
    def class_args_ret(person: 'DummyPerson') -> tuple:
        return class_args_ret(person)

    @staticmethod
    def huge_args_huge_ret(*args):
        return huge_args_huge_ret(*args)

    @staticmethod
    def func_in_func(start: int) -> bool:
        return func_in_func(start)

    @staticmethod
    def many_func_in_func():
        return many_func_in_func()

    @staticmethod
    def server_faculty(number: int) -> int:
        return server_faculty(number)

    @staticmethod
    def client_faculty(number: int) -> int:
        return client_faculty(number)

    @staticmethod
    def get_file(file_path: str, destination_path: str) -> net.File:
        return get_file(file_path, destination_path)


class _DummyClientFunctions(net.ServerFunctions):
    @staticmethod
    def no_arg_no_ret() -> None:
        return no_arg_no_ret()

    @staticmethod
    def no_arg_ret() -> bool:
        return no_arg_ret()

    @staticmethod
    def incrementer(number: int) -> int:
        return incrementer(number)

    @staticmethod
    def immutable_args_ret(name: str, age: int, children: tuple) -> str:
        return immutable_args_ret(name, age, children)

    @staticmethod
    def args_ret_object(name, age) -> 'DummyPerson':
        return args_ret_object(name, age)

    @staticmethod
    def class_args_ret(person: 'DummyPerson') -> tuple:
        return class_args_ret(person)

    @staticmethod
    def huge_args_huge_ret(*args):
        return huge_args_huge_ret(*args)

    @staticmethod
    def func_in_func(start: int) -> bool:
        return func_in_func(start)

    @staticmethod
    def many_func_in_func():
        return many_func_in_func()

    @staticmethod
    def server_faculty(number: int) -> int:
        return server_faculty(number)

    @staticmethod
    def client_faculty(number: int) -> int:
        return client_faculty(number)


class DummyServerCommunicator(net.ServerCommunicator):
    remote_functions = _DummyServerFunctions
    local_functions = _DummyClientFunctions


class DummyMultiServerCommunicator(net.MultiServerCommunicator):
    remote_functions = _DummyServerFunctions
    local_functions = _DummyClientFunctions


class DummyClientCommunicator(net.ClientCommunicator):
    remote_functions = _DummyClientFunctions
    local_functions = _DummyServerFunctions


class DummyPerson:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __eq__(self, other):
        if isinstance(other, DummyPerson):
            return (self.name == other.name
                    and self.age == other.age)


def no_arg_no_ret() -> None:
    print("no_arg_no_ret() called")


def no_arg_ret() -> bool:
    print("no_arg_ret() called")
    return True


def incrementer(number: int) -> int:
    return number + 1


def immutable_args_ret(name: str, age: int, children: tuple) -> str:
    return f"{name} is {age} old and has {len(children)}: {children}"


def args_ret_object(name, age) -> DummyPerson:
    return DummyPerson(name, age)


def class_args_ret(person: DummyPerson) -> tuple:
    name = person.name
    age = person.age
    return name, age


def huge_args_huge_ret(*args):
    return args


def func_in_func(start: int) -> bool:
    ret = net.ClientManager().get().remote_functions.incrementer(start)
    return ret + 1


def many_func_in_func():
    return net.ClientManager().get().remote_functions.client_faculty(5)


def server_faculty(number: int) -> int:
    if number <= 1:
        return number
    return number * net.ClientManager().get().remote_functions.client_faculty(number - 1)


def client_faculty(number: int) -> int:
    if number <= 1:
        return number
    return number * DummyServerCommunicator.remote_functions.server_faculty(number - 1)


def get_file(file_path: str, destination_path: str) -> net.File:
    return net.File(file_path, destination_path)

