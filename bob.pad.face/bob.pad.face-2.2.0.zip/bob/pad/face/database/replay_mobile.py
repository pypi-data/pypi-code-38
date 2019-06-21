#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Used in ReplayMobilePadFile class
from bob.bio.video import FrameSelector
from bob.pad.base.database import PadDatabase
from bob.pad.face.database import VideoPadFile
from bob.pad.face.utils import frames, number_of_frames
from bob.db.base.annotations import read_annotation_file
import numpy
from bob.extension import rc

REPLAYMOBILE_FRAME_SHAPE = (3, 1280, 720)


def replaymobile_annotations(lowlevelfile, original_directory):
    # numpy array containing the face bounding box data for each video
    # frame, returned data format described in the f.bbx() method of the
    # low level interface
    annots = lowlevelfile.bbx(directory=original_directory)

    annotations = {}  # dictionary to return

    for fn, frame_annots in enumerate(annots):

        topleft = (frame_annots[1], frame_annots[0])
        bottomright = (frame_annots[1] + frame_annots[3],
                       frame_annots[0] + frame_annots[2])

        annotations[str(fn)] = {
            'topleft': topleft,
            'bottomright': bottomright
        }

    return annotations


def replaymobile_frames(lowlevelfile, original_directory):
    vfilename = lowlevelfile.make_path(
        directory=original_directory,
        extension='.mov')
    is_not_tablet = not lowlevelfile.is_tablet()
    for frame in frames(vfilename):
        frame = numpy.rollaxis(frame, 2, 1)
        if is_not_tablet:
            frame = frame[:, ::-1, :]
        yield frame


class ReplayMobilePadFile(VideoPadFile):
    """
    A high level implementation of the File class for the Replay-Mobile
    database.
    """

    def __init__(self, f):
        """
        Parameters
        ----------
        f : object
            An instance of the File class defined in the low level db interface
            of the Replay-Mobile database, in the bob.db.replaymobile.models.py
            file.
        """

        self.f = f
        # this f is actually an instance of the File class that is defined in
        # bob.db.replaymobile.models and the PadFile class here needs
        # client_id, path, attack_type, file_id for initialization. We have to
        # convert information here and provide them to PadFile. attack_type is
        # a little tricky to get here. Based on the documentation of PadFile:
        # In cased of a spoofed data, this parameter should indicate what kind
        # of spoofed attack it is. The default None value is interpreted that
        # the PadFile is a genuine or real sample.
        if f.is_real():
            attack_type = None
        else:
            attack_type = 'attack'
        # attack_type is a string and I decided to make it like this for this
        # particular database. You can do whatever you want for your own
        # database.

        super(ReplayMobilePadFile, self).__init__(
            client_id=f.client_id,
            path=f.path,
            attack_type=attack_type,
            file_id=f.id)

    def load(self, directory=None, extension='.mov',
             frame_selector=FrameSelector(selection_style='all')):
        """
        Overridden version of the load method defined in the ``VideoPadFile``.

        Parameters
        ----------
        directory : str
            String containing the path to the Replay-Mobile database.

        extension : str
            Extension of the video files in the Replay-Mobile database.

        frame_selector : :any:`bob.bio.video.FrameSelector`
            The frame selector to use.

        Returns
        -------
        video_data : :any:`bob.bio.video.FrameContainer`
            Video data stored in the FrameContainer, see
            ``bob.bio.video.utils.FrameContainer`` for further details.
        """
        directory = directory or self.original_directory
        video_data_array = self.f.load(
            directory=directory, extension=extension)

        return frame_selector(video_data_array)

    @property
    def annotations(self):
        if self.annotation_directory is not None:
            # return the external annotations
            annotations = read_annotation_file(
                self.make_path(self.annotation_directory,
                               self.annotation_extension),
                self.annotation_type)
            return annotations

        # return original annotations
        return replaymobile_annotations(self.f, self.original_directory)

    @property
    def frames(self):
        return replaymobile_frames(self.f, self.original_directory)

    @property
    def number_of_frames(self):
        vfilename = self.make_path(
            directory=self.original_directory,
            extension='.mov')
        return number_of_frames(vfilename)

    @property
    def frame_shape(self):
        return REPLAYMOBILE_FRAME_SHAPE


class ReplayMobilePadDatabase(PadDatabase):
    """
    A high level implementation of the Database class for the Replay-Mobile
    database.
    """

    def __init__(
            self,
            protocol='grandtest',
            original_directory=rc['bob.db.replaymobile.directory'],
            original_extension='.mov',
            annotation_directory=None,
            annotation_extension='.json',
            annotation_type='json',
            **kwargs):
        """
        Parameters
        ----------
        protocol : str or None
            The name of the protocol that defines the default experimental
            setup for this database. ``grandtest`` is the default protocol for
            this database.

        original_directory : str
            The directory where the original data of the database are stored.

        original_extension : str
            The file name extension of the original data.

        annotation_directory : str
            If provided, the annotations will be read from this directory
            instead of the default annotations that are provided.

        annotation_extension : str
            The extension of annotations when annotation_extension is provided.

        **kwargs
            The arguments of the :py:class:`bob.bio.base.database.BioDatabase`
            base class constructor.
        """

        from bob.db.replaymobile import Database as LowLevelDatabase

        self.db = LowLevelDatabase()

        # Since the high level API expects different group names than what the
        # low level API offers, you need to convert them when necessary
        self.low_level_group_names = (
            'train', 'devel',
            'test')  # group names in the low-level database interface
        self.high_level_group_names = (
            'train', 'dev',
            'eval')  # names are expected to be like that in objects() function

        # Always use super to call parent class methods.
        super(ReplayMobilePadDatabase, self).__init__(
            name='replay-mobile',
            protocol=protocol,
            original_directory=original_directory,
            original_extension=original_extension,
            annotation_directory=annotation_directory,
            annotation_extension=annotation_extension,
            annotation_type=annotation_type,
            **kwargs)

    @property
    def original_directory(self):
        return self.db.original_directory

    @original_directory.setter
    def original_directory(self, value):
        self.db.original_directory = value

    def objects(self,
                groups=None,
                protocol=None,
                purposes=None,
                model_ids=None,
                **kwargs):
        """
        This function returns lists of ReplayMobilePadFile objects, which
        fulfill the given restrictions.

        Parameters
        ----------
        groups : str
            OR a list of strings.
            The groups of which the clients should be returned.
            Usually, groups are one or more elements of
            ('train', 'dev', 'eval')

        protocol : str
            The protocol for which the clients should be retrieved.
            The protocol is dependent on your database.
            If you do not have protocols defined, just ignore this field.

        purposes : str
            OR a list of strings.
            The purposes for which File objects should be retrieved.
            Usually it is either 'real' or 'attack'.

        model_ids
            This parameter is not supported in PAD databases yet
        **kwargs

        Returns
        -------
        files : [ReplayMobilePadFile]
            A list of ReplayMobilePadFile objects.
        """

        # Convert group names to low-level group names here.
        groups = self.convert_names_to_lowlevel(
            groups, self.low_level_group_names, self.high_level_group_names)
        # Since this database was designed for PAD experiments, nothing special
        # needs to be done here.
        files = self.db.objects(
            protocol=protocol, groups=groups, cls=purposes, **kwargs)

        files = [ReplayMobilePadFile(f) for f in files]

        for f in files:
            f.original_directory = self.original_directory
            f.annotation_directory = self.annotation_directory
            f.annotation_extension = self.annotation_extension
            f.annotation_type = self.annotation_type

        return files

    def annotations(self, f):
        """
        Return annotations for a given file object ``f``, which is an instance
        of ``ReplayMobilePadFile`` defined in the HLDI of the Replay-Mobile DB.
        The ``load()`` method of ``ReplayMobilePadFile`` class (see above)
        returns a video, therefore this method returns bounding-box annotations
        for each video frame. The annotations are returned as dictionary of
        dictionaries.

        If ``self.annotation_directory`` is not None, it will read the
        annotations from there.

        Parameters
        ----------
        f : :any:`ReplayMobilePadFile`
            An instance of :any:`ReplayMobilePadFile` defined above.

        Returns
        -------
        annotations : :py:class:`dict`
            A dictionary containing the annotations for each frame in the
            video. Dictionary structure:
            ``annotations = {'1': frame1_dict, '2': frame1_dict, ...}``. Where
            ``frameN_dict = {'topleft': (row, col),'bottomright': (row, col)}``
            is the dictionary defining the coordinates of the face bounding box
            in frame N.
        """
        return f.annotations

    def frames(self, padfile):
        """Yields the frames of the padfile one by one.

        Parameters
        ----------
        padfile : :any:`ReplayMobilePadFile`
            The high-level replay pad file

        Yields
        ------
        :any:`numpy.array`
            A frame of the video. The size is (3, 1280, 720).
        """
        return padfile.frames

    def number_of_frames(self, padfile):
        """Returns the number of frames in a video file.

        Parameters
        ----------
        padfile : :any:`ReplayPadFile`
            The high-level pad file

        Returns
        -------
        int
            The number of frames.
        """
        return padfile.number_of_frames

    @property
    def frame_shape(self):
        """Returns the size of each frame in this database.

        Returns
        -------
        (int, int, int)
            The (#Channels, Height, Width) which is (3, 1280, 720).
        """
        return REPLAYMOBILE_FRAME_SHAPE
