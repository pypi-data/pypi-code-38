import logging

class MUDObject(object):

    def __str__(self):
        return "{}({})".format(self.__class__.__name__, ", ".join([str(k) + "=" + str(v) for k,v in self.__dict__.items()]))

    def __del__(self):
        logging.debug("Deleting {}".format(self))

class MetaMUDInterface(type):
    _INTERFACES = {}

    def __new__(cls, name, bases, dct):
        inst = super().__new__(cls, name, bases, dct)
        if inst.name:
            cls._INTERFACES[inst.name] = inst
        return inst

class MUDInterface(MUDObject, metaclass=MetaMUDInterface):

    name = None
    engine = None
