"""Serialization with :mod:`pyarrow` (requires pyarrow to be installed)

Usage
-----

A context implements serialization of relevant Eelbrain objects, and can be
re-used indefinitely::

    >>> context = pyarrow_context()
    >>> s = context.serialize(ds).to_buffer()
    >>> ds = context.deserialize(s)
"""
from inspect import isclass
import os

from .._utils import ui


CONTEXT = None


def deserialize_2to3(obj, context):
    """Recursively deserialize objects serialized with Python 2
    
    Parameters
    ----------
    obj : object
        The object to decode.
    context : SerializationContext
        The relevant pyarrow serialization context.
    """
    if isinstance(obj, bytes):
        obj = obj.decode()
    elif isinstance(obj, dict):
        for k in tuple(obj.keys()):
            new_k = k.decode() if isinstance(k, bytes) else k
            obj[new_k] = deserialize_2to3(obj.pop(k), context)
        if context is not None and '_pytype_' in obj:
            obj = context._deserialize_callback(obj)
    elif isinstance(obj, tuple):
        obj = tuple(deserialize_2to3(item, context) for item in obj)
    elif isinstance(obj, list):
        obj = [deserialize_2to3(item, context) for item in obj]
    return obj


def serialize_factory(cls):
    if hasattr(cls, '__getstate__'):
        serialize = cls.__getstate__

        def deserialize(state):
            out = cls.__new__(cls)
            out.__setstate__(state)
            return out
    else:

        def serialize(inst):
            return inst.__reduce__()[1]

        def deserialize(data):
            return cls(*data)

    return serialize, deserialize


def pyarrow_context():
    """Generate :mod:`pyarrow` context implementing Eelbrain object serialization"""
    global CONTEXT

    if CONTEXT is None:
        import pyarrow
        import collections
        import eelbrain

        # find all classes
        classes = [
            (collections, 'OrderedDict'),
            (eelbrain._stats.testnd, 'NDPermutationDistribution'),
            (eelbrain._stats.testnd, '_MergedTemporalClusterDist'),
        ]
        for module in (eelbrain, eelbrain.test, eelbrain.testnd):
            classes.extend((module, attr) for attr in dir(module) if isclass(getattr(module, attr)))

        CONTEXT = pyarrow.SerializationContext()
        for module, attr in classes:
            cls = getattr(module, attr)
            name = '%s.%s' % (module.__name__, attr)
            serialize, deserialize = serialize_factory(cls)
            CONTEXT.register_type(cls, name, custom_serializer=serialize,
                                  custom_deserializer=deserialize)
    return CONTEXT


def load_arrow(file_path=None):
    """Load object serialized with :mod:`pyarrow`.

    Parameters
    ----------
    file_path : None | str
        Path to a pickled file. If None (default), a system file dialog will be
        shown. If the user cancels the file dialog, a RuntimeError is raised.
    """
    if file_path is None:
        filetypes = [("Parquet (*.arrow)", '*.arrow'), ("All files", '*')]
        file_path = ui.ask_file("Select Arrow file to load", "", filetypes)
        if file_path is False:
            raise RuntimeError("User canceled")
        else:
            print("load %r" % (file_path,))
    else:
        file_path = os.path.expanduser(file_path)
        if not os.path.exists(file_path):
            new_path = os.extsep.join((file_path, 'arrow'))
            if os.path.exists(new_path):
                file_path = new_path

    import pyarrow

    context = pyarrow_context()
    with pyarrow.OSFile(file_path) as fid:
        obj = context.deserialize(fid.read_buffer())

    if isinstance(obj, dict) and b'_pytype_' in obj:
        obj = deserialize_2to3(obj, context)

    return obj


def save_arrow(obj, dest=None):
    """Save a Python object with :mod:`pyarrow`.

    Parameters
    ----------
    obj : object
        Python object to save. Can contain Eelbrain objects, but custom classes
        are not supported.
    dest : None | str
        Path to destination where to save the  file. If no destination is
        provided, a file dialog is shown. If a destination without extension is
        provided, '.arrow' is appended.
    """
    if dest is None:
        filetypes = [("Arrow files (*.arrow)", '*.arrow')]
        dest = ui.ask_saveas("Save as arrow file", "", filetypes)
        if dest is False:
            raise RuntimeError("User canceled")
        else:
            print('dest=%r' % dest)
    else:
        dest = os.path.expanduser(dest)
        if not os.path.splitext(dest)[1]:
            dest += '.arrow'

    context = pyarrow_context()
    context.serialize(obj).write_to(dest)
