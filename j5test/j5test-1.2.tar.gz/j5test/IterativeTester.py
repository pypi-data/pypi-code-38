# -*- coding: utf-8 -*-
# Copyright 2006 St James Software

__all__ = ['IterativeTester','Dimension']

import copy
import sys
from j5basic import DictUtils
from j5test import Utils
try:
    from j5.OS import ThreadControl
except ImportError as e:
    ThreadControl = None
import threading
from six import with_metaclass

def combinations(*args):
    """Generate all combinations of items from argument lists.
    """
    if len(args) == 0:
        yield []
    else:
        for x in args[0]:
            for rest in combinations(*args[1:]):
                yield [x] + rest

class IterativeTesterMetaClass(type):
    def __init__(cls, name, bases, dct):
        """We need to create the new test methods at class creation time so that
           py.test knows can find them as soon as the module is loaded."""
        super(IterativeTesterMetaClass, cls).__init__(name, bases, dct)
        cls.makeIterativeTests(dct)

class IterativeTester(with_metaclass(IterativeTesterMetaClass, object)):
    """
    Parent class for test classes which want to have methods iterated over
    sets of parameters.
    """

    # Dictionary defining iterative tests. Keys are the prefixes of the
    # methods to be iterated with different parameters. Values are arrays
    # of Dimension objects which need to be iterated over.
    DIMENSIONS = {}

    # Dictionary for storing data used by test methods with a particular
    # prefix and set of iterated over parameters.
    _METHOD_DATA = {}

    @classmethod
    def makeIterativeTests(cls,dct):
        """
        Create all iterative tests specified in DIMENSIONS dictionary and
        remove processed methods.
        """
        # need to use the dct for this class because we're updating cls.__dict__
        # by adding new methods as we go
        dicts = [getattr(basecls,"__dict__",{}) for basecls in cls.__mro__ if not basecls is cls]
        dicts.insert(0,dct)

        for prefix in list(cls.DIMENSIONS.keys()):
            for clsdct in dicts:
                for methname, meth in clsdct.items():
                    if methname.startswith(prefix) and callable(meth):
                        cls.makeIterativeTestsForMethod(prefix,methname,meth)

            for dim in cls.DIMENSIONS[prefix]:
                cls.makeFailedConditionTestsForDim(prefix, dim)
                cls.makeSkippedConditionTestsForDim(prefix, dim)

    @classmethod
    def makeIterativeTestsForMethod(cls,prefix,methname,meth):
        """
        Create the iterative tests for a single method.
        """
        for varnames in cls.permuteVars(prefix):
            cls.createTestMethod(prefix,varnames,methname,meth)

    @classmethod
    def createTestMethod(cls,prefix,varnames,oldmethname,oldmeth):
        """
        Add a new test method.
        """
        newname = "test" + oldmethname[len(prefix):] + "_" + "_".join(varnames)

        # don't overwrite existing methods
        if newname in cls.__dict__:
            return

        def newmeth(self):
            self.setup_iterative_method(getattr(self, newname))
            try:
                if self.iterdata.get('_iterativetest_setup_class_failed',None) is not None:
                    e, trace = self.iterdata.get('_iterativetest_setup_class_failed')
                    raise e.with_traceback(trace)
                args = cls.getMethodArgs(prefix,varnames)
                return oldmeth(self,*args)
            finally:
                self.teardown_iterative_method(getattr(self, newname))

        newmeth.__name__ = newname
        if oldmeth.__doc__:
            newmeth.__doc__ = oldmeth.__doc__ + " (%s)" % (", ".join(varnames),)
        newmeth.__dict__ = oldmeth.__dict__.copy()
        newmeth.iterativetestprefix = prefix
        newmeth.iterativetestvarnames = varnames
        for k in dir(oldmeth):
            if not k.startswith("__"):
                setattr(newmeth, k, getattr(oldmeth, k))


        setattr(cls,newname,newmeth)

    @classmethod
    def makeFailedConditionTestsForDim(cls, prefix, dim):
        failed_conditions = dim.getFailedConditions()
        for name, message in failed_conditions.items():
            cls.createFailMessageTest(prefix, name, message)

    @classmethod
    def createFailMessageTest(cls, prefix, conditionname, message):
        """
        Add a failing test method which prints a message
        """
        newname = "test_"+prefix+"_"+conditionname

        def failmeth(self):
            print(message)
            assert False

        failmeth.__name__ = newname

        setattr(cls, newname, failmeth)

    @classmethod
    def makeSkippedConditionTestsForDim(cls, prefix, dim):
        skipped_conditions = dim.getSkippedConditions()
        for name, message in skipped_conditions.items():
            cls.createSkipMessageTest(prefix, name, message)

    @classmethod
    def createSkipMessageTest(cls, prefix, conditionname, message):
        """
        Add a skipping test method which prints a message
        """
        newname = "test_"+prefix+"_"+conditionname

        def skipmeth(self):
            Utils.skip(message)

        skipmeth.__name__ = newname

        setattr(cls, newname, skipmeth)

    @classmethod
    def permuteVars(cls,prefix):
        for varnames in combinations(*[dim.getNames() for dim in cls.DIMENSIONS[prefix]]):
            yield varnames

    @classmethod
    def getMethodArgs(cls,prefix,varnames):
        return [dim.getValue(name) for name, dim in zip(varnames,cls.DIMENSIONS[prefix])]

    @classmethod
    def setup_class(cls):
        for prefix, dims in cls.DIMENSIONS.items():
            # call dim setup methods
            for dim in dims:
                dim.setup()

            # create attribute dictionaries for use as self.iterdata values
            for varnames in cls.permuteVars(prefix):
                cls._METHOD_DATA[(prefix,tuple(varnames))] = DictUtils.attrdict()

            # call prefix's class setup methods
            setupmeth = getattr(cls,"setup_class_" + prefix,None)
            if callable(setupmeth):
                for varnames in cls.permuteVars(prefix):
                    cls.iterdata = cls._METHOD_DATA[(prefix,tuple(varnames))]

                    args = cls.getMethodArgs(prefix,varnames)
                    try:
                        setupmeth(*args)
                    except Exception as e:
                        cls.iterdata['_iterativetest_setup_class_failed'] = (e,sys.exc_info()[2])

                    del cls.iterdata

    @classmethod
    def teardown_class(cls):
        for prefix, dims in cls.DIMENSIONS.items():
            # call prefix's class teardown methods
            teardownmeth = getattr(cls,"teardown_class_" + prefix,None)
            if callable(teardownmeth):
                for varnames in cls.permuteVars(prefix):
                    cls.iterdata = cls._METHOD_DATA[(prefix,tuple(varnames))]

                    if cls.iterdata.get('_iterativetest_setup_class_failed',None) is not None:
                        continue

                    args = cls.getMethodArgs(prefix,varnames)
                    try:
                        teardownmeth(*args)
                    except Exception as e:
                        cls.iterdata['_iterativetest_teardown_class_failed'] = (e,sys.exc_info()[2])

                    del cls.iterdata

            # remove attribute dictionaries
            for varnames in cls.permuteVars(prefix):
                del cls._METHOD_DATA[(prefix,tuple(varnames))]

            # call dim teardown methods
            for dim in dims:
                dim.teardown()
        # Brute-force any extra threads to make sure plugins have shut down correctly
        if ThreadControl:
            ThreadControl.stop_threads(exclude_threads=[threading.currentThread()])

    def setup_iterative_method(self, method):
        if hasattr(method, "iterativetestprefix"):
            prefix = method.iterativetestprefix
            varnames = method.iterativetestvarnames
            setup_method = getattr(self,"setup_method_" + prefix, None)

            # get self.iterdata
            self.iterdata = self.__class__._METHOD_DATA[(prefix,tuple(varnames))]

            # let the dimension objects do any pre-method setup they need
            for varname, dim in zip(varnames,self.__class__.DIMENSIONS[prefix]):
                dim.setup_method(varname)

            # call the prefix specific method setup
            if callable(setup_method):
                args = self.__class__.getMethodArgs(prefix,varnames)
                setup_method(method,*args)


    def teardown_iterative_method(self, method):
        if hasattr(method, "iterativetestprefix"):
            prefix = method.iterativetestprefix
            varnames = method.iterativetestvarnames
            teardown_method = getattr(self,"teardown_method_" + prefix, None)

            # call the prefix specific method teardown
            if callable(teardown_method):
                args = self.__class__.getMethodArgs(prefix,varnames)
                teardown_method(method,*args)

            # let the dimension objects do any post-method teardown they need
            for varname, dim in zip(varnames,self.__class__.DIMENSIONS[prefix]):
                dim.teardown_method(varname)

            # unset self.iterdata
            del self.iterdata

class Dimension(object):
    """A collection of resources (databases, webservers or whatever) for
       IterativeTesters to access. Sub-classes need to override .getNames()
       to provide a list of names for the available resources and .getValue()
       to allow the resource associated with a name to be fetched. Overriding
       setup and teardown is optional.

       For convenience, .getNames() and .getValue() return the resources and
       names from a name <-> resource diciontary held in self._resources, but
       sub-classes should feel free to override these if necessary.
    """

    def getNames(self):
        """Return the names of the resources this Dimension object holds.
           Must be callable as soon as the object has been created.
        """
        return list(self._resources.keys())

    def getValue(self,name):
        """Return the value of a named resource.
           Need only be callable after the objects .setup() method has been called.
        """
        return self._resources[name]

    def getFailedConditions(self):
        """Return a dictionary mapping failed condition names to error messages
           Must be callable as soon as the object has been created
        """
        return getattr(self, "_failed_conditions", {})

    def getSkippedConditions(self):
        """Return a dictionary mapping failed condition names to error messages
           Must be callable as soon as the object has been created
        """
        return getattr(self, "_skipped_conditions", {})

    def setup(self):
        """Setup the held resources.
           Does nothing by default.
        """
        pass

    def teardown(self):
        """Clean-up and release the held resources.
           Does nothing by default.
        """
        pass

    def setup_method(self,varname):
        """Called before the resource varname is used in a test method.
        """
        pass

    def teardown_method(self,varname):
        """Called after the resource varname was used in a test method.
        """
        pass
