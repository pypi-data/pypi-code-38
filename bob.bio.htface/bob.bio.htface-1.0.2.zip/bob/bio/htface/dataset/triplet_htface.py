#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import numpy
import bob.core
from functools import partial
import tensorflow as tf
from bob.learn.tensorflow.dataset.triplet_image import image_augmentation_parser

numpy.random.seed(10)
logger = bob.core.log.setup("bob.learn.tensorflow")


def shuffle_data_and_labels_image_augmentation(database, protocol, data_shape, data_type,
                                               batch_size, epochs=None, buffer_size=10**3,
                                               gray_scale=False, 
                                               output_shape=None,
                                               random_flip=False,
                                               random_brightness=False,
                                               random_contrast=False,
                                               random_saturation=False,
                                               per_image_normalization=True, 
                                               groups="world", purposes="train",
                                               extension=None):
    """
    Dump random batches for siamese networks using heterogeneous face databases
    
    The batches returned with tf.Session.run() with be in the following format:
    **data** a dictionary containing the keys ['anchor', 'right'], each one representing 
    one element of the branch of the triplet
    
    **Parameters**

       database:
          List containing the path of the images
       
       protocol:
          List containing the labels (needs to be in EXACT same order as filenames)
          
       data_shape:
          Samples shape saved in the tf-record
          
       data_type:
          tf data type(https://www.tensorflow.org/versions/r0.12/resources/dims_types#data_types)
     
       batch_size:
          Size of the batch
          
       epochs:
           Number of epochs to be batched
       
       buffer_size:
            Size of the shuffle bucket

       gray_scale:
          Convert to gray scale?
          
       output_shape:
          If set, will randomly crop the image given the output shape

       random_flip:
          Randomly flip an image horizontally  (https://www.tensorflow.org/api_docs/python/tf/image/random_flip_left_right)

       random_brightness:
           Adjust the brightness of an RGB image by a random factor (https://www.tensorflow.org/api_docs/python/tf/image/random_brightness)

       random_contrast:
           Adjust the contrast of an RGB image by a random factor (https://www.tensorflow.org/api_docs/python/tf/image/random_contrast)

       random_saturation:
           Adjust the saturation of an RGB image by a random factor (https://www.tensorflow.org/api_docs/python/tf/image/random_saturation)

       per_image_normalization:
           Linearly scales image to have zero mean and unit norm.            
           
       groups:
       
       purposes:
       
       extension:
           If None, will load files using `tf.image.decode..` if set to `hdf5`, will load with `bob.io.base.load`

    """    
    parser = partial(image_augmentation_parser,
                 data_shape=data_shape,
                 data_type=data_type,
                 gray_scale=gray_scale, 
                 output_shape=output_shape,
                 random_flip=random_flip,
                 random_brightness=random_brightness,
                 random_contrast=random_contrast,
                 random_saturation=random_saturation,
                 per_image_normalization=per_image_normalization,
                 extension=extension)

    anchor_data, positive_data, negative_data = triplet_htface_generator(database, protocol, groups, purposes)
    dataset = tf.data.Dataset.from_tensor_slices((anchor_data, positive_data, negative_data))
    dataset = dataset.map(parser)

    # Shuffling
    dataset = dataset.shuffle(buffer_size).batch(batch_size).repeat(epochs)
    #dataset = dataset.prefetch(1) TODO: FOR THE r1.4
    data  = dataset.make_one_shot_iterator().get_next()
    return data


def triplet_htface_generator(database, protocol, groups="world", purposes="train", get_objects=False):
    """
    Triplet generator for Heterogeneous databases.
    Given two modalities A and B, the triplets are formed as the following:
    
    anchor = modality A
    positive = modality B
    negative = modality B
    
    Paramters
    ---------
    database:
    protocol:
    groups:
    purposes:
    get_objects:
    """
                 
    anchor_data = []
    positive_data = []
    negative_data = []
    def append(anchor, positive, negative):
        """
        Just appending one element in each list
        """
        anchor_data.append(anchor)
        positive_data.append(positive)
        negative_data.append(negative)
                           
    # List of samples from modality A
    samples_anchor = database.objects(protocol=protocol,
                                 groups=groups,
                                 purposes=purposes,
                                 modality=database.modalities[0])

    samples_modality_b = database.objects(protocol=protocol,
                                    groups=groups,
                                    purposes=purposes,
                                    modality=database.modalities[1])

    rounds = 5                                    
    # Doing several rounds to variate the number of negative pairs for each left side
    for _ in range(rounds):
        
        numpy.random.shuffle(samples_modality_b)
        genuine = True
        for a in samples_anchor:
            reference_identity = a.client_id

            # Getting the positive pair from modality B
            i = 0
            while samples_modality_b[i].client_id != reference_identity:
                i += 1
            p = samples_modality_b[i]

            # Getting the negative pair from modality B
            i = 0
            while samples_modality_b[i].client_id == reference_identity:
                i += 1
            n = samples_modality_b[i]

            if not get_objects:
                a = a.make_path(database.original_directory, database.original_extension)
                p = p.make_path(database.original_directory, database.original_extension)
                n = n.make_path(database.original_directory, database.original_extension)        
            
            append(a, p, n)

    return anchor_data, positive_data, negative_data



