#!/usr/bin/env python
# vim: set fileencoding=utf-8 :


import os
import shutil
import struct
import gzip
import numpy

from bob.db.base.utils import check_parameters_for_validity


class Database:
  """Wrapper class for the MNIST database of handwritten digits.

  The original database files are distributed over:
  http://yann.lecun.com/exdb/mnist/.
  """


  def __init__(self):

    from .driver import Interface
    f = Interface().files()

    self.train_images = f[0]
    self.train_labels = f[1]
    self.test_images  = f[2]
    self.test_labels  = f[3]

    self._labels = set(range(0,10))
    self._groups = ('train', 'test')


  def _read_labels(self, fname):
    """Reads the labels from the original MNIST label binary file"""

    with gzip.open(fname, 'rb') as f:

      # reads 2 big-ending integers
      magic_nr, n_examples = struct.unpack(">II", f.read(8))
      # reads the rest, using an uint8 dataformat (endian-less)

      labels = numpy.fromstring(f.read(), dtype='uint8')

      return labels


  def _read_images(self, fname):
    """Reads the images from the original MNIST label binary file"""

    with gzip.open(fname, 'rb') as f:

      # reads 4 big-ending integers
      magic_nr, n_examples, rows, cols = struct.unpack(">IIII", f.read(16))
      shape = (n_examples, rows*cols)

      # reads the rest, using an uint8 dataformat (endian-less)
      images = numpy.fromstring(f.read(), dtype='uint8').reshape(shape)

      return images


  def labels(self):
    """Returns the vector of labels
    """

    return self._labels


  def groups(self):
    """Returns the vector of groups
    """

    return self._groups


  def data(self, groups=None, labels=None):
    """Loads the MNIST samples and labels and returns them in NumPy arrays


    Parameters:

      groups (:py:class:`str` or :py:class:`list`): One of the groups ``train``
        or ``test``, or a list with both of them (which is the default)

      labels (:py:class:`int` or :py:class:`list`): A subset of the labels
        (digits 0 to 9) (everything is the default)


    Returns:

      numpy.ndarray: A 2D array representing the digit images, with as many
      rows as examples in the dataset, as many columns as pixels (actually,
      there are 28x28 = 784 rows). The pixels of each image are unrolled in
      C-scan order (i.e., first row 0, then row 1, etc.)

      numpy.ndarray: A 1D array with as many elements as examples in the
      dataset, containing the labels for each image returned above.

    """

    # check if groups set are valid
    groups = check_parameters_for_validity(groups, "group", self._groups)
    vlabels = check_parameters_for_validity(labels, "label", self._labels)

    # Reads data from the groups
    if 'train' in groups and 'test' in groups:
      images1 = self._read_images(self.train_images)
      labels1 = self._read_labels(self.train_labels)
      images2 = self._read_images(self.test_images)
      labels2 = self._read_labels(self.test_labels)
      images = numpy.vstack([images1,images2])
      labels = numpy.hstack([labels1,labels2])

    elif 'train' in groups:
      images = self._read_images(self.train_images)
      labels = self._read_labels(self.train_labels)

    elif 'test' in groups:
      images = self._read_images(self.test_images)
      labels = self._read_labels(self.test_labels)

    else:
      images = numpy.ndarray(shape=(0,784), dtype=numpy.uint8)
      labels = numpy.ndarray(shape=(0,), dtype=numpy.uint8)

    # List of indices for which the labels are in the list of requested labels
    indices = numpy.where(numpy.array([v in vlabels for v in labels]))[0]
    images = images[indices,:]
    labels = labels[indices]

    return images, labels
