#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import numpy as np
import bob.io.video
from bob.bio.video import FrameSelector, FrameContainer
from bob.pad.face.database import VideoPadFile  
from bob.pad.base.database import PadDatabase

from bob.extension import rc

class CasiaSurfPadFile(VideoPadFile):
    """
    A high level implementation of the File class for the CASIA-SURF database.

    Note that this does not represent a file per se, but rather a sample
    that may contain more than one file.

    Attributes
    ----------
    f : :py:class:`object`
      An instance of the Sample class defined in the low level db interface
      of the CASIA-SURF database, in the bob.db.casiasurf.models.py file.
    
    """

    def __init__(self, s, stream_type):
      """ Init

      Parameters
      ----------
      s : :py:class:`object`
        An instance of the Sample class defined in the low level db interface
        of the CASIA-SURF database, in the bob.db.casiasurf.models.py file.
      stream_type: str of list of str
        The streams to be loaded.
      """
      self.s = s
      self.stream_type = stream_type
      if not isinstance(s.attack_type, str):
        attack_type = str(s.attack_type)
      else:
        attack_type = s.attack_type

      if attack_type == '0':
        attack_type = None

      super(CasiaSurfPadFile, self).__init__(
            client_id=s.id,
            file_id=s.id,
            attack_type=attack_type,
            path=s.id)
      

    def load(self, directory=rc['bob.db.casiasurf.directory'], extension='.jpg', frame_selector=FrameSelector(selection_style='all')):
        """Overloaded version of the load method defined in ``VideoPadFile``.

        Parameters
        ----------
        directory : :py:class:`str`
          String containing the path to the CASIA-SURF database 
        extension : :py:class:`str`
          Extension of the image files 
        frame_selector : :py:class:`bob.bio.video.FrameSelector`
            The frame selector to use.

        Returns
        -------
        dict:
          image data for multiple streams stored in the dictionary. 
          The structure of the dictionary: ``data={"stream1_name" : numpy array, "stream2_name" : numpy array}``
          Names of the streams are defined in ``self.stream_type``.
        """
        return self.s.load(directory, extension, modality=self.stream_type)


class CasiaSurfPadDatabase(PadDatabase): 
    """High level implementation of the Database class for the 3DMAD database.
   
    Note that at the moment, this database only contains a training and validation set.

    The protocol specifies the modality(ies) to load.

    Attributes
    ----------
    db : :py:class:`bob.db.casiasurf.Database`
      the low-level database interface
    low_level_group_names : list of :py:obj:`str`
      the group names in the low-level interface (world, dev, test)
    high_level_group_names : list of :py:obj:`str`
      the group names in the high-level interface (train, dev, eval)

    """
       
    def __init__(self, protocol='all', original_directory=rc['bob.db.casiasurf.directory'], original_extension='.jpg', **kwargs):
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

      from bob.db.casiasurf import Database as LowLevelDatabase
      self.db = LowLevelDatabase()

      self.low_level_group_names = ('train', 'validation', 'test')  
      self.high_level_group_names = ('train', 'dev', 'eval')

      super(CasiaSurfPadDatabase, self).__init__(
          name='casiasurf',
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
                protocol='all',
                purposes=None,
                model_ids=None,
                **kwargs):
        """Returns a list of CasiaSurfPadFile objects, which fulfill the given restrictions.

        Parameters
        ----------
        groups : list of :py:class:`str`
          The groups of which the clients should be returned.
          Usually, groups are one or more elements of ('train', 'dev', 'eval')
        protocol : :py:class:`str`
          The protocol for which the samples should be retrieved.
        purposes : :py:class:`str`
          The purposes for which Sample objects should be retrieved.
          Usually it is either 'real' or 'attack'
        model_ids
          This parameter is not supported in PAD databases yet.

        Returns
        -------
        samples : :py:class:`CasiaSurfPadFilePadFile`
            A list of CasiaSurfPadFile objects.
        """

        groups = self.convert_names_to_lowlevel(groups, self.low_level_group_names, self.high_level_group_names)

        if groups is not None:
          
          # for training
          lowlevel_purposes = []
          if 'train' in groups and 'real' in purposes:
            lowlevel_purposes.append('real') 
          if 'train' in groups and 'attack' in purposes:
            lowlevel_purposes.append('attack') 

          # for dev
          if 'validation' in groups and 'real' in purposes:
            lowlevel_purposes.append('real') 
          if 'validation' in groups and 'attack' in purposes:
            lowlevel_purposes.append('attack') 
          
          # for eval
          if 'test' in groups and 'attack' in purposes:
            lowlevel_purposes.append('unknown')

        samples = self.db.objects(groups=groups, purposes=lowlevel_purposes, **kwargs)
        samples = [CasiaSurfPadFile(s, stream_type=protocol) for s in samples]
        return samples

    
    def annotations(self, file):
        """No annotations are provided with this DB
        """
        return None
