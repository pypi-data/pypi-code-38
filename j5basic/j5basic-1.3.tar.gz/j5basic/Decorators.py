#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Various decorators"""

# Copyright 2006 St James Software

import inspect, types, itertools
import logging
import time

#
# Utility Functions (for working with other functions)
#

def copyfunc(func): # not used internally
    "Creates an independent copy of a function."
    return types.FunctionType(func.__code__, func.__globals__, func.__name__,
                        func.__defaults__, func.__closure__)

def getrightargs(function, args):
    """Returns a dictionary of only the arguments which the callable takes out of the args.
       args is a dictionary as one might receive from accepting **kwargs for a function"""
    if not (inspect.isfunction(function) or inspect.ismethod(function)):
        # Try to find a function
        if not inspect.isclass(function):
            if hasattr(function, "__call__"):
                function = function.__call__
            else:
                raise ValueError("%s is not a function, method, class or object with a __call__ attribute")
        elif not hasattr(function, "__init__"):
            return {}
        else:
            function = function.__init__
    argnames, varargs, varkw, defaults = inspect.getargspec(function)
    if varkw == None:   # Can't accept random keywords
        newdict = {}
        for arg in argnames:
            if arg in args:
                newdict[arg] = args[arg]
            elif arg != "self" and (defaults is None or arg in argnames[:-len(defaults)]):      # If it doesn't have a default
                logging.warn("Lacking compulsory argument %s on callable %r - setting to None" % (arg, function))
                logging.debug("Full arg set = %r" % args)
                newdict[arg] = None
        return newdict
    return args


#
# decorator decorator (for making other decorators)
#

class decorator_helpers(object):
    """The basic trick is to generate the source code for a lambda function
       with the right signature and to evaluate it.
       Print lambda_src in _decorate to understand what is going on."""

    @staticmethod
    def getinfo(func, extendedargs=None):
        """Return an info dictionary containing:
           - name (the name of the function : str)
           - argnames (the names of the arguments : list)
           - defarg (the values of the default arguments : list)
           - fullsign (the full signature : str)
           - shortsign (the short signature : str)
           - arg0 ... argn (shortcuts for the names of the arguments)"""

        assert inspect.ismethod(func) or inspect.isfunction(func) or isinstance(func, classmethod), "getinfo can only be used with a function or class method"
        regargs, varargs, varkwargs, defaults = inspect.getargspec(func)
        if extendedargs:
            if defaults is None:
                defaults = []
            else:
                defaults = list(defaults)
            has_defaults = len(defaults) > 0
            for extendedarg in extendedargs:
                has_argdefault, argdefault = False, None
                if isinstance(extendedarg, tuple) and len(extendedarg) == 2:
                    argname, argdefault = extendedarg
                    has_argdefault = True
                elif isinstance(extendedarg, tuple) and len(extendedarg) == 1:
                    argname = extendedarg[0]
                elif isinstance(extendedarg, str):
                    argname = extendedarg
                else:
                    raise ValueError("Extended argument should be (keyword, default), (keyword,), or just keyword: got %r" % extendedarg)
                if has_defaults and not has_argdefault:
                    raise ValueError("Trying to add extended argument without defaults after arguments with defaults: %r" % (extendedarg,))
                existing_arg = argname in regargs
                if not existing_arg:
                    regargs.append(argname)
                if has_argdefault:
                    if existing_arg:
                        arg_pos = regargs.index(argname)
                        defaults_pos = len(regargs) - len(defaults)
                        # this can handle altering existing default values,
                        # or setting the default value for the last non-default value
                        # a number of non-default values can thus be set provided the order is right...
                        if defaults_pos <= arg_pos:
                            defaults[arg_pos - defaults_pos] = argdefault
                        elif defaults_pos == arg_pos + 1:
                            defaults.insert(0, argdefault)
                        else:
                            logging.debug("Couldn't add default to existing argument %s in function %s" % (argname, func.__name__))
                    else:
                        defaults.append(argdefault)
                    has_defaults = True
            defaults = tuple(defaults)
        argnames = list(regargs)
        if varargs: argnames.append(varargs)
        if varkwargs: argnames.append(varkwargs)
        counter = itertools.count()
        fullsign = inspect.formatargspec(
            regargs, varargs, varkwargs, defaults,
            formatvalue=lambda value: "=defarg[%i]" % next(counter))[1:-1]
        shortsign = inspect.formatargspec(
            regargs, varargs, varkwargs, defaults,
            formatvalue=lambda value: "")[1:-1]
        dic = dict(("arg%s" % n, name) for n, name in enumerate(argnames))
        dic.update(name=func.__name__, argnames=argnames, shortsign=shortsign,
            fullsign = fullsign, defarg = defaults or ())
        return dic

    @staticmethod
    def _contains_reserved_names(dic):
        return "_call_" in dic or "_func_" in dic

    @staticmethod
    def _decorate(func, caller, extendedargs=None, calling_frame_arg=None):
        """Takes a function and a caller and returns the function
           decorated with that caller. The decorated function is obtained
           by evaluating a lambda function with the correct signature.
           calling_frame_arg can be given as the name of an argument
           which should contain the calling function's stack frame"""
        infodict = decorator_helpers.getinfo(func, extendedargs)
        defaults = infodict["defarg"]
        assert not decorator_helpers._contains_reserved_names(infodict["argnames"]), \
               "You cannot use _call_ or _func_ as argument names!"
        execdict = dict(_func_=func, _call_=caller, defarg=defaults or ())
        if calling_frame_arg:
            # this uses inspect to pass the calling function's frame to the decorator
            if func.__name__ == "<lambda>":
                # we can't do assignment in a normal lambda, so we construct a function
                infodict["name"] = "lambda_wrapper"
            execdict["inspect"] = inspect
            infodict["calling_frame_arg"] = calling_frame_arg
            if calling_frame_arg in infodict["argnames"]:
                func_src = """def %(name)s(%(fullsign)s):
                %(calling_frame_arg)s = inspect.currentframe().f_back
                return _call_(_func_, %(shortsign)s)""" % infodict
            else:
                func_src = """def %(name)s(%(fullsign)s):
                %(calling_frame_arg)s = inspect.currentframe().f_back
                return _call_(_func_, %(shortsign)s, %(calling_frame_arg)s=%(calling_frame_arg)s)""" % infodict
            func_code = compile(func_src, func.__code__.co_filename, 'exec')
        elif func.__name__ == "<lambda>" and not calling_frame_arg:
            lambda_src = "lambda %(fullsign)s: _call_(_func_, %(shortsign)s)" \
                         % infodict
            func_code = compile(lambda_src, func.__code__.co_filename, 'eval')
        else:
            func_src = """def %(name)s(%(fullsign)s):
            return _call_(_func_, %(shortsign)s)""" % infodict
            func_code = compile(func_src, func.__code__.co_filename, 'exec')
        func_internal_code = func_code.co_consts[len(defaults or ())]
        dec_func = types.FunctionType(func_internal_code, execdict, func.__name__, defaults)
        dec_func.__doc__ = func.__doc__
        dec_func.__dict__ = func.__dict__
        return dec_func

class decorator(object):
    """General purpose decorator factory: takes a caller function as
       input and returns a decorator. extendedargs, if given is a list of
       keyword arguments and defaults that will be added to the function signature
       calling_frame_arg can be given as the name of an argument
       which should contain the calling function's stack frame
       A caller function is any function like this::

       def caller(func, *args, **kw):
           # do something
           return func(*args, **kw)

       Here is an example of usage:

           >>> @decorator
           ... def chatty(f, *args, **kw):
           ...     print "Calling %r" % f.__name__
           ...     return f(*args, **kw)

           >>> @chatty
           ... def g(): pass
           ...
           >>> g()
           Calling 'g'"""

    def __init__(self, caller, extendedargs=None, calling_frame_arg=None):
        self.caller = caller
        self.extendedargs = extendedargs or []
        self.calling_frame_arg = calling_frame_arg

    def __call__(self, func):
        return decorator_helpers._decorate(func, self.caller, self.extendedargs, self.calling_frame_arg)

def chain_decorators(*decorators):
    """returns a decorator that functions as the chain of the given decorators

    @chain_decorators(f1, f2, f3) is equivalent to:
    @f1
    @f2
    @f3"""
    @decorator
    def chained_decorator(f, *args, **kw):
        for decorator in reversed(decorators):
            f = decorator(f)
        return f(*args, **kw)
    return chained_decorator

#
# Decorators for Self Locking objects.
#

class SelfLocking(object):
    @staticmethod
    def runwithlock(f):
        """Can only be used on objects which have a self.lock (class or instance)
           attribute which supports the acquire() and release() methods.
           The decorator acquires self.lock, runs the method and releases the lock
           afterwards.

           Inside a method decorated with runwithlock, attempt to avoid calling other
           functions which obtain locks (including other methods wrapped with
           runwithlock). If you *really* have to do so, you are responsible for
           assuring that race conditions do not arise.  Ideally, methods wrapped with
           runwithlock (whatever functions they call) should do as little as possible,
           and preferrably nothing which has any chance of blocking for long periods of
           time (I/O, database queries, anything over a network, etc)."""

        def wrapper(self,*args,**kws):
            try:
                self.lock.acquire()
                ret = f(self,*args,**kws)
            finally:
                self.lock.release()
            return ret

        wrapper.__doc__ = f.__doc__
        wrapper.__name__ = getattr(f, 'func_name', getattr(f, '__name__', 'locked_function'))

        return wrapper

    @staticmethod
    def runwithnamedlock(lockname):
        def wrapper(f, self, *args, **kws):
            try:
                getattr(self, lockname).acquire()
                ret = f(self,*args,**kws)
            finally:
                getattr(self, lockname).release()
            return ret
        return decorator(wrapper)
#
# Decorator for unimplement methods
#

def notimplemented(f):
    """Takes a function f with a docstring and replaces it with a function which
       raises NotImplementedError(f.__doc__). Useful to avoid having to retype
       docstrings on methods designed to be overridden elsewhere."""

    def wrapper(self,*args,**kws):
        raise NotImplementedError(f.__doc__)

    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = f.__name__

    return wrapper

def wraptimer(function):
    """Log the time a function takes to run."""
    def timecall(self, *args, **kw):
        start_time = time.time()
        argstr = ", ".join([repr(arg) for arg in args]) + ", ".join(["%s=%r" % (kw, val) for kw, val in kw.items()])
        logging.debug("about to call %s(%s)" % (function.__name__, argstr))
        result = function(self, *args, **kw)
        end_time = time.time()
        logging.debug("call to %s(%s) took %0.2f seconds" % (function.__name__, argstr, end_time-start_time))
        return result
    timecall.__doc__ = function.__doc__
    return timecall

### helper methods for decorators to extract or alter arguments, and pass on the right thing to the decoratees

def override_arg(argname,value,args,kwargs,argspec):
    """overrides the given argname=value in args or kwargs as appropriate, returning (args, kwargs)"""
    if argname in kwargs:
        kwargs[argname] = value
        return (args, kwargs)
    regargs, varargs, varkwargs, defaults = argspec
    if argname in regargs:
        if isinstance(args, tuple):
            args = list(args)
        args[regargs.index(argname)] = value
    else:
        kwargs[argname] = value
    return (args, kwargs)

def get_or_pop_arg(argname,args,kwargs,argspec):
    """Finds the value of argname by looking in args and kwargs. Is argname
       is present in argspec then the value is simply returned. If argname
       is not present, the value is removed from arg or kwargs as appropriate.

       Note: If argname is not present in either argspec or kwargs then it is
             assumed to be the last element of args and is popped off (and added
             to kwargs if the argspec says a **keywords argument is present)."""
    regargs, varargs, varkwargs, defaults = argspec

    if argname in kwargs:
        if varkwargs is None and argname not in regargs:
            return kwargs.pop(argname)
        else:
            return kwargs[argname]
    elif argname not in regargs:
        if varkwargs is None:
            return args.pop()
        else:
            value = args.pop()
            kwargs[argname] = value
            return value
    else:
        return args[regargs.index(argname)]

# TODO: compare to getrightargs, see if any code can be merged

def conform_to_argspec(args,kwargs,argspec):
    """Attempts to take the arguments in arg and kwargs and return only those which can be used
       by the argspec given."""
    regargs, varargs, varkwargs, defaults = argspec
    N = len(regargs)

    # shallow copy arguments
    newargs = list(args)
    newkwargs = kwargs.copy()

    # Fill up as many regarg slots from *args as we can
    if varargs is None:
        newargs = newargs[:N]
    else:
        pass

    # Fill up the rest from **kwargs
    for varname in regargs[len(newargs):]:
        try:
            newargs.append(newkwargs[varname])
            del newkwargs[varname]
        except KeyError:
            # just leave the rest of the kwargs as they are and let Python raise an error later
            break

    # Handle remaining kwargs
    if varkwargs is None:
        newkwargs = {}
    else:
        pass

    return newargs, newkwargs

