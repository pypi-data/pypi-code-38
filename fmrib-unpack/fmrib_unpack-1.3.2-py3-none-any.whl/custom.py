#!/usr/bin/env python
#
# custom.py - Custom plugins for funpack.
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#
"""This module provides infrastructure for registering and accessing
``funpack`` plugins - custom functions for sniffing and loading data files,
and for cleaning and processing.


The following plugin types currently exist:


  +-------------------+-------------------------------------------------------+
  | Plugin type       |                                                       |
  +-------------------+-------------------------------------------------------|
  | ``sniffer``       | Return information about the columns in a file        |
  | ``loader``        | Load data from a file                                 |
  | ``cleaner``       | Run a cleaning function on a single column            |
  | ``processor``     | Run a processing function on one or more data columns |
  | ``metaproc``      | Run a function on a :class:`.Column` ``metadata``     |
  |                   | value                                                 |
  | ``formatter``     | Format a column for output                            |
  | ``exporter``      | Export the processed data set                         |
  +-------------------+-------------------------------------------------------+


To ensure that the ``funpack`` command line help is nicely formatted, all
plugin functions should have a docstring of the form::

    \"\"\"functionSignature(args)
    Short description of function.

    Extended description
    \"\"\"


.. autosummary::
   :nosignatures:

   clearRegistry
   loadPluginFile
   registerPlugin
   registerBuiltIns
   listPlugins
   exists
   get
   run
"""


import importlib.util as imputil
import os.path        as op
import functools      as ft
import                   re
import                   sys
import                   logging
import                   importlib
import                   collections


log = logging.getLogger(__name__)


PLUGIN_TYPES = ['loader',
                'sniffer',
                'formatter',
                'cleaner',
                'processor',
                'metaproc',
                'exporter']


class PluginRegistry(object):
    """The ``PluginRegistry`` keeps track of, and provides access to all
    registered plugins.
    """

    def __init__(self):
        """Create a ``PluginRegistry``. """

        self.clearRegistry()


    def clearRegistry(self):
        """Clears and resets the contents of the ``PluginRegistry``. """
        self.__plugins = collections.OrderedDict()

        for pt in PLUGIN_TYPES:

            self.__plugins[pt] = collections.OrderedDict()

            decorator = ft.partial(self.registerPlugin, pt)
            runner    = ft.partial(self.run,            pt)
            dname     = pt
            rname     = 'run{}'.format(pt.capitalize())

            setattr(self, dname, decorator)
            setattr(self, rname, runner)


    def registerPlugin(self, pluginType, pluginName=None):
        """Decorator to register a plugin. If name is not provided, the
        name of the decorated function is used.
        """

        if pluginType not in PLUGIN_TYPES:
            raise ValueError('Unsupported plugin type: {}'.format(pluginType))

        if pluginName in self.__plugins[pluginType]:
            log.warning('Overwriting existing {}: {}'.format(
                pluginType, pluginName))

        def wrapper(func):
            name = pluginName
            if name is None:
                name = func.__name__

            log.debug('Registering custom %s function: %s', pluginType, name)

            self.__plugins[pluginType][name] = func
            return func

        return wrapper


    def loadPluginFile(self, filename):
        """Loads the given file, assumed to be a Python module containing funpack
        plugin functions.
        """

        # If file does not exist, assume
        # it is a direct reference to a
        # file in the plugins directory.
        if not op.exists(filename):
            if not filename.endswith('.py'):
                filename = filename + '.py'
            moddir   = op.dirname(op.abspath(__file__))
            filename = op.join(moddir, 'plugins', filename)

        filename = op.abspath(filename)
        name     = re.sub('[^a-zA-Z]', '_', filename)

        log.debug('Loading custom plugin: %s [%s]', name, filename)

        spec = imputil.spec_from_file_location(name, filename)
        mod  = imputil.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # Make sure the plugin
        # contents can be pickled
        sys.modules[name] = mod


    def listPlugins(self, pluginType):
        """List plugins of the specified type. """
        return list(self.__plugins.get(pluginType, []))


    def exists(self, pluginType, pluginName):
        """Returns ``True`` if the given plugin exists, ``False`` otherwise.
        """
        return pluginName in self.__plugins.get(pluginType, [])

    def get(self, pluginType, pluginName):
        """Return a reference to the specified plugin. """
        return self.__plugins[pluginType][pluginName]


    def run(self, pluginType, pluginName, *args, **kwargs):
        """Run the specified plugin. """
        log.debug('Calling %s plugin function: %s', pluginType, pluginName)
        return self.__plugins[pluginType][pluginName](*args, **kwargs)


def registerBuiltIns():
    """Ensures that all built-in plugins are in the registry. """

    firstTime = len(registry.listPlugins('cleaner')) == 0

    import funpack.exporting            as ue
    import funpack.exporting_hdf5       as ueh5
    import funpack.exporting_tsv        as uet
    import funpack.cleaning_functions   as cf
    import funpack.processing_functions as pf
    import funpack.metaproc_functions   as mf

    if firstTime:
        loglevel = log.getEffectiveLevel()
        log.setLevel(logging.CRITICAL)

    importlib.reload(ue)
    importlib.reload(ueh5)
    importlib.reload(uet)
    importlib.reload(cf)
    importlib.reload(pf)
    importlib.reload(mf)

    if firstTime:
        log.setLevel(loglevel)


registry       = PluginRegistry()
clearRegistry  = registry.clearRegistry
loadPluginFile = registry.loadPluginFile
registerPlugin = registry.registerPlugin
listPlugins    = registry.listPlugins
exists         = registry.exists
get            = registry.get
run            = registry.run


for pt in PLUGIN_TYPES:
    decorator = pt
    runner    = 'run{}'.format(pt.capitalize())
    setattr(sys.modules[__name__], decorator, getattr(registry, decorator))
    setattr(sys.modules[__name__], runner,    getattr(registry, runner))
