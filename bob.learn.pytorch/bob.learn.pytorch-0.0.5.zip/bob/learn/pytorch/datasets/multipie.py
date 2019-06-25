#!/usr/bin/env python
# encoding: utf-8

import os

import torch
import numpy

from torch.utils.data import Dataset 

import bob.db.multipie
import bob.io.base
import bob.io.image

from .utils import map_labels

class MultiPIEDataset(Dataset):
  """Class representing the Multi-PIE dataset

  Attributes
  ----------
  root_dir : str
    The path to the data
  world : bool
    If you want to only use data corresponding to the world model
  transform: `torchvision.transforms`
    The transform(s) to apply to the face images
  data_files: list of str
    The list of data files
  id_labels : list of int
    The list of identities, for each data file
  pose_labels : list of int
    The list containing the pose labels 
  
  """

  def __init__(self, root_dir, world=False, frontal_only=False, transform=None):
    """Class representing the Multi-PIE dataset

    Attributes
    ----------
    root_dir : str
      The path to the data
    world : bool
      If you want to only use data corresponding to the world model
    frontal_only : bool
      If you want to only use frontal faces 
    transform: `torchvision.transforms`
      The transform(s) to apply to the face images
    
    """
    self.root_dir = root_dir
    self.transform = transform
    self.world = world
  
    camera_to_pose = {'11_0': 'l90',
                      '12_0': 'l75',
                      '09_0': 'l60',
                      '08_0': 'l45',
                      '13_0': 'l30',
                      '14_0': 'l15',
                      '05_1': '0',
                      '05_0': 'r15',
                      '04_1': 'r30',
                      '19_0': 'r45',
                      '20_0': 'r60',
                      '01_0': 'r75',
                      '24_0': 'r90'}

    camera_to_label = {'11_0': '0',
                       '12_0': '1',
                       '09_0': '2',
                       '08_0': '3',
                       '13_0': '4',
                       '14_0': '5',
                       '05_1': '6',
                       '05_0': '7',
                       '04_1': '8',
                       '19_0': '9',
                       '20_0': '10',
                       '01_0': '11',
                       '24_0': '12'}

    # get all the needed file, the pose labels, and the id labels
    self.data_files = []
    self.pose_labels = []
    id_labels = []

    db = bob.db.multipie.Database()
    
    if world: 
      c_set = db.clients(groups='world')
    else:
      c_set = db.clients()

    # filename and pose label are dependent on the camera
    for camera in sorted(db.camera_names()):
    
      if world:
        objs = db.objects(cameras=camera, groups='world')
      else:
        objs = db.objects(cameras=camera)
   
      # skip "high" cameras
      if (camera == '19_1') or (camera == '08_1'):
        continue

      # skip cameras that are not frontal if we want frontal only
      if (camera != '05_1') and frontal_only:
        continue

      for obj in objs:
        temp = os.path.split(obj.path)
        identity = int(temp[0].split('/')[2])
        id_labels.append(identity)
        cropped_filename = os.path.join(root_dir, camera_to_pose[camera], temp[1])
        cropped_filename += '.png'
        self.data_files.append(cropped_filename)
        self.pose_labels.append(int(camera_to_label[camera]))
      
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
      transformed face image, its identity and pose information
    
    """
    image = bob.io.base.load(self.data_files[idx])
    identity = self.id_labels[idx]
    pose = self.pose_labels[idx]
    sample = {'image': image, 'id': identity, 'pose': pose}

    if self.transform:
      sample = self.transform(sample)

    return sample
