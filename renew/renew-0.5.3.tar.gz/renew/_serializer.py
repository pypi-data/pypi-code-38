import codecs
import contextlib
import importlib
import inspect
import os
import re
import sys

from renew import _py_lang


def write_file(output_file_path, content, makedirs=False):
    parent_dir = os.path.dirname(output_file_path)

    if makedirs:
        _make_dirs(parent_dir)
    else:
        if not os.path.isdir(parent_dir):
            raise ValueError("Target dir does not exist: {!r}.".format(parent_dir))

    with codecs.open(output_file_path, 'w', encoding="utf-8") as f:
        return f.write(content)


def _make_dirs(directory_path):
    if not os.path.isdir(directory_path):
        assert not os.path.exists(directory_path), "Path for parent dir already taken: %r." % directory_path
        os.makedirs(directory_path)


def _import_from_path(path_to_py_module):
    if not isinstance(path_to_py_module, str):
        raise TypeError("Expecting path to be a string.")

    if os.path.exists(path_to_py_module):
        import_dir_path, package_name = _split_path_and_name(path_to_py_module)
        with _supplementing_sys_path(import_dir_path):
            try:
                return importlib.import_module(package_name)
            except Exception as e:
                msg = "Renew: Failed to load a %r although it's db package file exists in %s. Got %s: '%s'. " \
                      "The DB package will be recreated. It's great that you have a backup."
                # todo: that should be logged, not printed
                print(msg % (package_name, import_dir_path, type(e).__name__, e))
                return


def _split_path_and_name(python_file_path):
    import_dir_path, module_name = os.path.split(os.path.abspath(python_file_path))

    module_name = re.sub(r"(.*)\.pyc?$", r"\1", module_name)
    if module_name == "__init__":
        import_dir_path, module_name = os.path.split(import_dir_path)

    return import_dir_path, module_name


@contextlib.contextmanager
def _supplementing_sys_path(path_to_supplement):
    assert os.path.isdir(path_to_supplement), "Path has to be an existing dir: %s." % path_to_supplement

    if path_to_supplement in sys.path:
        yield
    else:
        sys.path.insert(0, path_to_supplement)
        try:
            yield
        finally:
            if path_to_supplement in sys.path:
                sys.path.pop(sys.path.index(path_to_supplement))


def _hiding_attr_name(name):
    if not name.startswith("_"):
        name = "_" + name
    return "{}_hidden".format(name)


class PyStorage(object):
    _allowed_attrs = ["storage_path"]

    def __init__(self, storage_path, create=False):
        """ Passing: 'some/path_to/pkg_name' or 'some/path_to/pkg_name/__init__.py' will cause:
        - pkg_name being a name of the package with 'some/path_to/pkg_name/__init__.py' as main file
        - 'some/path_to' appearing in sys.path for importing reasons
        - creating sub files in 'some/path_to/pkg_name/' directory
        """
        self.storage_path = storage_path
        self.load_from_disk(storage_path, create)

    def load_from_disk(self, package_path, create=False):
        if create:
            _make_dirs(package_path)
            package = None
        else:
            package = _import_from_path(package_path or self.storage_path)

        processed = set()
        for name, proxy in self._collect_serializables():
            if package and hasattr(package, name):
                value_from_a_package = getattr(package, name)
                setattr(self, name, value_from_a_package)
            else:
                # cause a RAII case - single acquisition initializes the object
                getattr(self, name)
            processed.add(name)

        if package:
            for name in dir(package):
                if not name.startswith("_") and name not in processed:
                    value_from_a_package = getattr(package, name)
                    has_sub_module = hasattr(package, _py_lang.sub_module_name(name))

                    if not inspect.ismodule(value_from_a_package) and not inspect.isclass(value_from_a_package):
                        if has_sub_module:
                            setattr(self, name, LiveReference(value_from_a_package))
                        else:
                            setattr(self, name, LiveLabel(value_from_a_package))

    @contextlib.contextmanager
    def updating_db(self):
        try:
            yield self
        finally:
            self.store_to_disk()

    def store_to_disk(self):
        labels, references = self._split_references()
        all_names = sorted(dict(self._collect_serializables()))
        self._dump_package_init(labels, references, all_names)
        for aux_name in references.values():
            self._dump_submodule(aux_name, references)

    def _dump_package_init(self, labels, ref_watches, all_names):
        items = sorted(labels.items())
        items.insert(0, ("__all__", all_names))
        content = _py_lang.build_py_file_content(items, ref_watches=ref_watches, all_refs=True)
        target_path = self._sub_module_path("__init__")
        return write_file(target_path, content, makedirs=True)

    def _dump_submodule(self, aux_name, ref_watches):
        """ submodule's variable should:
         - be able to reference any other label from other submodule (not from __init__.py)
         - import any of user type definitions (_cls_dependency & _cls_namespace)
         - is supposed to contain exactly one label
           (note that grouping several labels into one submodule is tricky and not needed at all)
        """
        ref_watches = {id_: n for id_, n in ref_watches.items() if n != aux_name}
        items = [(aux_name, self._get_instance_obj(aux_name))]
        content = _py_lang.build_py_file_content(items, ref_watches=ref_watches)
        target_path = self._sub_module_path(_py_lang.sub_module_name(aux_name))
        write_file(target_path, content, makedirs=True)

    def __getattribute__(self, attribute_name):
        attribute = object.__getattribute__(self, attribute_name)
        if not attribute_name.startswith("_") and isinstance(attribute, SerializableBase):
            # When getting Label, Reference or LiveReference (those are class attributes),
            # redirect the query to corresponding "hidden" attribute of this instance then
            hidden_name = _hiding_attr_name(attribute_name)
            if not hasattr(self, hidden_name) and isinstance(attribute, Label):
                # If it has been not created yet - perform a RAII
                object.__setattr__(self, hidden_name, attribute.default_constructor())
            return object.__getattribute__(self, hidden_name)

        return attribute

    def __setattr__(self, attribute_name, value):
        if attribute_name.startswith("_"):
            object.__setattr__(self, attribute_name, value)
            return

        # magic to be done only for setting public attributes being instances of SerializableBase

        hidden_name = _hiding_attr_name(attribute_name)

        if attribute_name in self._allowed_attrs:
            object.__setattr__(self, attribute_name, value)
            return

        elif attribute_name in dir(self):
            attribute = object.__getattribute__(self, attribute_name)

            if isinstance(attribute, SerializableBase):
                if isinstance(attribute, Label):
                    if not isinstance(value, attribute.default_constructor):
                        msg = "Cannot assign a different type than %r, got %r."
                        raise AttributeError(msg % (attribute.default_constructor.__name__, type(value).__name__))

                if isinstance(value, LiveLabel):
                    value = value.value
                object.__setattr__(self, hidden_name, value)
                return

        elif isinstance(value, LiveLabel):
            # adding dynamic fields
            if hasattr(self, hidden_name):
                raise AttributeError("The name %s (hiding %s) is already occupied." % (hidden_name, attribute_name))

            object.__setattr__(self, attribute_name, value)
            if isinstance(value, Label):
                object.__setattr__(self, hidden_name, value.default_constructor())
            else:
                object.__setattr__(self, hidden_name, value.value)

            return

        msg = "Unexpected assignment of type %s to %s class, attribute %s."
        if isinstance(value, Label):
            msg += " In order to set live objects encapsulate its values with renew.LiveLabel or renew.LiveReference."
        raise AttributeError(msg % (type(value).__name__, self.__class__.__name__, attribute_name))

    def _collect_serializables(self):
        for name in dir(self):
            if not name.startswith("_"):
                value = object.__getattribute__(self, name)
                if isinstance(value, SerializableBase):
                    yield name, value

    def _split_references(self):
        labels = {}
        references = {}
        for name, proxy in self._collect_serializables():
            underlying_value = self._get_instance_obj(name)
            if self._do_separate_source(name, proxy, underlying_value):
                references[id(underlying_value)] = name
            else:
                labels[name] = underlying_value

        return labels, references

    def _do_separate_source(self, name, proxy, underlying_object):
        """ Used in _split_references decides if given object is supposed to be placed
        in common __init__.py (return False) or a separate sub module (return True).
        It can be overridden (e.g. using regex on name).
        """
        return isinstance(proxy, (Reference, LiveReference))

    def _get_instance_obj(self, name):
        hideous_name = _hiding_attr_name(name)
        return self.__getattribute__(hideous_name)

    def _sub_module_path(self, sub_name):
        if not sub_name.endswith(".py"):
            sub_name += ".py"

        return os.path.join(self.storage_path, sub_name)


class SerializableBase(object):
    @classmethod
    def _validate_is_a_constructor(cls, callable_type):
        return None


class Label(SerializableBase):
    def __init__(self, default_constructor):
        self.default_constructor = self._validate_is_a_constructor(default_constructor)

    @classmethod
    def _validate_is_a_constructor(cls, callable_type):
        try:
            assert callable_type() is not None, "It has to return something."
        except Exception as e:
            msg = "The object passed to %r class (type: %r) has to be a callable wih no args and return anything. " \
                  "Failed to call or get return value from %r. Got %s: %s"

            type_name = getattr(callable_type, '__name__', repr(callable_type))
            raise TypeError(msg % (cls.__name__, type_name, callable_type, type(e).__name__, e))

        return callable_type


class Reference(Label):
    """ Have to provide a default type. Statically typed to become an
    externally defined/serialized value (in a separate submodule). """


class LiveLabel(SerializableBase):
    """ Doesn't need to provide a default type. Used only for creating a serializable values in a runtime.
    Does not validate assigned values. It's value gets serialized in a main package module (__init__.py).
    """

    def __init__(self, value):
        self.value = value


class LiveReference(LiveLabel):
    """ Doesn't need to provide a default type. Used only for creating a serializable values in a runtime.
    Does not validate assigned values. It's value gets serialized in a separate submodule.
    """
