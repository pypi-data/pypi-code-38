#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

import bob.db.base
import bob.io.base
import numpy
import os


class File(object):
    """ Generic file container """

    def __init__(self, filename, cls, group):

        self.filename = filename
        self.cls = cls  # 'attack' or 'real'
        self.group = group  # 'train' or 'test'

    def __repr__(self):
        return "File('%s')" % self.filename

    def get_file(self, pc):
        '''Returns the full file path given the path components pc'''
        from pkg_resources import resource_filename
        return resource_filename(__name__, os.path.join(pc))

    def make_path(self, directory=None, extension=None):
        """Wraps this files' filename so that a complete path is formed

    Keyword parameters:

    directory
      An optional directory name that will be prefixed to the returned result.

    extension
      An optional extension that will be suffixed to the returned filename. The
      extension normally includes the leading ``.`` character as in ``.jpg`` or
      ``.hdf5``.

    Returns a string containing the newly generated file path.
    """

        if not directory: directory = ''
        if not extension: extension = ''
        return os.path.join(directory, self.filename + extension)

    def is_real(self):
        """True if the file belongs to a real access, False otherwise """

        return bool(self.cls == 'real')

    def get_clientid(self):
        """The ID of the client. Value from 1 to 50. Clients in the train and
        devel set may have IDs from 1 to 20; clients in the test set have IDs
        from 21 to 50."""

        stem_client = self.filename.split('/')[
            1]  # the identity stem of the filename
        if self.group == 'train' or self.group == 'dev':
            return int(stem_client)
        else:  #'test'
            return int(stem_client) + 20

    # db_mappings = {'real_normal':'1', 'real_low':'2', 'real_high':'HR_1',
    # 'warped_normal':'3', 'warped_low':'4', 'warped_high':'HR_2',
    # 'cut_normal':'5', 'cut_low':'6', 'cut_high':'HR_3', 'video_normal':'7',
    # 'video_low':'8', 'video_high':'HR_4'}

    def get_type(self):
        """The type of attack, if it is an attack. Possible values: 'warped',
        'cut' and 'video'. Returns None for real accesses"""

        stem_fname = self.filename.rpartition('/')[
            2]  # just the filename (without the full path)
        if stem_fname in ('3', '4', 'HR_2'):
            return 'warped'
        elif stem_fname in ('5', '6', 'HR_3'):
            return 'cut'
        elif stem_fname in ('7', '8', 'HR_4'):
            return 'video'
        else:  # real access, no type attribute
            return None

    def get_quality(self):
        """The quality of the video file. Possible value: 'normal', 'low' and 'high'."""

        stem_fname = self.filename.rpartition('/')[
            2]  # just the filename (without the full path)
        if stem_fname in ('1', '3', '5', '7'):
            return 'normal'
        elif stem_fname in ('2', '4', '6', '8'):
            return 'low'
        else:  # stem_name in ('HR1', 'HR2', 'HR3', 'HR4')
            return 'high'

    def facefile(self, directory=None):
        """Returns the path to the companion face bounding-box file

    Keyword parameters:

    directory
      An optional directory name that will be prefixed to the returned result.

    Returns a string containing the face file path.
    """

        if not directory:
            directory = self.get_file('face-locations')
        return self.make_path(directory, '.face')

    def videofile(self, directory=None):
        """Returns the path to the database video file for this object

    Keyword parameters:

    directory
      An optional directory name that will be prefixed to the returned result.

    Returns a string containing the video file path.
    """

        return self.make_path(directory, '.avi')

    def bbx(self, directory=None):
        """Reads the file containing the face locations for the frames in the
    current video

    Keyword parameters:

    directory
      A directory name that will be prepended to the final filepaths where the
      face bounding boxes are located, if not on the current directory.

    Returns:
      A :py:class:`numpy.ndarray` containing information about the located
      faces in the videos. Each row of the :py:class:`numpy.ndarray`
      corresponds for one frame. The five columns of the
      :py:class:`numpy.ndarray` are (all integers):

      * Frame number (int)
      * Bounding box top-left X coordinate (int)
      * Bounding box top-left Y coordinate (int)
      * Bounding box width (int)
      * Bounding box height (int)

      Note that **not** all the frames may contain detected faces.
    """

        return numpy.loadtxt(self.facefile(directory), dtype=int)

    def load(self, directory=None, extension='.hdf5'):
        """Loads the data at the specified location and using the given extension.

    Keyword parameters:

    data
      The data blob to be saved (normally a :py:class:`numpy.ndarray`).

    directory
      [optional] If not empty or None, this directory is prefixed to the final
      file destination

    extension
      [optional] The extension of the filename - this will control the type of
      output and the codec for saving the input blob.
    """
        return bob.io.base.load(self.make_path(directory, extension))

    def save(self, data, directory=None, extension='.hdf5'):
        """Saves the input data at the specified location and using the given
    extension.

    Keyword parameters:

    data
      The data blob to be saved (normally a :py:class:`numpy.ndarray`).

    directory
      If not empty or None, this directory is prefixed to the final file
      destination

    extension
      The extension of the filename - this will control the type of output and
      the codec for saving the input blob.
    """

        path = self.make_path(directory, extension)
        bob.io.base.create_directories_safe(os.path.dirname(path))
        bob.io.base.save(data, path)
