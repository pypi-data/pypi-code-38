import pathlib

class FileValidationError(Exception):
    pass

class DataFile:
    """
    A class representing a DataFile to be made by pipeline stages
    and passed on to subsequent ones.

    DataFile itself should not be instantiated - instead subclasses
    should be defined for different file types.

    These subclasses are used in the definition of pipeline stages
    to indicate what kind of file is expected.  The "suffix" attribute,
    which must be defined on subclasses, indicates the file suffix.

    The open method, which can optionally be overridden, is used by the 
    machinery of the PipelineStage class to open an input our output
    named by a tag.

    """
    def __init__(self, path, mode, validate=True, **kwargs):
        self.path = path
        self.mode = mode
        self.file = self.open(path, mode, **kwargs)
        if validate and mode == 'r':
            self.validate()

    def validate(self):
        """
        Concrete subclasses should override this method
        to check that all expected columns are present.
        """
        pass

    @classmethod
    def open(cls, path, mode):
        """
        Open a data file.  The base implementation of this function just
        opens and returns a standard python file object.

        Subclasses can override to either open files using different openers
        (like fitsio.FITS), or, for more specific data types, return an
        instance of the class itself to use as an intermediary for the file.

        """
        return open(path, mode)

    def close(self):
        self.file.close()

    @classmethod
    def make_name(cls, tag):
        if cls.suffix:
            return f'{tag}.{cls.suffix}'
        else:
            return tag

class HDFFile(DataFile):
    """
    A data file in the HDF5 format.
    Using these files requires the h5py package, which in turn
    requires an HDF5 library installation.

    """
    suffix = 'hdf5'
    required_datasets = []

    @classmethod
    def open(cls, path, mode, **kwargs):
        # Suppress a warning that h5py always displays
        # on import
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import h5py
        # Return an open h5py File
        return h5py.File(path, mode, **kwargs)

    def validate(self):
        missing = [name for name in self.required_datasets if name not in self.file]
        if missing:
            text = "\n".join(missing)
            raise FileValidationError(f"These data sets are missing from HDF file {self.path}:\n{text}")

    def close(self):
        self.file.close()


class FitsFile(DataFile):
    """
    A data file in the FITS format.
    Using these files requires the fitsio package.
    """
    suffix = 'fits'
    required_columns = []

    @classmethod
    def open(cls, path, mode, **kwargs):
        import fitsio
        # Fitsio doesn't have pure 'w' modes, just 'rw'.
        # Maybe we should check if the file already exists here?
        if mode == 'w':
            mode = 'rw'
        return fitsio.FITS(path, mode=mode, **kwargs)

    def missing_columns(self, columns, hdu=1):
        """
        Check that all supplied columns exist
        and are in the chosen HDU
        """
        ext = self.file[hdu]
        found_cols = ext.get_colnames()
        missing_columns = [col for col in columns if col not in found_cols]
        return missing_columns


    def validate(self):
        """Check that the catalog has all the required columns and complain otherwise"""
        # Find any columns that do not exist in the file
        missing = self.missing_columns(self.required_columns)

        # If there are any, raise an exception that lists them explicitly
        if missing:
            text = "\n".join(missing)
            raise FileValidationError(f"These columns are missing from FITS file {self.path}:\n{text}")

    def close(self):
        self.file.close()


class TextFile(DataFile):
    """
    A data file in plain text format.
    """
    suffix = 'txt'

class YamlFile(DataFile):
    """
    A data file in yaml format.
    """
    suffix = 'yml'

class Directory(DataFile):
    suffix = ''

    @classmethod
    def open(self, path, mode):
        p = pathlib.Path(path)

        if mode == "w":
            if p.exists():
                shutil.rmtree(p)
            p.mkdir(parents=True)
        else:
            if not p.is_dir():
                raise ValueError(f"Directory input {path} does not exist")
        return p

    def close(self):
        pass
