from collections import OrderedDict

from ievv_opensource.utils.singleton import Singleton


class DuplicateKeyError(Exception):
    """
    Raised when adding a key already in a :class:`.ClassRegistrySingleton`
    """
    def __init__(self, registry, key):
        self.registry = registry
        self.key = key
        message = f'Duplicate key, {key!r}, in {registry.get_pretty_classpath()}.'
        super(DuplicateKeyError, self).__init__(message)


class AbstractRegistryItem:
    """
    Base class for :class:`.ClassRegistrySingleton` items.
    """
    @classmethod
    def get_registry_key(cls):
        raise NotImplementedError()

    @property
    def registry_key(self):
        return self.__class__.get_registry_key()

    @classmethod
    def on_add_to_registry(cls, registry):
        """
        Called automatically when the class is added to a :class:`.ClassRegistrySingleton`.
        """

    @classmethod
    def on_remove_from_registry(cls, registry):
        """
        Called automatically when the class is removed from a :class:`.ClassRegistrySingleton`.
        """


class RegistryItemWrapper:
    """
    Registry item wrapper.

    When you add a :class:`.AbstractRegistryItem` to a :class:`.ClassRegistrySingleton`,
    it is stored as an instance of this class.

    You can use a subclass of this class with your registry singleton by overriding
    :meth:`.ClassRegistrySingleton.get_registry_item_wrapper_class`. This enables
    you to store extra metadata along with your registry items, and provided
    extra helper methods.
    """
    def __init__(self, cls, default_instance_kwargs):
        #: The :class:`.AbstractRegistryItem` class.
        self.cls = cls

        #: The default kwargs for instance created with :meth:`.get_instance`.
        self.default_instance_kwargs = default_instance_kwargs

    def make_instance_kwargs(self, kwargs):
        """
        Used by :meth:`.get_instance` to merge ``kwargs`` with ``default_instance_kwargs``.

        Returns:
            dict: The full kwargs fo the instance.
        """
        full_kwargs = {}
        full_kwargs.update(self.default_instance_kwargs)
        full_kwargs.update(kwargs)
        return full_kwargs

    def get_instance(self, **kwargs):
        """
        Get an instance of the :class:`.AbstractRegistryItem`
        class initialized with the provided ``**kwargs``.

        The provided ``**kwargs`` is merged with the ``default_instance_kwargs``,
        with ``**kwargs`` overriding any keys also in ``default_instance_kwargs``.

        Args:
            **kwargs: Kwargs for the class constructor.

        Returns:
            .AbstractRegistryItem: A class instance.
        """
        return self.cls(**self.make_instance_kwargs(kwargs))


class ClassRegistrySingleton(Singleton):
    """
    Base class for class registry singletons - for having a singleton
    of swappable classes. Useful when creating complex libraries with
    classes that the apps using the libraries should be able to swap out
    with their own classes.

    Example::

        class AbstractMessageGenerator(class_registry_singleton.AbstractRegistryItem):
            def get_message(self):
                raise NotImplementedError()


        class SimpleSadMessageGenerator(AbstractMessageGenerator):
            @classmethod
            def get_registry_key(cls):
                return 'sad'

            def get_message(self):
                return 'A sad message'

        class ComplexSadMessageGenerator(AbstractMessageGenerator):
            @classmethod
            def get_registry_key(cls):
                return 'sad'

            def get_message(self):
                return random.choice([
                    'Most people are smart, but 60% of people think they are smart.',
                    'Humanity will probably die off before we become a multi-planet spiecies.',
                    'We could feed everyone in the world - if we just bothered to share resources.',
                ])

        class SimpleHappyMessageGenerator(AbstractMessageGenerator):
            @classmethod
            def get_registry_key(cls):
                return 'happy'

            def get_message(self):
                return 'A happy message'

        class ComplexHappyMessageGenerator(AbstractMessageGenerator):
            @classmethod
            def get_registry_key(cls):
                return 'happy'

            def get_message(self):
                return random.choice([
                    'Almost every person you will ever meet are good people.',
                    'You will very likely live to see people land on mars.',
                    'Games are good now - just think how good they will be in 10 years!',
                ])

        class MessageGeneratorSingleton(class_registry_singleton.ClassRegistrySingleton):
            ''''
            We never use ClassRegistrySingleton directly - we always create a subclass. This is because
            of the nature of singletons. If you ise ClassRegistrySingleton directly as your singleton,
            everything added to the registry would be in THE SAME singleton.
            ''''


        class DefaultAppConfig(AppConfig):
            def ready(self):
                registry = MessageGeneratorSingleton.get_instance()
                registry.add(SimpleSadMessageGenerator)
                registry.add(SimpleHappyMessageGenerator)


        class SomeCustomAppConfig(AppConfig):
            def ready(self):
                registry = MessageGeneratorSingleton.get_instance()
                registry.add_or_replace(ComplexSadMessageGenerator)
                registry.add_or_replace(ComplexHappyMessageGenerator)


        # Using the singleton in code
        registry = MessageGeneratorSingleton.get_instance()
        print(registry.get_registry_item_instance('sad').get_message())
        print(registry.get_registry_item_instance('happy').get_message())
    """

    def __init__(self):
        super().__init__()
        self._classmap = OrderedDict()

    def get_registry_item_wrapper_class(self):
        """
        Get the registry item wrapper class.

        Defaults to :class:`.RegistryItemWrapper` which should work well for
        most use cases.
        """
        return RegistryItemWrapper

    def get_pretty_classpath(self):
        return '{}.{}'.format(self.__module__, self.__class__.__name__)

    def __getitem__(self, key):
        """
        Get a class (wrapper) stored in the registry by its key.

        Args:
            key (str): The key.

        Raises:
            KeyError: When the ``key`` is not in the registry.

        Returns:
            .RegistryItemWrapper: You can use this to get the class or to get an instance of the class.
        """
        return self._classmap[key]

    def get(self, key, fallback=None):
        """
        Get a class (wrapper) stored in the registry by its key.

        Args:
            key (str): A registry item class key.
            fallback: Fallback value of the ``key`` is not in the registry

        Returns:

        Returns:
            .RegistryItemWrapper: You can use this to get the class or to get an instance of the class.

        """
        if key in self:
            return self[key]
        return fallback

    def __contains__(self, key):
        return key in self._classmap

    def __iter__(self):
        """
        Iterate over all the keys in the registry.
        """
        return iter(self._classmap)

    def items(self):
        """
        Iterate over all the items in the registry yielding (key, RegistryItemWrapper)
        tuples.
        """
        return self._classmap.items()

    def iterwrappers(self):
        """
        Iterate over all the items in the registry yielding RegistryItemWrapper
        objects.
        """
        return self._classmap.values()

    def iterchoices(self):
        """
        Iterate over the the classes in the
        in the registry yielding two-value tuples where both values are the
        :obj:`~.AbstractRegistryItem.get_registry_key()`.

        Useful when rendering in a ChoiceField.

        Returns:
            An iterator that yields ``(<key>, <key>)`` tuples for each
            :class:`.AbstractRegistryItem`
            in the registry. The iterator is sorted by
            :obj:`~.AbstractRegistryItem.get_registry_key()`.
        """
        for cls in sorted(self._classmap.values(), key=lambda wrapper: wrapper.cls.get_registry_key()):
            yield (cls.get_registry_key(),
                   cls.get_registry_key())

    def _set(self, cls, **default_instance_kwargs):
        key = cls.get_registry_key()
        if key in self._classmap:
            self._classmap[key].cls.on_remove_from_registry(registry=self)
        self._classmap[key] = RegistryItemWrapper(
            cls=cls, default_instance_kwargs=default_instance_kwargs)
        self._classmap[key].cls.on_add_to_registry(registry=self)

    def add(self, cls, **default_instance_kwargs):
        """
        Add the provided ``cls`` to the registry.
        Args:
            cls: A :class:`.AbstractRegistryItem` class (NOT AN OBJECT/INSTANCE).
            **default_instance_kwargs: Default instance kwargs.
        Raises:
            .DuplicateKeyError: When a class with the same
            :obj:`~.AbstractRegistryItem.get_registry_key()` is already
            in the registry.
        """
        key = cls.get_registry_key()
        if key in self._classmap:
            raise DuplicateKeyError(
                registry=self,
                key=key)
        self._set(cls, **default_instance_kwargs)

    def add_or_replace(self, cls, **default_instance_kwargs):
        """
        Insert the provided ``cls`` in registry.
        If another ``cls`` is already
        registered with the same ``key``, this will be replaced.

        Args:
            cls: A :class:`.AbstractRegistryItem` class (NOT AN OBJECT/INSTANCE).
            **default_instance_kwargs: Default instance kwargs.
        """
        self._set(cls, **default_instance_kwargs)

    def replace(self, cls, **default_instance_kwargs):
        """
        Replace the class currently in the registry with the same key
        as the provided ``cls.get_registry_key()``.

        Args:
            cls: A :class:`.AbstractRegistryItem` class (NOT AN OBJECT/INSTANCE).
            **default_instance_kwargs: Default instance kwargs.

        Raises:
            KeyError: If the ``cls.get_registry_key()`` is NOT in the registry.
        """
        key = cls.get_registry_key()
        if key not in self._classmap:
            raise KeyError(f'{key!r} is not in the registry.')
        self._set(cls, **default_instance_kwargs)

    def remove(self, key):
        """
        Remove the class provided ``key`` from the registry.

        Args:
            key (str): A
            :obj:`~.AbstractRegistryItem.get_registry_key()`.
        Raises:
            KeyError: When the ``key`` is not in the registry.
        """
        if key not in self:
            raise KeyError
        self._classmap[key].cls.on_remove_from_registry(registry=self)
        del self._classmap[key]

    def remove_if_in_registry(self, key):
        """
        Works just like :meth:`.remove`, but if the ``key`` is not in the registry
        this method just does nothing instead of raising KeyError.
        """
        if key not in self:
            return
        self.remove(key)

    def get_registry_item_instance(self, key, **kwargs):
        """
        Just a shortcut for ``singleton[key].get_instance(**kwargs)``.
        """
        return self[key].get_instance(**kwargs)
