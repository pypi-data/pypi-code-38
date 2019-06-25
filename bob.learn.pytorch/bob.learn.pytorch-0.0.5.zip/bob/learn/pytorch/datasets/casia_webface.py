#!/usr/bin/env python
# encoding: utf-8

import os
import numpy

from torch.utils.data import Dataset, DataLoader

import bob.io.base
import bob.io.image

from .utils import map_labels


class CasiaWebFaceDataset(Dataset):
  """Class representing the CASIA WebFace dataset

  Note that here the only label is identity

  Attributes
  ----------
  root_dir : str
    The path to the data
  transform : `torchvision.transforms`
    The transform(s) to apply to the face images
  data_files : list of :obj:`str`
    The list of data files
  id_labels : list of :obj:`int`
    The list of identities, for each data file

  """
  def __init__(self, root_dir, transform=None, start_index=0):
    """Init function

    Parameters
    ----------
    root_dir : str
      The path to the data
    transform : :py:class:`torchvision.transforms`
      The transform(s) to apply to the face images
    start_index : int
      label of the first identity (useful if you use
      several databases)
    
    """
    self.root_dir = root_dir
    self.transform = transform
    self.data_files = []
    id_labels = []

    for root, dirs, files in os.walk(self.root_dir):
      for name in files:
        filename = os.path.split(os.path.join(root, name))[-1]
        path = root.split(os.sep)
        subject = int(path[-1])
        self.data_files.append(os.path.join(root, name))
        id_labels.append(subject)

    self.id_labels = map_labels(id_labels, start_index)


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
    identity = self.id_labels[idx]
    sample = {'image': image, 'label': identity}

    if self.transform:
      sample = self.transform(sample)

    return sample


class CasiaDataset(Dataset):
  """Class representing the CASIA WebFace dataset

  Note that in this class, two labels are provided
  with each image: identity and pose.

  Pose labels have been automatically inferred using
  the ROC face recognirion SDK from RankOne.

  There are 13 pose labels, corresponding to cluster
  of 15 degrees, ranging from -90 degress (left profile)
  to 90 degrees (right profile)

  Attributes
  ----------
  root_dir: str
    The path to the data
  transform : `torchvision.transforms`
    The transform(s) to apply to the face images
  data_files: list of :obj:`str`
    The list of data files
  id_labels : list of :obj:`int`
    The list of identities, for each data file
  pose_labels : list of :obj:`int`
    The list containing the pose labels 

  """
  def __init__(self, root_dir, transform=None, start_index=0):
    """Init function

    Parameters
    ----------
    root_dir: str
      The path to the data
    transform: :py:class:`torchvision.transforms`
      The transform(s) to apply to the face images
    start_index : int
      label of the first identity (useful if you use
      several databases)
    
    """
    self.root_dir = root_dir
    self.transform = transform
  
    dir_to_pose_label = {'l90': '0',
                         'l75': '1',
                         'l60': '2',
                         'l45': '3',
                         'l30': '4',
                         'l15': '5',
                         '0'  : '6',
                         'r15': '7',
                         'r30': '8',
                         'r45': '9',
                         'r60': '10',
                         'r75': '11',
                         'r90': '12',
                        }

    # get all the needed file, the pose labels, and the id labels
    self.data_files = []
    self.pose_labels = []
    id_labels = []

    for root, dirs, files in os.walk(self.root_dir):
      for name in files:
        filename = os.path.split(os.path.join(root, name))[-1]
        path = root.split(os.sep)
        subject = int(path[-1])
        cluster = path[-2]
        self.data_files.append(os.path.join(root, name))
        self.pose_labels.append(int(dir_to_pose_label[cluster]))
        id_labels.append(subject)
 
    self.id_labels = map_labels(id_labels, start_index)
      
    
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
      transformed face image, its identity and pose information
    
    """
    image = bob.io.base.load(self.data_files[idx])
    identity = self.id_labels[idx]
    pose = self.pose_labels[idx]
    sample = {'image': image, 'label': identity, 'pose': pose}

    if self.transform:
      sample = self.transform(sample)

    return sample
