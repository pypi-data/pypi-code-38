import logging
import inspect
import importlib
import re
from functools import reduce
from time import time
from zensols.actioncli import (
    Configurable,
    Stash,
)

logger = logging.getLogger(__name__)


class ClassImporter(object):
    """Utility class that reloads a module and instantiates a class from a string
    class name.  This is handy for prototyping code in a Python REPL.

    """
    CLASS_REGEX = re.compile(r'^(.+)\.(.+?)$')

    def __init__(self, class_name: str, reload: bool = True):
        """Initialize with the class name.

        :param class_name: the fully qualifed name of the class (including the
                           module portion of the class name)
        :param reload: if ``True`` then reload the module before returning the
        class
        """
        self.class_name = class_name
        self.reload = reload

    def parse_module_class(self):
        """Parse the module and class name part of the fully qualifed class name.

        """
        cname = self.class_name
        match = re.match(self.CLASS_REGEX, cname)
        if not match:
            raise ValueError(f'not a fully qualified class name: {cname}')
        return match.groups()

    def get_module_class(self):
        """Return the module and class as a tuple of the given class in the
        initializer.

        :param reload: if ``True`` then reload the module before returning the
        class

        """
        pkg, cname = self.parse_module_class()
        logger.debug(f'pkg: {pkg}, class: {cname}')
        pkg = pkg.split('.')
        mod = reduce(lambda m, n: getattr(m, n), pkg[1:], __import__(pkg[0]))
        logger.debug(f'mod: {mod}')
        if self.reload:
            importlib.reload(mod)
        cls = getattr(mod, cname)
        logger.debug(f'class: {cls}')
        return mod, cls

    def instance(self, *args, **kwargs):
        """Create an instance of the specified class in the initializer.

        :param args: the arguments given to the initializer of the new class
        :param kwargs: the keyword arguments given to the initializer of the
                     new class

        """
        mod, cls = self.get_module_class()
        inst = cls(*args, **kwargs)
        logger.debug(f'inst: {inst}')
        return inst

    def set_log_level(self, level=logging.INFO):
        """Convenciene method to set the log level of the module given in the
        initializer of this class.

        :param level: and instance of ``logging.<level>``
        """
        mod, cls = self.parse_module_class()
        logging.getLogger(mod).setLevel(level)


class ConfigFactory(object):
    """Creates new instances of classes and configures them given data in a
    configuration ``Config`` instance.

    :param config: an instance of ``Configurable``
    :param pattern: the pattern of the section/name identifier to get kwargs to
        initialize the new instance of the object
    """
    def __init__(self, config: Configurable, pattern='{name}',
                 config_param_name='config', name_param_name='name',
                 default_name='default'):
        """Initialize.

        :param config: the configuration used to create the instance; all data
            from the corresponding section is given to the ``__init__`` method

        :param pattern: section pattern used to find the values given to the
        ``__init__`` method

        :param config_param_name: the ``__init__`` parameter name used for the
            configuration object given to the factory's ``instance`` method;
            defaults to ``config``

        :param config_param_name: the ``__init__`` parameter name used for the
            instance name given to the factory's ``instance`` method; defaults
            to ``name``

        """
        self.config = config
        self.pattern = pattern
        self.config_param_name = config_param_name
        self.name_param_name = name_param_name
        self.default_name = default_name

    @classmethod
    def register(cls, instance_class, name=None):
        """Register a class with the factory.

        :param instance_class: the class to register with the factory (not a
            string)
        :param name: the name to use as the key for instance class lookups;
            defaults to the name of the class

        """
        if name is None:
            name = instance_class.__name__
        cls.INSTANCE_CLASSES[name] = instance_class

    def _find_class(self, class_name):
        "Resolve the class from the name."
        classes = {}
        classes.update(globals())
        classes.update(self.INSTANCE_CLASSES)
        logger.debug(f'looking up class: {class_name}')
        cls = classes[class_name]
        logger.debug(f'found class: {cls}')
        return cls

    def _class_name_params(self, name):
        "Get the class name and parameters to use for ``__init__``."
        sec = self.pattern.format(**{'name': name})
        logger.debug(f'section: {sec}')
        params = {}
        params.update(self.config.populate({}, section=sec))
        class_name = params['class_name']
        del params['class_name']
        return class_name, params

    def _has_init_config(self, cls):
        """Return whether the class has a ``config`` parameter in the ``__init__``
        method.

        """
        args = inspect.signature(cls.__init__)
        return self.config_param_name in args.parameters

    def _has_init_name(self, cls):
        """Return whether the class has a ``name`` parameter in the ``__init__``
        method.

        """
        args = inspect.signature(cls.__init__)
        return self.name_param_name in args.parameters

    def _instance(self, cls, *args, **kwargs):
        """Return the instance.

        :param cls: the class to create the instance from
        :param args: given to the ``__init__`` method
        :param kwargs: given to the ``__init__`` method
        """
        logger.debug(f'args: {args}, kwargs: {kwargs}')
        return cls(*args, **kwargs)

    def instance(self, name=None, *args, **kwargs):
        """Create a new instance using key ``name``.

        :param name: the name of the class (by default) or the key name of the
            class used to find the class
        :param args: given to the ``__init__`` method
        :param kwargs: given to the ``__init__`` method

        """
        logger.info(f'new instance of {name}')
        t0 = time()
        name = self.default_name if name is None else name
        logger.debug(f'creating instance of {name}')
        class_name, params = self._class_name_params(name)
        cls = self._find_class(class_name)
        params.update(kwargs)
        if self._has_init_config(cls):
            logger.debug(f'found config parameter')
            params['config'] = self.config
        if self._has_init_name(cls):
            logger.debug(f'found name parameter')
            params['name'] = name
        if logger.level >= logging.DEBUG:
            for k, v in params.items():
                logger.debug(f'populating {k} -> {v} ({type(v)})')
        inst = self._instance(cls, *args, **params)
        logger.info(f'created {name} instance of {cls.__name__} ' +
                    f'in {(time() - t0):.2f}s')
        return inst


class ConfigManager(ConfigFactory):
    """Like ``ConfigFactory`` base saves off instances (really CRUDs).

    """
    def __init__(self, config: Configurable, stash: Stash, *args, **kwargs):
        """Initialize.

        :param config: the configuration object used to configure the new
            instance
        :param stash: the stash object used to persist instances

        """
        super(ConfigManager, self).__init__(config, *args, **kwargs)
        self.stash = stash

    def load(self, name=None, *args, **kwargs):
        "Load the instance of the object from the stash."
        inst = self.stash.load(name)
        if inst is None:
            inst = self.instance(name, *args, **kwargs)
        logger.debug(f'loaded (conf mng) instance: {inst}')
        return inst

    def exists(self, name: str):
        "Return ``True`` if data with key ``name`` exists."
        return self.stash.exists(name)

    def keys(self):
        """Return an iterable of keys in the collection."""
        return self.stash.keys()

    def dump(self, name: str, inst):
        "Save the object instance to the stash."
        self.stash.dump(name, inst)

    def delete(self, name=None):
        "Delete the object instance from the backing store."
        self.stash.delete(name)


class SingleClassConfigManager(ConfigManager):
    """A configuration manager that specifies a single class.  This is useful when
    you don't want to specify the class in the configuration.

    """
    def __init__(self, config: Configurable, cls, *args, **kwargs):
        """Initialize.

        :param config: the configuration object
        :param cls: the class used to create each instance
        """
        super(SingleClassConfigManager, self).__init__(config, *args, **kwargs)
        self.cls = cls

    def _find_class(self, class_name):
        return self.cls

    def _class_name_params(self, name):
        sec = self.pattern.format(**{'name': name})
        logger.debug(f'section: {sec}')
        params = {}
        params.update(self.config.populate({}, section=sec))
        return None, params


class CachingConfigFactory(object):
    """Just like ``ConfigFactory`` but caches instances in memory by name.

    """
    def __init__(self, delegate: ConfigFactory):
        """Initialize.

        :param delegate: the delegate factory to use for the actual instance
            creation

        """
        self.delegate = delegate
        self.insts = {}

    def instance(self, name=None, *args, **kwargs):
        logger.debug(f'cache config instance for {name}')
        if name in self.insts:
            logger.debug(f'reusing cached instance of {name}')
            return self.insts[name]
        else:
            logger.debug(f'creating new instance of {name}')
            inst = self.delegate.instance(name, *args, **kwargs)
            self.insts[name] = inst
            return inst

    def load(self, name=None, *args, **kwargs):
        if name in self.insts:
            logger.debug(f'reusing (load) cached instance of {name}')
            return self.insts[name]
        else:
            logger.debug(f'load new instance of {name}')
            inst = self.delegate.load(name, *args, **kwargs)
            self.insts[name] = inst
            return inst

    def exists(self, name: str):
        return self.delegate.exists(name)

    def dump(self, name: str, inst):
        self.delegate.dump(name, inst)

    def delete(self, name):
        self.delegate.delete(name)
        self.evict(name)

    def evict(self, name):
        if name in self.insts:
            del self.insts[name]

    def evict_all(self):
        self.insts.clear()
