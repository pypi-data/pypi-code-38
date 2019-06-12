# # # # # # # # # # # # # # # # # # # # # # # # # #
# Java driver class
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import os
#import socket
#import traceback

from sys import platform, version_info

import numpy # noqa: F401

CLASSPATH_SEP = ";" if platform == "win32" else ":"

IS_VENV = os.environ.get("VIRTUAL_ENV") is not None


class Java(object):
    """Convenience wrapper for Python Java bindings.

    WARNING: due to underlying Python Java bindings library limitations, you
    cannot run a single Python process that uses this driver at least twice but
    with different Java classpaths. The subsequent classpaths won't correctly
    load.
    """
    jpype = None
    started_in = set()

    _jpype = None

    @classmethod
    def _get_jpype(cls):
        """Import jpype"""

        if cls._jpype is None:
            try:
                import jpype
            except ImportError:
                if (
                    version_info.major < 3
                ):
                    raise RuntimeError("you can only use java models with Python 3")
                if IS_VENV:
                    raise ImportError("please run 'pip3 install --user JPype1' first.")
                else:
                    raise ImportError(
                        "please run 'pip3 install --user JPype1' first."
                    )

            cls._jpype = jpype

        return cls._jpype

    def __init__(self, jvmpath=None, classpath=None, jvmargs="", cwrank=-1):
        """Instantiate the java driver corresponding to the java jar given in classpath"""

        jpype = self._get_jpype()

        if jvmpath is None:
            jvmpath = jpype.getDefaultJVMPath()

        if not jpype.isJVMStarted():

            jpype.startJVM(
                jvmpath,
                "-XX:ParallelGCThreads=1",
                jvmargs,
                "" if classpath is None else ("-Djava.class.path=%s" % classpath),
            )

    # FIXME: enable JVM shutdown
    # def __enter__(self):
    #     return self
    #
    # def __exit__(self, exc_type, exc_value, traceback):
    #     jpype = self._get_jpype()
    #     if jpype.isJVMStarted():
    #         jpype.shutdownJVM()

    def get_class(self, name):
        """Return the java class 'name' from loaded java jar"""

        jpype = self._get_jpype()
        assert jpype is not None, "please instantiate Java first"
        return jpype.JClass(name)

    @classmethod
    def save(cls, buff):
        """Return 'state' (of the model) as numpy uint8 array when 'buff' (the state of the model from the user code) is in binary format"""

        state = numpy.empty(len(buff), dtype="uint8")
        #state = cls.state(len(buff))

        try:
            #state = buff
            state[:] = buff[:]
        except:
            jpype = cls._get_jpype()
            Jstr = jpype.java.lang.String(buff,'ISO-8859-1').toString().encode('UTF-16LE')
            bytearr = numpy.array(numpy.frombuffer(Jstr, dtype='=u2'), dtype=numpy.byte)
            state = numpy.frombuffer(bytearr, dtype="uint8")
            #raise ValueError("state = buff failed in save() of java.py. This may be a bug.")
        if len(state) != len(buff):
            raise ValueError("len(state) != len(buff) in save() of java.py. This may be a bug.")

        return state

    @classmethod
    def load(cls, state):
        """Take 'state' (of the model) from save(), i.e. as numpy uint8 array, and return 'buff' in byte to be passed to the java user code"""

        jpype = cls._get_jpype()
        JByteArray = jpype.JArray(jpype.JByte)
        buff = JByteArray(len(state))

        #buff = cls.state(len(state))

        try:
            #buff = state
            buff[:] = state[:]
        except:
            tmpstate = numpy.frombuffer(state,dtype="b") #int8,B
            buff = jpype.JArray(jpype.JByte,1)(tmpstate.tolist())
            #raise ValueError("buff = state failed in load() of java.py. This may be a bug.")

        if len(buff) != len(state):
            raise ValueError("len(buff) != len(state) in load() of java.py. This may be a bug.")

        return buff

    @classmethod
    def state(cls, size):
        """Return 'state' as jByteArray of given 'size'"""

        #state = bytearray(size)

        jpype = cls._get_jpype()
        JByteArray = jpype.JArray(jpype.JByte)
        state = JByteArray(size)
        return state
