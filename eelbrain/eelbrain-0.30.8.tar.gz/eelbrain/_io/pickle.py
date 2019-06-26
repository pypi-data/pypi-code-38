# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from pickle import dump, HIGHEST_PROTOCOL, Unpickler
from itertools import chain
import os

from .._data_obj import NDVar, SourceSpaceBase
from .._utils import ui


class EelUnpickler(Unpickler):

    def find_class(self, module, name):
        "Backwards-compatibility for changes in module paths"
        if module.startswith('eelbrain.'):
            if module == 'eelbrain.vessels.data':
                module = 'eelbrain._data_obj'
                class_names = {'var': 'Var', 'factor': 'Factor', 'ndvar': 'NDVar',
                               'datalist': 'Datalist', 'dataset': 'Dataset'}
                name = class_names[name]
            elif module.startswith('eelbrain.data.'):
                if module.startswith('eelbrain.data.load'):
                    module = module.replace('.data.load', '.load')
                elif module.startswith('eelbrain.data.stats'):
                    module = module.replace('.data.stats', '._stats')
                elif module.startswith('eelbrain.data.data_obj'):
                    module = module.replace('.data.data_obj', '._data_obj')
                else:
                    raise NotImplementedError("%r / %r" % (module, name))

        return Unpickler.find_class(self, module, name)


def pickle(obj, dest=None, protocol=HIGHEST_PROTOCOL):
    """Pickle a Python object.

    Parameters
    ----------
    obj : object
        Python object to save.
    dest : None | str
        Path to destination where to save the  file. If no destination is
        provided, a file dialog is shown. If a destination without extension is
        provided, '.pickled' is appended.
    protocol : int
        Pickle protocol (default is ``HIGHEST_PROTOCOL``). For pickles that can
        be opened in Python 2, use ``protocol<=2``.
    """
    if dest is None:
        filetypes = [("Pickled Python Objects (*.pickled)", '*.pickled')]
        dest = ui.ask_saveas("Pickle Destination", "", filetypes)
        if dest is False:
            raise RuntimeError("User canceled")
        else:
            print('dest=%r' % dest)
    else:
        dest = os.path.expanduser(dest)
        if not os.path.splitext(dest)[1]:
            dest += '.pickled'

    try:
        with open(dest, 'wb') as fid:
            dump(obj, fid, protocol)
    except SystemError as exception:
        if exception.args[0] == 'error return without exception set':
            if os.path.exists(dest):
                os.remove(dest)
            raise IOError("An error occurred while pickling. This could be "
                          "due to an attempt to pickle an array (or NDVar) "
                          "that is too big. Try saving several smaller arrays.")
        else:
            raise


def unpickle(file_path=None):
    """Load pickled Python objects from a file.

    Almost like ``pickle.load(open(file_path))``, but also loads object saved
    with older versions of Eelbrain, and allows using a system file dialog to
    select a file.

    Parameters
    ----------
    file_path : None | str
        Path to a pickled file. If ``None`` (default), a system file dialog
        will be shown. If the user cancels the file dialog, a RuntimeError is
        raised.

    Notes
    -----
    If you see ``ValueError: unsupported pickle protocol: 4``, the pickle file
    was saved with Python 3; in order to make pickles backwards-compatible, use
    :func:`~eelbrain.save.pickle` with ``protocol=2``.
    """
    if file_path is None:
        filetypes = [("Pickles (*.pickled)", '*.pickled'), ("All files", '*')]
        file_path = ui.ask_file("Select File to Unpickle", "Select a pickled "
                                "file to unpickle", filetypes)
        if file_path is False:
            raise RuntimeError("User canceled")
        else:
            print("unpick %r" % (file_path,))
    else:
        file_path = os.path.expanduser(file_path)
        if not os.path.exists(file_path):
            new_path = os.extsep.join((file_path, 'pickled'))
            if os.path.exists(new_path):
                file_path = new_path

    with open(file_path, 'rb') as fid:
        unpickler = EelUnpickler(fid, encoding='latin1')
        return unpickler.load()


def update_subjects_dir(obj, subjects_dir, depth=0):
    """Update NDVar SourceSpace.subjects_dir attributes

    Examine elements of ``obj`` recursively and replace ``subjects_dir`` on all
    NDVars with SourceSpace dimension that are found.

    Parameters
    ----------
    obj : object
        Object to examine.
    subjects_dir : str
        New values for subjects_dir.
    depth : int
        Recursion depth for examining attributes (default 0, i.e. only apply to
        ``obj`` without recursion). Negative number for exhaustive search.

    Notes
    -----
    The following elements are searched:

      - Attributes of objects that have a ``__dict__``.
      - ``dict`` values.
      - list/tuple items.
    """
    if isinstance(obj, NDVar):
        for dim in obj.dims:
            if isinstance(dim, SourceSpaceBase):
                if dim.subjects_dir == subjects_dir:
                    break
                dim.subjects_dir = subjects_dir
                if dim._subjects_dir is not None:
                    dim._subjects_dir = subjects_dir
        else:
            for v in obj.info.values():
                update_subjects_dir(v, subjects_dir, depth)
    elif depth:
        if hasattr(obj, '__dict__'):
            values = obj.__dict__.values()
        else:
            values = ()

        if isinstance(obj, dict):
            values = chain(values, obj.values())
        elif isinstance(obj, (tuple, list)):
            values = chain(values, obj)

        for v in values:
            update_subjects_dir(v, subjects_dir, depth - 1)
