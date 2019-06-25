#!/usr/bin/env python
# encoding: utf-8

import os
import numpy

from torch.utils.data import Dataset, DataLoader

import bob.db.fargo
import bob.io.base
import bob.io.image

from bob.extension import rc
from bob.db.base import read_annotation_file

from .utils import map_labels


class FargoDataset(Dataset):
  """Class representing the FARGO dataset

  Only retrieves the RGB training set

  Attributes
  ----------
  original_directory : str
    The path to the data
  transform : `torchvision.transforms`
    The transform(s) to apply to the face images
  data_files : list of :obj:`str`
    The list of data files
  id_labels : list of :obj:`int`
    The list of identities, for each data file
  annotations : 
    The annotations (eyes center) corresponding to each file 

  """
  def __init__(self, original_directory=rc['bob.db.fargo.directory'],
                     annotation_directory=rc['bob.db.fargo.annotation_directory'],
                     transform=None, start_index=0, modality='rgb'):
    """Init function

    Parameters
    ----------
    original_directory : str
      The path to the data
    annotation_directory : str
      The path to the annotations
    transform : :py:class:`torchvision.transforms`
      The transform(s) to apply to the face images
    start_index : int
      label of the first identity (useful if you use several databases)
    
    """
    self.transform = transform
    self.data_files = []
    self.annotations = []
    id_labels = []

    db = bob.db.fargo.Database(original_directory=original_directory)
    objs = db.objects(purposes='train', modality=modality)
 
    for o in objs:
      self.data_files.append(o.make_path(directory=original_directory, extension='.png'))
      id_labels.append(o.client_id)
      annotation_file = os.path.join(annotation_directory, o.path + '.pos')
      self.annotations.append(read_annotation_file(annotation_file, 'eyecenter'))

    self.id_labels = map_labels(id_labels)

  def __len__(self):
    """Returns the length of the dataset (i.e. nb of examples)
    
    Returns
    -------
    int 
      the number of examples in the dataset
    
    """
    return len(self.data_files)


  def __getitem__(self, idx):
    """Returns a sample from the dataset
   
    Returns
    -------
    dict
      an example of the dataset, containing the 
      transformed face image and its identity
    
    """
    image = bob.io.base.load(self.data_files[idx])
    eyescenter = self.annotations[idx]
    identity = self.id_labels[idx]
    sample = {'image': image, 'label': identity, 'eyes' : eyescenter}

    if self.transform:
      sample = self.transform(sample)

    return sample
