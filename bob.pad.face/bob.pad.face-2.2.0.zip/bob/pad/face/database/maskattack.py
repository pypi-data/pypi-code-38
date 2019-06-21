#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import numpy as np
import bob.io.video
from bob.bio.video import FrameSelector, FrameContainer
from bob.pad.face.database import VideoPadFile  
from bob.pad.base.database import PadDatabase

class MaskAttackPadFile(VideoPadFile):
    """
    A high level implementation of the File class for the 3DMAD database.

    Attributes
    ----------
    f : :py:class:`object`
      An instance of the File class defined in the low level db interface
      of the 3DMAD database, in the bob.db.maskattack.models.py file.
    
    """

    def __init__(self, f):
        """Init function
        
        Parameters
        ----------
        f : :py:class:`object`
          An instance of the File class defined in the low level db interface
          of the 3DMAD database, in the bob.db.maskattack.models.py file.
        
        """
        self.f = f
        if f.is_real():
            attack_type = None
        else:
            attack_type = 'mask'

        super(MaskAttackPadFile, self).__init__(
            client_id=f.client_id,
            path=f.path,
            attack_type=attack_type,
            file_id=f.id)

    def load(self, directory=None, extension='.avi', frame_selector=FrameSelector(selection_style='all')):
        """Overridden version of the load method defined in ``VideoPadFile``.

        Parameters
        ----------
        directory : :py:class:`str`
          String containing the path to the 3DMAD database 
          (generated sequences from original data).
        extension : :py:class:`str`
          Extension of the video files 
        frame_selector : :py:class:`bob.bio.video.FrameSelector`
            The frame selector to use.

        Returns
        -------
        video_data : :py:class:`bob.bio.video.utils.FrameContainer`
          video data stored in a FrameContainer
        
        """
        vfilename = self.make_path(directory, extension)
        video = bob.io.video.reader(vfilename)
        video_data_array = video.load()
        return frame_selector(video_data_array)


class MaskAttackPadDatabase(PadDatabase):
    """High level implementation of the Database class for the 3DMAD database.
    
    Attributes
    ----------
    db : :py:class:`bob.db.maskattack.Database`
      the low-level database interface
    low_level_group_names : list of :py:obj:`str`
      the group names in the low-level interface (world, dev, test)
    high_level_group_names : list of :py:obj:`str`
      the group names in the high-level interface (train, dev, eval)

    """

    def __init__(self, protocol='classification', original_directory=None, original_extension='.avi', **kwargs):
        """Init function

        Parameters
        ----------
        protocol : :py:class:`str`
          The name of the protocol that defines the default experimental setup for this database.
        original_directory : :py:class:`str`
          The directory where the original data of the database are stored.
        original_extension : :py:class:`str`
          The file name extension of the original data.
        
        """
        from bob.db.maskattack import Database as LowLevelDatabase
        self.db = LowLevelDatabase()

        self.low_level_group_names = ('world', 'dev', 'test')  
        self.high_level_group_names = ('train', 'dev', 'eval')

        super(MaskAttackPadDatabase, self).__init__(
            name='maskattack',
            protocol=protocol,
            original_directory=original_directory,
            original_extension=original_extension,
            **kwargs)


    @property
    def original_directory(self):
        return self.db.original_directory


    @original_directory.setter
    def original_directory(self, value):
        self.db.original_directory = value

    def objects(self,
                groups=None,
                protocol='classification',
                purposes=None,
                model_ids=None,
                **kwargs):
        """Returns a list of MaskAttackPadFile objects, which fulfill the given restrictions.

        Parameters
        ----------
        groups : list of :py:class:`str`
          The groups of which the clients should be returned.
          Usually, groups are one or more elements of ('train', 'dev', 'eval')
        protocol : :py:class:`str`
          The protocol for which the clients should be retrieved.
        purposes : :py:class:`str`
          The purposes for which File objects should be retrieved.
          Usually it is either 'real' or 'attack'.
        model_ids
          This parameter is not supported in PAD databases yet.

        Returns
        -------
        files : :py:class:`MaskAttackPadFile`
            A list of MaskAttackPadFile objects.
        """

        groups = self.convert_names_to_lowlevel(groups, self.low_level_group_names, self.high_level_group_names)

        if groups is not None:
          
          # for training
          lowlevel_purposes = []
          if 'world' in groups and purposes == 'real':
            lowlevel_purposes.append('trainReal') 
          if 'world' in groups and purposes == 'attack':
            lowlevel_purposes.append('trainMask') 

          # for dev and eval
          if ('dev' in groups or 'test' in groups) and purposes == 'real':
            lowlevel_purposes.append('classifyReal')
          if ('dev' in groups or 'test' in groups) and purposes == 'attack':
            lowlevel_purposes.append('classifyMask')

        files = self.db.objects(sets=groups, purposes=lowlevel_purposes, **kwargs)
        files = [MaskAttackPadFile(f) for f in files]

        return files

    
    def annotations(self, file):
        """Return annotations for a given file object.

        Parameters
        ----------
        f : :py:class:`MaskAttackPadFile`
          An instance of ``MaskAttackPadFile`` defined above.

        Returns
        -------
        annotations : :py:class:`dict`
          A dictionary containing the annotations for each frame in the video.
          Dictionary structure: ``annotations = {'1': frame1_dict, '2': frame1_dict, ...}``.
        """
        return None

