#!/usr/bin/env python

import logging
import os
import pkgutil
import sys
import six

importedmodules = {}

def find_module(modulename):
    """finds the filename of the module with the given name (supports submodules)"""
    module_parts = modulename.split(".")
    search_path = None
    for i, part in enumerate(module_parts):
        search_module = ".".join(module_parts[:i+1])
        try:
            loader = pkgutil.find_loader(search_module)
            if loader is None:
                raise ImportError(search_module)
            search_path = loader.get_filename(search_module)
        except ImportError:
            raise ValueError("Could not find %s (reached %s at %s)" % (modulename, part, search_path))
    if search_path.endswith(os.sep + "__init__.py"):
        return search_path[:-len(os.sep + "__init__.py")]
    return search_path

def resolvemodule(modulename, loglevel=logging.WARN):
    """Imports a.b.c as far as possible then returns the value of a.b.c.d.e"""
    if modulename in importedmodules:
        return importedmodules[modulename]

    try:
        parentmodule = getimportablemodule(modulename, loglevel)
    except (ImportError, SyntaxError) as e:
        logging.log(loglevel, "Could not import module for %s" % (modulename))
        raise
    try:
        module = getpart(parentmodule, modulename)
    except AttributeError as e:
        logging.log(loglevel, "Could not resolve modulename %s" % (modulename))
        raise
    importedmodules[modulename] = module
    return module

def canonicalize(path):
    """returns the canonical reference to the path that can be used for comparison to other paths"""
    return os.path.normpath(os.path.realpath(os.path.abspath(path)))

thisfilename = canonicalize(__file__)
if thisfilename.endswith(".pyc") or thisfilename.endswith(".pyo"):
    thisfilename = thisfilename[:-1]

def getimportablemodule(modulename, loglevel=logging.WARN):
    """Attempts to import successive modules on the a.b.c route - first a.b.c, then a.b, etc. Only goes one level up"""
    components = modulename.split('.')
    module = None
    component_depth = len(components)
    errormessage = ""
    if component_depth > 1:
        parentmodulename = ".".join(components[:-1])
        try:
            parentmodule = __import__(parentmodulename)
        except ImportError as error:
            # if we get an import error on the parent module, we're unlikely to be able to import the child
            logging.log(loglevel, "Import Error attempting to import %s (parent of %s): %s" % (parentmodulename, modulename, error))
            raise
        except Exception as error:
            logging.log(loglevel, "Error attempting to import %s: %s" % (parentmodulename, error))
            raise
    try:
        module = __import__(modulename)
        return module
    except ImportError as error:
        if component_depth > 1:
            actualparentmodule = sys.modules[parentmodulename]
            moduleattr = components[-1]
            if hasattr(actualparentmodule, moduleattr):
                logging.debug("Import Error attempting to import %s (but have parent module to return which has %s as attribute): %s" % (modulename, moduleattr, error))
                return parentmodule
        logging.log(loglevel, "Error attempting to import %s: %s" % (modulename, error))
        raise
    except Exception as error:
        logging.log(loglevel, "Error attempting to import %s: %s" % (modulename, error))
        raise

def getpart(module, partname):
    components = partname.split('.')
    for component in components[1:]:
        module = getattr(module, component)
    return module

def get_all_distinct_mro_targets(obj, functionname):
    """Gets a list of all distinct instances of functionname in the mro"""
    targets = []
    sources = {}
    for t in reversed(obj.__mro__):
        base_hook_fn = getattr(t, functionname, None)
        if base_hook_fn:
            t_f = six.get_unbound_function(base_hook_fn)
            if t_f not in sources:
                sources[t_f] = t
                sources[t] = (t_f, base_hook_fn)
                targets.append(base_hook_fn)
                for base in t.__mro__[1:]:
                    if base in sources:
                        r_f, r_m = sources[base]
                        if r_m in targets:
                            targets.remove(r_m)
    return list(reversed(targets))

