from . import importers as ip
import numpy
from .data_container import DataContainer
import os
import tempfile
from contextlib import contextmanager


class UndefinedImporter(Exception):
    pass


def import_data(file, type, **args):
    """
    Import data from lab instruments using a dedicated importer.

    Note:
        Deprecated in 0.3.0, use :func:`read` instead.
    """
    if type in ip.validImporters:
        if isinstance(file, list):
            data = []
            for f in file:
                data.append(ip.validImporters[type](f, **args))
            return numpy.array(data)
        return ip.validImporters[type](file, **args)
    raise UndefinedImporter('No importer defined for %s' % type)


def export_data(file, data, separator="\t"):
    numpy.savetxt(file, data, delimiter=separator)


def list_formats():
    print('The below formats are currently understood by the importer.\n'
          'To import one of these formats, use io.read("filename", type="<Importer>"),\n'
          'where <Importer> needs to be replaced by one of the following:\n')
    for i in ip.validImporters.keys():
        print('\t', i)
    print('\nThe following formats can be automatically detected and thus the\n'
          'type keyword can be omitted during import:\n')
    for i in ip.validAutoImporters.keys():
        print('\t', i)


def read(files, append=False, type=None, **kwargs):
    """
    :param files: a filename or list of file names to import.
    :param append: If True, multiple files will be appended row wise. If False, column wise.
    :param type: explicitly specify an importer. Not necessary if the importer supports auto import.
    :param kwargs: optional argument list that is passed on to the importer.
    :return: DataContainer with imported files or empty DataContainer.
    """
    """
    Import data from lab instruments.

    Automatically imports lab instrument data files. Several importers
    are available, and will be used to try and import the data. Note that the
    same importer will be used for all files. The data will be returned as a
    Pandas :obj:`DataFrame`.

    Args:
        files : a filename or list of file names to import
        **kwargs : optional argument list that is passed on to the importer.
            Use the `type` keyword to explicitly specify an importer.

    Returns:
        OpenQlab.io.DataContainer:
        a DataContainer containing the imported data with header information if available.
        The index of the data frame will be set to a natural x-axis, e.g. frequency or
        time.

    Examples:
        Read traces from an oscilloscope data file::

            >>> data = io.read('scope.bin')
            >>> data.head()
                        Channel 0  Channel 1
            Time (s)
            -0.005000  -0.019347    5.22613
            -0.004995  -0.019347    5.22613
            ...

        Read multiple files containing spectral data::

            >>> data = io.read(['vac.txt', 'dark.txt', 'sqz.txt'])

    Raises:
        UndefinedImporter: The file type cannot be recognized and cannot be
            imported automatically, or the given importer type does not exist
            (if `type` was specified).
    """
    # we always want to have a list of file names
    if isinstance(files, str):
        files = [files]
    if not files:
        return DataContainer()

    if type:
        if type not in ip.validImporters:
            raise UndefinedImporter('No importer defined for {0}'.format(type))
        importer = ip.validImporters[type]
    else:
        importer = _auto_importer

    if append is True:
        axis = 0
    else:
        axis = 1

    return DataContainer.concat([importer(f, **kwargs) for f in files], axis=axis)


def _auto_importer(file, **kwargs):
    for name, importer in ip.validAutoImporters.items():
        try:
            return _import_input(file, importer, **kwargs)
        except ip.utils.UnknownFileType as e:
            pass
    raise UndefinedImporter('AutoImporter: unable to find importer for {0}'.format(file))


def _import_input(_data, importer, **kwargs):
    try:
        data = importer(_data, **kwargs)
        return data
    except (FileNotFoundError, OSError):
        with tempinput(_data) as file:
            data = importer(file, **kwargs)
            return data


@contextmanager
def tempinput(data):
    temp = tempfile.NamedTemporaryFile(mode='w', delete=False, prefix='string', suffix='test')
    temp.write(data)
    temp.close()
    try:
        yield temp.name
    finally:
        os.unlink(temp.name)
