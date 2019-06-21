#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#!/usr/bin/env python

#==============================================================================

import bob.bio.video # Used in CELEBAPadFile class
import bob.io.base
import numpy as np

from bob.pad.base.database import PadFile # Used in ReplayPadFile class

from bob.pad.base.database import FileListPadDatabase


#==============================================================================

class CELEBAPadFile(PadFile):
    """
    A high level implementation of the File class for the CELEBA database.
    """

    def __init__(self, client_id, path, attack_type=None, file_id=None):
        super(CELEBAPadFile, self).__init__(client_id, path, attack_type, file_id)

    # ==========================================================================
    def load(self, directory=None, extension=None,
             frame_selector=bob.bio.video.FrameSelector(selection_style='all')):
        """
        Overridden version of the load method defined in the ``PadFile``.

        **Parameters:**

        ``directory`` : :py:class:`str`
            String containing the path to the CELEBA database.
            Default: None

        ``extension`` : :py:class:`str`
            Extension of the video files in the CELEBA database.
            Default: None

        ``frame_selector`` : :any:`bob.bio.video.FrameSelector`, optional
            Specifying the frames to be selected.

        **Returns:**

        ``video_data`` : FrameContainer
            Video data stored in the FrameContainer, see ``bob.bio.video.utils.FrameContainer``
            for further details.
        """

        path = self.make_path(directory=directory, extension=extension) # path to the file

        data = bob.io.base.load(path)
        data = np.expand_dims(data, axis=0) # upgrade to 4D (video)
        video_data = frame_selector(data) # video data

        return video_data # video data


#==============================================================================
class CELEBAPadDatabase(FileListPadDatabase):
    """
    A high level implementation of the Database class for the CELEBA database.
    """

    def __init__(
        self,
        protocol='grandtest', # grandtest is the default protocol for this database
        original_directory='[YOUR_CELEB_A_DATABASE_DIRECTORY]',
        original_extension='.jpg',
        **kwargs):

        from pkg_resources import resource_filename
        folder = resource_filename(__name__, '../lists/celeb_a/')
        super(CELEBAPadDatabase, self).__init__(folder, 'celeb_a',
                                            pad_file_class=CELEBAPadFile,
                                            protocol = protocol,
                                            original_directory=original_directory,
                                            original_extension=original_extension)

    #==========================================================================
    def annotations(self, f):
        """
        Return annotations for a given file object ``f``, which is an instance
        of ``CELEBAPadFile``.

        **Parameters:**

        ``f`` : :py:class:`object`
            An instance of ``CELEBAPadFile`` defined above.

        **Returns:**

        ``annotations`` : :py:class:`dict`
            A dictionary containing the annotations for each frame in the video.
            Dictionary structure: ``annotations = {'1': frame1_dict, '2': frame1_dict, ...}``.
            Where ``frameN_dict = {'topleft': (row, col), 'bottomright': (row, col)}``
            is the dictionary defining the coordinates of the face bounding box in frame N.
        """


        annotations = {} # dictionary to return


        return annotations