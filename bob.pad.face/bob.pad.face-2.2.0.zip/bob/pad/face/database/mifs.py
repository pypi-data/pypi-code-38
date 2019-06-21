#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#!/usr/bin/env python

#==============================================================================

# Used in ReplayMobilePadFile class
from bob.bio.video import FrameSelector, FrameContainer
import bob.io.base
import numpy as np

from bob.pad.face.database import VideoPadFile  # Used in ReplayPadFile class

from bob.pad.base.database import FileListPadDatabase

#==============================================================================


class MIFSPadFile(VideoPadFile):
    """
    A high level implementation of the File class for the MIFS database.
    """

    def __init__(self, client_id, path, attack_type=None, file_id=None):
        super(MIFSPadFile, self).__init__(client_id, path, attack_type,
                                          file_id)

    #==========================================================================
    def load(self, directory=None, extension=None, frame_selector=FrameSelector(selection_style='all')):
        """
        Overridden version of the load method defined in the ``VideoPadFile``.

        **Parameters:**

        ``directory`` : :py:class:`str`
            String containing the path to the MIFS database.
            Default: None

        ``extension`` : :py:class:`str`
            Extension of the video files in the MIFS database.
            Default: None

        ``frame_selector`` : ``FrameSelector``
            The frame selector to use.

        **Returns:**

        ``video_data`` : FrameContainer
            Video data stored in the FrameContainer, see ``bob.bio.video.utils.FrameContainer``
            for further details.
        """

        path = self.make_path(
            directory=directory, extension=extension)  # path to the file

        data = bob.io.base.load(path)
        data = np.expand_dims(data, axis=0)  # upgrade to 4D (video)
        video_data = frame_selector(data)  # video data

        return video_data  # video data


#==============================================================================
class MIFSPadDatabase(FileListPadDatabase):
    """
    A high level implementation of the Database class for the MIFS database.
    """

    def __init__(
            self,
            protocol='grandtest',  # grandtest is the default protocol for this database
            original_directory='[YOUR_MIFS_DATABASE_DIRECTORY]',
            original_extension='.jpg',
            **kwargs):

        from pkg_resources import resource_filename
        folder = resource_filename(__name__, '../lists/mifs/')
        super(MIFSPadDatabase, self).__init__(
            folder,
            'mifs',
            pad_file_class=MIFSPadFile,
            protocol=protocol,
            original_directory=original_directory,
            original_extension=original_extension)

    #==========================================================================
    def annotations(self, f):
        """
        Return annotations for a given file object ``f``, which is an instance
        of ``MIFSPadFile``.

        **Parameters:**

        ``f`` : :py:class:`object`
            An instance of ``MIFSPadFile`` defined above.

        **Returns:**

        ``annotations`` : :py:class:`dict`
            A dictionary containing the annotations for each frame in the video.
            Dictionary structure: ``annotations = {'1': frame1_dict, '2': frame1_dict, ...}``.
            Where ``frameN_dict = {'topleft': (row, col), 'bottomright': (row, col)}``
            is the dictionary defining the coordinates of the face bounding box in frame N.
        """

        path_to_file = self.m_base_dir + '/annotations/' + f.path[:-4] + '.face'
        file_handle = open(path_to_file, 'r')
        line = file_handle.readline()
        bbox = [int(x) for x in line.split()]

        annotations = {}  # dictionary to return

        topleft = (bbox[0], bbox[1])
        bottomright = (bbox[0] + bbox[2], bbox[1] + bbox[3])

        annotations['0'] = {'topleft': topleft, 'bottomright': bottomright}

        return annotations
