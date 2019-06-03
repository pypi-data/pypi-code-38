from abc import ABC, abstractmethod

from . import name_of, DescDict, id_name_of


__author__ = 'Jake'
__all__ = ['DescriptorStorage', 'InstanceStorage', 'DictStorage', 'identity',
           'protected', 'hex_desc_id']


class DescriptorStorage(ABC):
    """
    :DescriptorStorage is an abstract base class of a set of classes that are
    meant to store data for descriptors. Their primary usage is like using a
    dictionary with the instance as the key, but they also have a few extra
    pieces that make using them in descriptors a little easier. For one, they
    can provide proper `AttributeError`s instead of `KeyError`s so descriptors
    may not need to. Secondly, the storage also stores the attribute name for
    the descriptor.

    To accomplish these, though, there are certain rules that have to be followed.
    The first two are easy, and are likely what you were doing to begin with:

    1. An instance of a :DescriptorStorage can only be used on a single
        descriptor
    2. The descriptor instance the :DescriptorStorage is used on must only be
        used on a single class

    The third rule is much less obvious, but can be pretty easy:

    3. In order for the :DescriptorStorage instance to get the name of the
        attribute the descriptor is stored on, one of three things must happen:

        + `set_name()` must be called by the descriptor before any of the other
            methods. A great time to use this is in the descriptor's
            `__set_name__()` method, but that's not available in versions before
            3.6.
        + The instance of the descriptor must be passed into the constructor.
            This should work if the :DescriptorStorage is being hard-coded into
            the descriptor, but it's impossible if the :DescriptorStorage is
            being injected into the descriptor's constructor, like for
            `descriptor_tools.instance_properties.InstanceProperty`s. Thus, the
            third option.
        + The instance of the descriptor must be assigned to the `desc` attribute
            of the :DescriptorStorage before any methods are called.

    Those options are in order of preference. If the descriptor you're writing
    will only be used in versions 3.6+, then you'd only need to use `set_name()`
    from a `__set_name__()` method. If it will be used in a variety of versions
    (minimum version for this library is 3.3), then I would still include that
    (it's the most effecient way) as well as one of the ways of setting the
    `desc` attribute.
    """
    def __init__(self, desc=None):
        """
        Initialize the :DescriptorStorage object
        :param desc: (optional) can set the descriptor object immediately.
        """
        self.desc = desc
        self.base_name = None

    def name(self, instance):
        """
        Look up the name of the attribute the hosting descriptor is stored under.

        Requires that `set_name()` has been called before this or that the `desc`
        attribute has been assigned the host descriptor. Using `set_name()` is
        preferred and faster, but is not always possible.
        :param instance: object to look up the name through, if necessary.
        :return: name of the attribute the hosting descriptor is stored under
        """
        if self.base_name is None:
            self.set_name(name_of(self.desc, type(instance)))
        return self.base_name

    def set_name(self, name):
        """
        Sets the name attribute so looking it up with `name()` can be quicker.

        Is also called by `name()` when the name is looked up.

        Avoid overriding. If you do override, be certain that the `base_name`
        attribute is set to the name by either doing a `super()` call into this
        implementation or doing it yourself.
        :param name: name of the attribute the host descriptor is stored on
        """
        self.base_name = name

    @abstractmethod
    def __getitem__(self, instance):
        """
        Using the instance as a key, looks up the value stored for the host
        descriptor for the instance's attribute.
        :param instance: instance to look up the value for
        :return: value stored for the host descriptor
        """
        ...

    @abstractmethod
    def __setitem__(self, instance, value):
        """
        Using the instance as a key, store the value for the attribute the host
        descriptor represents.
        :param instance: instance to store the value for
        :param value: value to store for the host descriptor
        """
        ...

    @abstractmethod
    def __delitem__(self, instance):
        """
        Removes the given instance key and its associated value from this
        storage
        :param instance: instance to remove the attribute from
        """
        ...

    @abstractmethod
    def __contains__(self, instance):
        """
        Checks whether the given instance has a value stored for it
        :param instance: instance to check
        :return: `True` if there is an associated value for the given instance,
        `False` otherwise
        """
        ...

    def _raise_no_attr(self, instance):
        """
        Raises an :AttributeError with the message "Attribute '<attr name>' does
        not exist on object <obj string>". This is useful when looking up and
        deleting a value from the collection that doesn't exist.
        :param instance:
        :raises: :AttributeError
        """
        msg = "Attribute '{}' does not exist on object {}"
        raise AttributeError(msg.format(self.name(instance), instance))


class DictStorage(DescriptorStorage):
    """
    :DictStorage is a kind of :DescriptorStorage that uses :DescDict as the
    storage medium. As a :DescriptorStorage, usage of the :InstanceStorage must
    follow the strict guidelines provided in the :DescriptorStorage documentation.
    """

    def __init__(self, desc=None):
        super().__init__(desc)
        self.store = DescDict()

    def __getitem__(self, instance):
        try:
            return self.store[instance]
        except KeyError:
            self._raise_no_attr(instance)

    def __setitem__(self, instance, value):
        self.store[instance] = value

    def __delitem__(self, instance):
        try:
            del self.store[instance]
        except KeyError:
            self._raise_no_attr(instance)

    def __contains__(self, instance):
        return instance in self.store


def identity(name, _):
    """
    Name-generating/mangling function that simply returns the name given it
    :param name: name of the attribute the host descriptor is stored under
    :param _: (unused) - the descriptor object the name is being generated/
    mangled for
    :return: `name`
    """
    return name


def protected(name, _):
    """
    Name-generating/mangling function that returns the name given it with an '_'
    prefix to mark it as "protected"
    :param name: name of the attribute the host descriptor is stored under
    :param _: (unused) - the descriptor object the name is being generated/
    mangled for
    :return: `name` with an '_' prefix
    """
    return "_"+name


def hex_desc_id(_, desc):
    """
    Name-generating/mangling function that returns the id of the descriptor
    given, formatted in hex with the leading '0' from the '0x' removed
    :param _: (unused) - name of the attribute the host descriptor is stored
    under
    :param desc: the descriptor object the name is being generated/mangled for
    :return: result of `id_name_of(desc)`
    """
    return id_name_of(desc)


class InstanceStorage(DescriptorStorage):
    # Do not use on more than one descriptor
    # Be certain to either call set_name or, if that can't be guaranteed, set
    #   the 'desc' attribute to the descriptor instance.
    """
    :InstanceStorage is a type of :DescriptorStorage that stores the value on the
    instance itself. As a :DescriptorStorage, usage of the :InstanceStorage must
    follow the strict guidelines provided in the :DescriptorStorage documentation.

    Since :InstanceStorage stores the values on the instance itself, a suitable
    location to store the value must be found. By default, it stores it under
    the same name the host descriptor is stored under. If you'd like to change
    this behavior, pass a name mangler function into the constructor, as explained
    in the __init__ docs.
    """

    def __init__(self, name_mangler=identity, desc=None):
        """
        Initialize the :InstanceStorage object.

        If passing in a name_mangler function, in must adhere to the following
        contract: (str, descriptor) -> str. The first parameter is the name the
        host descriptor is stored under. Some built-in functions are provided:
        `identity()`(default), `protected()`, and `hex_desc_id()`
        :param name_mangler: (defaults to `identity()`) - a function that
        provides a "mangled" name to store the value under on the instance
        :param desc: (optional) - can set the descriptor object immediately
        """
        super().__init__(desc)
        self._name = None
        self._mangler = name_mangler

    def mangled_name(self, instance):
        """
        Works just like `name()`, except it looks up the mangled version of the
        name
        :param instance: object to look up the name through, if necessary
        :return: mangled version of the name
        """
        if self._name is None:
            super().name(instance)
        return self._name

    def set_name(self, name):
        """
        Sets the name attribute so looking it up with `name()` can be quicker.
        Also sets the mangled name.

        Is also called by `name()` when the name is looked up.

        Avoid overriding. If you do override, be certain that the `base_name`
        attribute is set to the name by either doing a `super()` call into this
        implementation or doing it yourself.
        :param name: name of the attribute the host descriptor is stored on
        """
        super().set_name(name)
        self._name = self._mangler(name, self)

    def __getitem__(self, instance):
        try:
            return vars(instance)[self.mangled_name(instance)]
        except KeyError:
            self._raise_no_attr(instance)

    def __setitem__(self, instance, value):
        vars(instance)[self.mangled_name(instance)] = value

    def __delitem__(self, instance):
        try:
            del vars(instance)[self.mangled_name(instance)]
        except KeyError:
            self._raise_no_attr(instance)

    def __contains__(self, instance):
        return self.mangled_name(instance) in vars(instance)
