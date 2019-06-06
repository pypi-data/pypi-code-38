import importlib
from collections import defaultdict

from pyqalx.core.entities import QalxEntity
from pyqalx.core.errors import QalxAlreadyRegistered, QalxIncorrectEntityType, \
    QalxCannotUnregister, QalxRegistrationClassNotFound


class Registry(defaultdict):

    def __init__(self, *args, **kwargs):
        super(Registry, self).__init__(*args, **kwargs)

        # Registry but always be a `dict`
        self.default_factory = dict
        # The classes that we allow to be registered.  Only classes defined
        # here will get registered by the system.
        self.registration_classes = [EntityRegistry, ]

    def _register_defaults(self):
        """
        Iterates the valid classes that we allow to register and registers
        the defaults that are defined by pyqalx itself
        """
        for registration_class in self.registration_classes:
            register_class = registration_class()

            for default_class in register_class._get_defaults():
                register_class.register(cls=default_class)
            self.update(register_class)

    @property
    def base_class(self):
        """
        The base class is used to prove registry subclass level validation
        on the class being registered
        :raises: NotImplementedError
        """
        raise NotImplementedError('`base_class` must be defined on '
                                  'implementing class')

    def _lookup_key(self, cls):
        """
        The key to use to uniquely identify the registered class
        :param cls: The class to register
        :raises: NotImplementedError
        """
        raise NotImplementedError('`lookup_key` must be defined on '
                                  'implementing class')

    def _get_package(self, cls):
        """
        Gets the package the given class is in
        :param cls: The class to get the package for (i.e. `QalxItem`)
        :return: The package in dot notation (i.e. `pyqalx.core.entities`)
        """
        return importlib.import_module(cls.__module__).__package__

    def _get_defaults(self, _cls=None):
        """
        Recursively gets all default subclasses of the registrys `base_class`
        """
        all_subclasses = set()

        def _append_subclasses(_subclasses):
            # Adapters without an `entity_class` (such as
            # `QalxUnpackableAdapter` should be disregarded)
            for _subclass in _subclasses:
                # if hasattr(_subclass, 'entity_class'):
                all_subclasses.add(_subclass)
            return all_subclasses

        if _cls is None:
            _cls = self.base_class
        package = self._get_package(self.base_class)

        for subclass in _cls.__subclasses__():
            subclass_package = self._get_package(subclass)

            if subclass_package == package:
                all_subclasses = _append_subclasses([subclass])
                subclasses = self._get_defaults(_cls=subclass)
                all_subclasses = _append_subclasses(subclasses)
        return all_subclasses

    @property
    def _registry_key(self):
        """
        The key to group similar registered classes.
        Uses the right most part of the package name
        :return: Given `pyqalx.core.entities` as a package will return
                 `entities`
        """
        return self._get_package(cls=self.base_class).rsplit('.', 1)[1]

    def _get_registry_class(self, cls):
        """
        Determines the registry class to use based on the given cls. We need
        a specific registry class to perform specific validation
        :param cls: The class to get the registry class for.
        :return: The specific registry subclass
        :raises: QalxRegistrationClassNotFound
        """
        registry_class = None
        for registration_class in self.registration_classes:
            if issubclass(cls, registration_class.base_class):
                registry_class = registration_class()
                break

        if registry_class is None:
            valid_base_classes = [str(x.base_class) for x in self.registration_classes]
            msg = f'Could not find registration class for `{cls}`.  Ensure ' \
                f'that you are registering a class which is a subclass of' \
                f' `{", ".join(valid_base_classes)}`'
            raise QalxRegistrationClassNotFound(msg)
        return registry_class

    def _validate(self, cls):
        """
        Hook for providing registry class level validation
        """
        return

    @property
    def registered_classes(self):
        """
        A list of the current registered classes for the `registry_key`
        """
        registered_classes = []
        for _cls in self[self._registry_key].values():
            registered_classes.append(_cls)
        return registered_classes

    def register(self, cls):
        """
        Register the given class to the registry.
        :param cls: The subclass to be registered
        :raises: QalxInvalidSubclass
        :raises: QalxAlreadyRegistered
        """
        RegistrationClass = self
        if type(self) == Registry:
            # A `QalxSession` registers via a `Registry()` instance so we
            # need to lookup the specific registry class here to be able to
            # be able to perform validation
            RegistrationClass = self._get_registry_class(cls)
        lookup_key = RegistrationClass._lookup_key(cls)

        # Handle registry level validation
        RegistrationClass._validate(cls)

        if cls in self[RegistrationClass._registry_key].values():
            raise QalxAlreadyRegistered(f'{cls} is already registered')
        # Register the class to the specific `_registry` and `lookup` keys
        self[RegistrationClass._registry_key][lookup_key] = cls

    def unregister(self, cls):
        """
        Unregisters the given adapter_class and reregisters the default
        value
        :param cls: The class you want to unregister
        :raises: QalxCannotUnregister
        """
        RegistrationClass = self._get_registry_class(cls)
        if RegistrationClass._get_package(cls) == RegistrationClass._get_package(RegistrationClass.base_class):
            # Prevent deregistration of default adapters
            raise QalxCannotUnregister(f'You cannot unregister default '
                                       f'class `{cls}`')

        for default_class in RegistrationClass._get_defaults():
            if issubclass(cls, default_class):
                # reregister the default
                self[RegistrationClass._registry_key][RegistrationClass._lookup_key(default_class)] = default_class


class EntityRegistry(Registry):
    base_class = QalxEntity

    def _validate(self, cls):
        entity_type = getattr(cls, 'entity_type', None)

        if not entity_type:
            raise QalxIncorrectEntityType(f'{cls} must have an '
                                          f'attribute `entity_type` set')

    def _lookup_key(self, cls):
        """
        The key to use to uniquely identify the registered class
        :param cls: The class to register
        :returns: cls.entity_type
        """
        return cls.entity_type
