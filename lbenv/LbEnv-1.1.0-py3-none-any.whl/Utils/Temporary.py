""" create temporary structure for remote buids """


import os as _os
import warnings as _warnings
import sys as _sys
from tempfile import mkdtemp, mkstemp


# FIXME: backport from Python 3.2 (see http://stackoverflow.com/a/19299884)
class TemporaryDirectory(object):
    """Create and return a temporary directory.  This has the same
    behavior as mkdtemp but can be used as a context manager.  For
    example:

        with TemporaryDirectory() as tmpdir:
            ...

    Upon exiting the context, the directory and everything contained
    in it are removed.
    """

    def __init__(self, suffix="", prefix="tmp", dir=None):
        self._closed = False
        self.name = None  # Handle mkdtemp raising an exception
        self.name = mkdtemp(suffix, prefix, dir)

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.name)

    def __enter__(self):
        return self.name

    def cleanup(self, _warn=False):
        if self.name and not self._closed:
            try:
                self._rmtree(self.name)
            except TypeError as ex:
                # Issue #10188: Emit a warning on stderr
                # if the directory could not be cleaned
                # up due to missing globals
                if "None" not in str(ex):
                    raise
                _sys.stderr.write("ERROR: %r while cleaning up %r" % (ex, self))
                return
            except AttributeError as ex:
                # Issue #10188: Emit a warning on stderr
                # if the directory could not be cleaned
                # up due to missing globals
                if "None" not in str(ex):
                    raise
                _sys.stderr.write("ERROR: %r while cleaning up %r" % (ex, self))
                return
            self._closed = True
            if _warn:
                # It should be ResourceWarning, but it exists only in Python 3
                self._warn("Implicitly cleaning up %r" % self, UserWarning)

    def __exit__(self, exc, value, tb):
        self.cleanup()

    def __del__(self):
        # Issue a ResourceWarning if implicit cleanup needed
        self.cleanup(_warn=True)

    # XXX (ncoghlan): The following code attempts to make
    # this class tolerant of the module nulling out process
    # that happens during CPython interpreter shutdown
    # Alas, it doesn't actually manage it. See issue #10188
    _listdir = staticmethod(_os.listdir)
    _path_join = staticmethod(_os.path.join)
    _isdir = staticmethod(_os.path.isdir)
    _islink = staticmethod(_os.path.islink)
    _remove = staticmethod(_os.remove)
    _rmdir = staticmethod(_os.rmdir)
    _warn = _warnings.warn

    def _rmtree(self, path):
        # Essentially a stripped down version of shutil.rmtree.  We can't
        # use globals because they may be None'ed out at shutdown.
        for name in self._listdir(path):
            fullname = self._path_join(path, name)
            try:
                isdir = self._isdir(fullname) and not self._islink(fullname)
            except OSError:
                isdir = False
            if isdir:
                self._rmtree(fullname)
            else:
                try:
                    self._remove(fullname)
                except OSError:
                    pass
        try:
            self._rmdir(path)
        except OSError:
            pass


class TempDir(TemporaryDirectory):
    """Class to create a temporary directory."""

    def __init__(self,
                 suffix="",
                 prefix="tmp",
                 base_dir=None,
                 keep_var="KEEPTEMPDIR"):
        """Constructor.

        'keep_var' is used to define which environment variable will prevent
        the deletion of the directory.

        The other arguments are the same as tempfile.mkdtemp.
        """
        super(TempDir, self).__init__(suffix, prefix, base_dir)
        self._keep_var = keep_var

    def getName(self):
        """Returns the name of the temporary directory"""
        return self.name

    def __str__(self):
        """Convert to string."""
        return self.getName()

    def cleanup(self, _warn=False):
        if self._keep_var in _os.environ:
            import logging
            logging.info(
                "%s set: I do not remove the temporary directory '%s'",
                self._keep_var, self.name)
            return
        super(TempDir, self).cleanup(_warn=False)


class TempFile:
    """ class to create a temporary file """

    def __init__(self):
        """ Constructor """
        self._file = None
        self.name = ''

        fd, name = mkstemp()
        self.name = name
        self._file = _os.fdopen(fd, "w+")

    def __del__(self):
        """ Destructor """
        if self._file:
            self._file.close()
            _os.remove(self.name)

    def __getattr__(self, attr):
        return getattr(self._file, attr)
