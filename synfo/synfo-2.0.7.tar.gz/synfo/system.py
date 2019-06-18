"""
A lightweight utility for retrieving system information and specifications.

System Information
------------------
Python
    Version
    Compiler
System
    OS
    Release
    Machine
    Architecture
    Hostname
    Username
Hardware
    Processor
        Type
        Cores
    Memory
        Installed
        Available
"""
from argparse import ArgumentParser
from multiprocessing import cpu_count
from os import getlogin
from platform import python_version, python_compiler, system, release, machine, processor, architecture, node
from synfo.format import Formatter

# Conditional import of psutil
try:
    from psutil import virtual_memory
    _PSUTIL_INSTALL = True
except ImportError:
    _PSUTIL_INSTALL = False


class Python(Formatter):
    """Python related information such as Python version and Python compiler"""
    def __init__(self):
        super(Python, self).__init__('Python', self.info)

    def info(self):
        return {'version': self.version, 'compiler': self.compiler}

    @property
    def version(self): return python_version()

    @property
    def compiler(self): return python_compiler()


class System(Formatter):
    """Software related information such as operating system, machine type, username, etc."""
    def __init__(self):
        super(System, self).__init__('System', self.info)

    def info(self):
        return {'os': self.os, 'release': self.release, 'machine': self.machine, 'architecture': self.architecture,
                'hostname': self.hostname, 'username': self.username}

    @property
    def os(self):
        return system()

    @property
    def release(self):
        return release()

    @property
    def machine(self):
        return machine()

    @property
    def architecture(self):
        return architecture()[0]

    @property
    def hostname(self):
        return node()

    @property
    def username(self):
        try:
            return getlogin()
        except OSError:
            return 'N/A'


class Memory(Formatter):
    """Memory information class."""
    def __init__(self):
        super(Memory, self).__init__('Memory', self.info)

    def __str__(self): return self.installed

    if _PSUTIL_INSTALL:
        def info(self):
            return {'installed': self.installed, 'available': self.available}

        @property
        def installed(self):
            return self._format_size(virtual_memory()[0], binary=True)

        @property
        def available(self):
            return self._format_size(virtual_memory()[1], binary=True)

    else:
        @staticmethod
        def info(): return 'N/A'

        @property
        def installed(self):
            return self.info()

        @property
        def available(self):
            return self.info()


class Processor:
    """Processor information class"""
    def __str__(self):
        return self.type

    @property
    def type(self):
        return processor()

    @property
    def cores(self):
        return cpu_count()


class Hardware(Formatter):
    """Hardware related information such as memory and processor information"""
    def __init__(self):
        super(Hardware, self).__init__('Hardware', self.info)

    def info(self):
        return {'memory_installed': self.memory.installed, 'memory_available': self.memory.available,
                'processor_type': self.processor.type, 'processor_cores': self.processor.cores}

    @property
    def memory(self): return Memory()

    @property
    def processor(self): return Processor()


class Synfo:
    def __init__(self, kwargs=None):
        self.python = Python()
        self.system = System()
        self.hardware = Hardware()
        self._iter = self._set_iter(kwargs)

    def _set_iter(self, kwargs):
        """Create list system info to return"""
        # Confirm kwargs is not None
        if kwargs:
            python, system, hardware = kwargs.get('python', True), kwargs.get('system', True), kwargs.get('hardware', True)
        else:
            python, system, hardware = True, True, True

        # Create list to return
        lst = []
        if python and python is True:
            lst.append(self.python)
        if system and system is True:
            lst.append(self.system)
        if hardware and hardware is True:
            lst.append(self.hardware)
        return lst

    def __iter__(self):
        return iter(self._iter)

    def __str__(self):
        return ''.join([str(i) for i in self.__iter__()]).strip()

    def all(self):
        return {n._type.lower(): n.info() for n in self.__iter__()}


def synfo(kwargs=None):
    """Wrapper function for Synfo class"""
    return Synfo(kwargs)


def main():
    # Declare argparse argument descriptions
    usage = 'Retrieve system information'
    description = 'A lightweight utility for retrieving system information and specifications.'
    helpers = {
        'a': "All available system information",
        'p': "Python interpreter information such as Python version and Python compiler",
        's': "Software related information such as operating system, machine type, username, etc.",
        'hw': "Hardware related information such as memory and processor information",
    }

    # construct the argument parse and parse the arguments
    ap = ArgumentParser(usage=usage, description=description)
    ap.add_argument("-a", "--all", help=helpers['a'], action='store_true')
    ap.add_argument("-p", "--python", help=helpers['p'], action='store_true')
    ap.add_argument("-s", "--system", help=helpers['s'], action='store_true')
    ap.add_argument("-hw", "--hardware", help=helpers['hw'], action='store_true')
    args = vars(ap.parse_args())

    # Set python, system and hardware flags to True if all is set
    _all = args.pop('all')
    if _all is True:
        args = {k: True for k in args.keys()}
    elif all(v is False for v in args.values()):
        args = {k: True for k in args.keys()}

    # Run EnvInfo
    print(synfo(args))


if __name__ == '__main__':
    main()
