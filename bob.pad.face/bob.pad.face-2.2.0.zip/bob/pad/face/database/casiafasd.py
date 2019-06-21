#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bob.bio.video import FrameSelector
from bob.extension import rc
from bob.io.video import reader
from bob.pad.base.database import PadDatabase
from bob.pad.face.database import VideoPadFile
from bob.db.base.utils import (
    check_parameter_for_validity, check_parameters_for_validity)
import numpy
import os


CASIA_FASD_FRAME_SHAPE = (3, 1280, 720)


class CasiaFasdPadFile(VideoPadFile):
    """
    A high level implementation of the File class for the CASIA_FASD database.
    """

    def __init__(self, f, original_directory=None):
        """
        Parameters
        ----------
        f : object
            An instance of the File class defined in the low level db interface
            of the CasiaFasd database, in bob.db.casia_fasd.models
        """

        self.f = f
        self.original_directory = original_directory

        if f.is_real():
            attack_type = None
        else:
            attack_type = 'attack/{}/{}'.format(f.get_type(), f.get_quality())

        super(CasiaFasdPadFile, self).__init__(
            client_id=str(f.get_clientid()),
            path=f.filename,
            attack_type=attack_type,
            file_id=f.filename)

    @property
    def frames(self):
        """Yields the frames of the biofile one by one.

        Yields
        ------
        :any:`numpy.array`
            A frame of the video. The size is :any:`CASIA_FASD_FRAME_SHAPE`.
        """
        vfilename = self.make_path(
            directory=self.original_directory, extension='.avi')
        for frame in reader(vfilename):
            # pad frames to 1280 x 720 so they all have the same size
            h, w = frame.shape[1:]
            H, W = CASIA_FASD_FRAME_SHAPE[1:]
            assert h <= H
            assert w <= W
            frame = numpy.pad(frame, ((0, 0), (0, H - h), (0, W - w)),
                              mode='constant', constant_values=0)
            yield frame

    @property
    def number_of_frames(self):
        """Returns the number of frames in a video file.

        Returns
        -------
        int
            The number of frames.
        """
        vfilename = self.make_path(
            directory=self.original_directory, extension='.avi')
        return reader(vfilename).number_of_frames

    @property
    def frame_shape(self):
        """Returns the size of each frame in this database.

        Returns
        -------
        (int, int, int)
            The (#Channels, Height, Width) which is
            :any:`CASIA_FASD_FRAME_SHAPE`.
        """
        return CASIA_FASD_FRAME_SHAPE

    @property
    def annotations(self):
        """Reads the annotations

        Returns
        -------
        annotations : :py:class:`dict`
            A dictionary containing the annotations for each frame in the
            video. Dictionary structure:
            ``annotations = {'1': frame1_dict, '2': frame1_dict, ...}``.Where
            ``frameN_dict = {'topleft': (row, col), 'bottomright':(row, col)}``
            is the dictionary defining the coordinates of the face bounding box
            in frame N.
        """
        annots = self.f.bbx()
        annotations = {}
        for i, v in enumerate(annots):
            topleft = (v[2], v[1])
            bottomright = (v[2] + v[4], v[1] + v[3])
            annotations[str(i)] = {'topleft': topleft,
                                   'bottomright': bottomright}
        return annotations

    def load(self, directory=None, extension='.avi',
             frame_selector=FrameSelector(selection_style='all')):
        """Loads the video file and returns in a
        :any:`bob.bio.video.FrameContainer`.

        Parameters
        ----------
        directory : :obj:`str`, optional
            The directory to load the data from.
        extension : :obj:`str`, optional
            The extension of the file to load.
        frame_selector : :any:`bob.bio.video.FrameSelector`, optional
            Which frames to select.

        Returns
        -------
        :any:`bob.bio.video.FrameContainer`
            The loaded frames inside a frame container.
        """
        directory = directory or self.original_directory
        return frame_selector(self.make_path(directory, extension))


class CasiaFasdPadDatabase(PadDatabase):
    """
    A high level implementation of the Database class for the CASIA_FASD
    database. Please run ``bob config set bob.db.casia_fasd.directory
    /path/to/casia_fasd_files`` in a terminal to point to the original files on
    your computer. This interface is different from the one implemented in
    ``bob.db.casia_fasd.Database``.
    """

    def __init__(
            self,
            # grandtest is the new modified protocol for this database
            protocol='grandtest',
            original_directory=rc['bob.db.casia_fasd.directory'],
            **kwargs):
        """
        Parameters
        ----------
        protocol : str or None
            The name of the protocol that defines the default experimental
            setup for this database. Only grandtest is supported for now.

        original_directory : str
            The directory where the original data of the database are stored.

        kwargs
            The arguments of the :py:class:`bob.pad.base.database.PadDatabase`
            base class constructor.
        """
        return super(CasiaFasdPadDatabase, self).__init__(
            name='casiafasd',
            protocol=protocol,
            original_directory=original_directory,
            original_extension='.avi',
            training_depends_on_protocol=True,
            **kwargs)

    def objects(self,
                groups=None,
                protocol=None,
                purposes=None,
                model_ids=None,
                **kwargs):
        """
        This function returns lists of CasiaFasdPadFile objects, which fulfill
        the given restrictions.

        Parameters
        ----------
        groups : :obj:`str` or [:obj:`str`]
            The groups of which the clients should be returned.
            Usually, groups are one or more elements of
            ('train', 'dev', 'eval')

        protocol : str
            The protocol for which the clients should be retrieved.
            Only 'grandtest' is supported for now. This protocol modifies the
            'Overall Test' protocol and adds some ids to dev set.

        purposes : :obj:`str` or [:obj:`str`]
            The purposes for which File objects should be retrieved either
            'real' or 'attack' or both.

        model_ids
            Ignored.

        **kwargs
            Ignored.

        Returns
        -------
        files : [CasiaFasdPadFile]
            A list of CasiaFasdPadFile objects.
        """
        groups = check_parameters_for_validity(
            groups, 'groups', ('train', 'dev', 'eval'),
            ('train', 'dev', 'eval'))
        protocol = check_parameter_for_validity(
            protocol, 'protocol', ('grandtest'), 'grandtest')
        purposes = check_parameters_for_validity(
            purposes, 'purposes', ('real', 'attack'), ('real', 'attack'))

        qualities = ('low', 'normal', 'high')
        types = ('warped', 'cut', 'video')
        from bob.db.casia_fasd.models import File

        files = []

        db_mappings = {
            'real_normal': '1',
            'real_low': '2',
            'real_high': 'HR_1',
            'warped_normal': '3',
            'warped_low': '4',
            'warped_high': 'HR_2',
            'cut_normal': '5',
            'cut_low': '6',
            'cut_high': 'HR_3',
            'video_normal': '7',
            'video_low': '8',
            'video_high': 'HR_4'
        }

        # identitites 1-15 are for train, 16-20 are dev, and 21-50 for eval
        grp_id_map = {
            'train': list(range(1, 16)),
            'dev': list(range(16, 21)),
            'eval': list(range(21, 51)),
        }
        grp_map = {
            'train': 'train',
            'dev': 'train',
            'eval': 'test',
        }

        for g in groups:
            ids = grp_id_map[g]
            for i in ids:
                cur_id = i
                if g == 'eval':
                    cur_id = i - 20
                    # the id within the group subset

                # this group name (grp) is only train and test
                grp = grp_map[g]

                folder_name = grp + '_release'

                for q in qualities:
                    for c in purposes:
                        # the class real doesn't have any different types, only
                        # the attacks can be of different type
                        if c == 'real':
                            filename = os.path.join(folder_name, "%d" % cur_id,
                                                    db_mappings['real_' + q])
                            files.append(CasiaFasdPadFile(
                                File(filename, c, grp),
                                self.original_directory))
                        else:
                            for t in types:
                                filename = os.path.join(
                                    folder_name, "%d" % cur_id,
                                    db_mappings[t + '_' + q])
                                files.append(CasiaFasdPadFile(
                                    File(filename, c, grp),
                                    self.original_directory))
        return files

    def annotations(self, padfile):
        return padfile.annotations

    def frames(self, padfile):
        return padfile.frames

    def number_of_frames(self, padfile):
        return padfile.number_of_frames

    @property
    def frame_shape(self):
        return CASIA_FASD_FRAME_SHAPE
