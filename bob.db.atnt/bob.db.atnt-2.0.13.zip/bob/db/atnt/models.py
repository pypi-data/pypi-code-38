#!/usr/bin/env python
# vim: set fileencoding=utf-8 :


"""
This file defines simple Client and File interfaces that should be comparable
with other bob.db databases.
"""

import os
import bob

import bob.db.base
import bob.io.image  # to be able to load images when File.load is called!

# Location where the data files are typically decompressed at
import pkg_resources
DEFAULT_DATADIR = pkg_resources.resource_filename(__name__, 'data')


class Client(object):
    """The clients of this database contain ONLY client ids. Nothing special.


    """
    m_valid_client_ids = set(range(1, 41))

    def __init__(self, client_id):
        super(Client, self).__init__()
        assert client_id in self.m_valid_client_ids
        self.id = client_id


class File (bob.db.base.File):
    """Files of this database are composed from the client id and a file id.


    Parameters:

      client_id (int): The unique client identity

      client_file_id (int): The unique file identity for this given client

      install_path (str): The installation path for the database

      default_ext (str): The default extension for the database (normally,
        should be ``.pgm``)

    """

    m_valid_file_ids = set(range(1, 11))


    def __init__(self, client_id, client_file_id, install_path, default_ext):
        assert client_file_id in self.m_valid_file_ids
        # compute the file id on the fly
        file_id = (client_id - 1) * len(self.m_valid_file_ids) + client_file_id
        # generate path on the fly
        path = os.path.join("s" + str(client_id), str(client_file_id))
        # call base class constructor
        bob.db.base.File.__init__(self, file_id=file_id, path=path)
        self.client_id = client_id
        self.install_path = install_path
        self.default_ext = default_ext


    @staticmethod
    def _from_file_id(file_id, install_path, default_ext):
        """Returns the File object for a given file_id"""
        client_id = int((file_id - 1) / len(File.m_valid_file_ids) + 1)
        client_file_id = (file_id - 1) % len(File.m_valid_file_ids) + 1
        return File(client_id, client_file_id, install_path, default_ext)


    @staticmethod
    def _from_path(path, install_path, default_ext):
        """Returns the File object for a given path"""
        # get the last two paths
        paths = os.path.split(path)
        file_name = os.path.splitext(paths[1])[0]
        paths = os.path.split(paths[0])
        assert paths[1][0] == 's'
        return File(int(paths[1][1:]), int(file_name), install_path,
            default_ext)


    def make_path(self, directory=None, extension=None):
      """Wraps the current path so that a complete path is formed


      Parameters:

        directory (:py:class:`str`, Optional): An optional directory name that
          will be prefixed to the returned result. If not set, use the database
          raw files installation directory as set on the database.

        extension (:py:class:`str`, Optional): An optional extension that will
          be suffixed to the returned filename. The extension normally includes
          the leading ``.`` character as in ``.jpg`` or ``.hdf5``. If not set,
          use the default for the database, which is ``.pgm``.


      Returns:

        str: The newly generated file path.

      """
      directory = directory or self.install_path
      extension = extension or self.default_ext
      # assure that directory and extension are actually strings
      # create the path
      return str(os.path.join(directory or '', self.path + (extension or '')))


    def load(self, directory=None, extension=None):
      """Loads the data at the specified location and using the given extension.

      Uses :py:func:`bob.io.base.load` to load the contents of the file named
      ``<directory>/<self.path>+<extension>``. Returns whatever that function
      returns.


      Parameters:

        directory (:py:class:`str`, Optional): An optional directory name that
          will be prefixed to the returned result. If not set, use the database
          raw files installation directory as set on the database.

        extension (:py:class:`str`, Optional): An optional extension that will
          be suffixed to the returned filename. The extension normally includes
          the leading ``.`` character as in ``.jpg`` or ``.hdf5``. If not set,
          use the default for the database, which is ``.pgm``.


      Returns:

        object: The return value of :py:func:`bob.io.base.load` given the input
        file type.

      """

      return bob.io.base.load(self.make_path(directory, extension))
