#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
@author: Olegs Nikisins
"""

#==============================================================================
# Import what is needed here:

import torch.utils.data as data

import os

import random

random.seed( a = 7 )

import numpy as np

from torchvision import transforms

import h5py


#==============================================================================
def get_file_names_and_labels(files, data_folder, extension = ".hdf5", hldi_type = "pad"):
    """
    Get absolute names of the corresponding file objects and their class labels,
    as well as keys defining name of the frame to load the data from.

    Attributes
    ----------

    files : [File]
        A list of files objects defined in the High Level Database Interface
        of the particular database.

    data_folder : str
        A directory containing the training data.

    extension : str
        Extension of the data files. Default: ".hdf5" .

    hldi_type : str
        Type of the high level database interface. Default: "pad".
        Note: this is the only type supported at the moment.

    Returns
    -------

    file_names_labels_keys : [(str, int, str)]
        A list of tuples, where each tuple contain an absolute filename,
        a corresponding label of the class, and a key defining the name of the
        frame to extract the data from.
    """

    file_names_labels_keys = []

    if hldi_type == "pad":

        for f in files:

            if f.attack_type is None:

                label = 1

            else:

                label = 0

            file_name = os.path.join(data_folder, f.path + extension)

            if os.path.isfile(file_name): # if file is available:

                with h5py.File(file_name, "r") as f_h5py:

                    file_keys = list(f_h5py.keys())

                #removes the 'FrameIndexes' key
                file_keys=[f for f in file_keys if f!='FrameIndexes' ]

                # elements of tuples in the below list are as follows:
                # a filename a key is extracted from,
                # a label corresponding to the file,
                # a key defining a frame from the file.
                file_names_labels_keys = file_names_labels_keys + [(file_name, label, key) for file_name, label, key in
                                                                   zip([file_name]*len(file_keys), [label]*len(file_keys), file_keys)]

    return file_names_labels_keys


#==============================================================================
class DataFolder(data.Dataset):
    """
    A generic data loader compatible with Bob High Level Database Interfaces
    (HLDI). Only HLDI's of ``bob.pad.face`` are currently supported.

    The basic functionality is composed of two steps: load the data from hdf5
    file, and transform it using user defined transformation function.

    Two types of user defined transformations are supported:

    1. An instance of ``Compose`` transformation class from ``torchvision``
    package.

    2. A custom transformation function, which takes numpy.ndarray as input,
    and returns a transformed Tensor. The dimensionality of the output tensor
    must match the format expected by the network to be trained.

    Note: if no special transformation is needed, the ``transform``
    must at least convert an input numpy array to Tensor.

    Attributes
    ----------

    data_folder : str
        A directory containing the training data. Note, that the training data
        must be stored as a FrameContainers written to the hdf5 files. Other
        formats are currently not supported.

    transform : object
        A function ``transform`` takes an input numpy.ndarray sample/image,
        and returns a transformed version as a Tensor. Default: None.

    extension : str
        Extension of the data files. Default: ".hdf5".
        Note: this is the only extension supported at the moment.

    bob_hldi_instance : object
        An instance of the HLDI interface. Only HLDI's of bob.pad.face
        are currently supported.

    hldi_type : str
        String defining the type of the HLDI. Default: "pad".
        Note: this is the only option currently supported.

    groups : str or [str]
        The groups for which the clients should be returned.
        Usually, groups are one or more elements of ['train', 'dev', 'eval'].
        Default: ['train', 'dev', 'eval'].

    protocol : str
        The protocol for which the clients should be retrieved.
        Default: 'grandtest'.

    purposes : str or [str]
        The purposes for which File objects should be retrieved.
        Usually it is either 'real' or 'attack'.
        Default: ['real', 'attack'].

    allow_missing_files : bool
        The missing files in the ``data_folder`` will not break the
        execution if set to True.
        Default: True.
    """

    def __init__(self, data_folder,
                 transform = None,
                 extension = '.hdf5',
                 bob_hldi_instance = None,
                 hldi_type = "pad",
                 groups = ['train', 'dev', 'eval'],
                 protocol = 'grandtest',
                 purposes=['real', 'attack'],
                 allow_missing_files = True,
                 **kwargs):
        """
        Attributes
        ----------

        data_folder : str
            A directory containing the training data.

        transform : object
            A function ``transform`` takes an input numpy.ndarray sample/image,
            and returns a transformed version as a Tensor. Default: None.

        extension : str
            Extension of the data files. Default: ".hdf5".
            Note: this is the only extension supported at the moment.

        bob_hldi_instance : object
            An instance of the HLDI interface. Only HLDI's of bob.pad.face
            are currently supported.

        hldi_type : str
            String defining the type of the HLDI. Default: "pad".
            Note: this is the only option currently supported.

        groups : str or [str]
            The groups for which the clients should be returned.
            Usually, groups are one or more elements of ['train', 'dev', 'eval'].
            Default: ['train', 'dev', 'eval'].

        protocol : str
            The protocol for which the clients should be retrieved.
            Default: 'grandtest'.

        purposes : str or [str]
            The purposes for which File objects should be retrieved.
            Usually it is either 'real' or 'attack'.
            Default: ['real', 'attack'].

        allow_missing_files : bool
            The missing files in the ``data_folder`` will not break the
            execution if set to True.
            Default: True.
        """

        self.data_folder = data_folder
        self.transform = transform
        self.extension = extension
        self.bob_hldi_instance = bob_hldi_instance
        self.hldi_type = hldi_type
        self.groups = groups
        self.protocol = protocol
        self.purposes = purposes
        self.allow_missing_files = allow_missing_files

        if bob_hldi_instance is not None:

            files = bob_hldi_instance.objects(groups = self.groups,
                                              protocol = self.protocol,
                                              purposes = self.purposes,
                                              **kwargs)

            file_names_labels_keys = get_file_names_and_labels(files = files,
                                        data_folder = self.data_folder,
                                        extension = self.extension,
                                        hldi_type = self.hldi_type)

            if self.allow_missing_files: # return only existing files

                file_names_labels_keys = [f for f in file_names_labels_keys if os.path.isfile(f[0])]

        else:

            # TODO - add behaviour similar to image folder
            file_names_labels_keys = []

        self.file_names_labels_keys = file_names_labels_keys


    #==========================================================================
    def __getitem__(self, index):
        """
        Returns a **transformed** sample/image and a target class, given index.
        Two types of transformations are handled, see the doc-string of the
        class.

        Attributes
        ----------

        index : int
            An index of the sample to return.

        Returns
        -------

        np_img : Tensor
            Transformed sample.

        target : int
            Index of the class.
        """

        path, target, key = self.file_names_labels_keys[index]

        with h5py.File(path, "r") as f_h5py:

            img_array = np.array(f_h5py.get(key+'/array')) # The size now is (3 x W x H)

        if isinstance(self.transform, transforms.Compose): # if an instance of torchvision composed transformation

            if len(img_array.shape) == 3: # for color or multi-channel images

                img_array_tr = np.swapaxes(img_array, 1, 2)
                img_array_tr = np.swapaxes(img_array_tr, 0, 2)

                np_img =img_array_tr.copy()  # np_img is numpy.ndarray of shape HxWxC

            else: # for gray-scale images

                np_img=np.expand_dims(img_array_tr,2) # np_img is numpy.ndarray of size HxWx1


            if self.transform is not None:

                np_img = self.transform(np_img) # after this transformation np_img should be a tensor

        else: # if custom transformation function is given

            img_array_transformed = self.transform(img_array)

            return img_array_transformed, target
            # NOTE: make sure ``img_array_transformed`` converted to Tensor in your custom ``transform`` function.

        return np_img, target


    #==========================================================================
    def __len__(self):
        """
        Returns
        -------

        len : int
            The length of the file list.
        """
        return len(self.file_names_labels_keys)

