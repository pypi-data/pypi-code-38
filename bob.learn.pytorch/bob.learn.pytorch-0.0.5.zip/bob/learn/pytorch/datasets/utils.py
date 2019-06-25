#!/usr/bin/env python
# encoding: utf-8

import numpy

import torchvision.transforms as transforms

class FaceCropper():
  """
    Class to crop a face, based on eyes position
  """
  def __init__(self, cropped_height, cropped_width, color_channel='rgb'):
    # the face cropper
    from bob.bio.face.preprocessor import FaceCrop
    cropped_image_size = (cropped_height, cropped_width)
    right_eye_pos = (cropped_height // 5, cropped_width // 4 -1)
    left_eye_pos = (cropped_height // 5, cropped_width // 4 * 3)
    cropped_positions = {'leye': left_eye_pos, 'reye': right_eye_pos}
    self.color_channel = color_channel
    self.face_cropper = FaceCrop(cropped_image_size=cropped_image_size,
                                 cropped_positions=cropped_positions,
                                 color_channel=color_channel,
                                 dtype='uint8'
                                )

  def __call__(self, sample):
    cropped = self.face_cropper(sample['image'], sample['eyes'])
    sample['image'] = cropped
    if self.color_channel == 'gray': 
      sample['image'] = sample['image'][..., numpy.newaxis]
    return sample


class FaceCropAlign():
  """
    Wrapper to the FaceCropAlign of bob.pad.face preprocessor
  
  """

  def __init__(self, face_size, rgb_output_flag=False,
               use_face_alignment=True,
               alignment_type='lightcnn',
               face_detection_method='mtcnn',
               ):
    """ Init function

    Parameters
    ----------

    face_size: :obj:`int`
      The size of the cropped face (square)
    rgb_output_flag: :py:class:`bool`
      Return RGB cropped face if True, grayscale otherwise 
    use_face_alignment: :py:class:`bool`
      If set to True, the face will be aligned, using the facial landmarks detected locally
      Works only when ``face_detection_method is not None``.
    alignment_type: :py:class:`str`
      Specifies the alignment type to use if ``use_face_alignment`` is set to ``True``.
      Two methods are currently implemented:
      ``default`` which would do alignment by making eyes horizontally
      ``lightcnn`` which aligns the face such that eye center and mouth centers are aligned to
      predefined positions. This option overrides the face size option as the output required
      is always 128x128. This is suitable for use with LightCNN model.
    face_detection_method: :py:class:`str`
      A package to be used for face detection and landmark detection.
      Options supported by this class: "dlib" and "mtcnn"
    
    """
    from bob.pad.face.preprocessor import FaceCropAlign
    self.face_cropper = FaceCropAlign(face_size, 
                                      rgb_output_flag,
                                      use_face_alignment,
                                      alignment_type=alignment_type,
                                      face_detection_method=face_detection_method,
                                      )

  def __call__(self, sample):
    cropped = self.face_cropper(sample['image'])
    if cropped is None:
      print("Face not detected ...")
      cropped = numpy.zeros((128, 128))
    sample['image'] = cropped[..., numpy.newaxis]
    return sample


class RollChannels(object):
  """
    Class to transform a bob image into skimage.
    i.e. CxHxW to HxWxC
  """
  def __call__(self, sample):
    temp = numpy.rollaxis(numpy.rollaxis(sample['image'], 2),2)
    sample['image'] = temp
    return sample

class ToTensor(object):
  def __init__(self):
    self.op = transforms.ToTensor()

  def __call__(self, sample):
    if len(sample['image'].shape) == 2:
      sample['image'] = sample['image'][..., numpy.newaxis]
    sample['image'] = self.op(sample['image'])
    return sample

class Normalize(object):
  def __init__(self, mean, std):
    self.op = transforms.Normalize(mean, std)

  def __call__(self, sample):
    sample['image'] = self.op(sample['image'])
    return sample

class Resize(object):
  def __init__(self, size):
    self.op = transforms.Resize(size)

  def __call__(self, sample):
    # convert to PIL image
    from PIL.Image import fromarray
    img = fromarray(sample['image'].squeeze())
    img = self.op(img)
    sample['image'] = numpy.array(img)
    sample['image'] = sample['image'][..., numpy.newaxis]
    return sample

class ToGray(object):
  def __init__(self):
    self.op = transforms.Grayscale()

  def __call__(self, sample):
    # convert to PIL image
    from PIL.Image import fromarray
    img = fromarray(sample['image'].squeeze())
    img = self.op(img)
    sample['image'] = numpy.array(img)
    sample['image'] = sample['image'][..., numpy.newaxis]
    return sample


def map_labels(raw_labels, start_index=0):
  """
  Map the ID label to [0 - # of IDs]
  
  Parameters
  ----------
  raw_labels: list of :obj:`int`
    The labels of the samples 
  
  """
  possible_labels = sorted(list(set(raw_labels)))
  labels = numpy.array(raw_labels)

  for i in range(len(possible_labels)):
    l = possible_labels[i]
    labels[numpy.where(labels==l)[0]] = i + start_index

  return labels

from torch.utils.data import Dataset
import bob.io.base
import bob.io.image


class ConcatDataset(Dataset):
  """
  Class to concatenate two or more datasets for DR-GAN training

  **Parameters**

  datasets: list
    The list of datasets (as torch.utils.data.Dataset)
  """
  def __init__(self, datasets):

    self.transform = datasets[0].transform
    self.data_files = sum((d.data_files for d in datasets), [])
    self.pose_labels = sum((d.pose_labels for d in datasets), [])
    self.id_labels = sum((d.id_labels for d in datasets), [])

  def __len__(self):
      """
        return the length of the dataset (i.e. nb of examples)
      """
      return len(self.data_files)


  def __getitem__(self, idx):
      """
        return a sample from the dataset
      """
      image = bob.io.base.load(self.data_files[idx])
      identity = self.id_labels[idx]
      pose = self.pose_labels[idx]
      sample = {'image': image, 'id': identity, 'pose': pose}

      if self.transform:
        sample = self.transform(sample)

      return sample

class ChannelSelect(object):

  """Subselects or re-orders channels in a multi-channel image. Expects a 
  numpy.ndarray as input with size `HxWxnum_channels` and returns an image 
  with size `HxWxlen(selected_channels)`, where the last dimension is subselected
  using the indexes in the list `selected_channels`. 

  Attributes
  ----------

  selected_channels: list
    The indexes of the channels to be selected.

  img: numpy.ndarray
    A multi channel image, HxWxnum_channels
  """

  def __init__(self, selected_channels=[0,1,2,3]):

    """
    Parameters
    ----------
    selected_channels: list
      The indexes of the channels to be selected.

    """
    self.selected_channels = selected_channels

  def __call__(self, img):
    """
    Parameters
    ----------
    img: numpy.ndarray
      A multi channel image, HxWxnum_channels

    """
    return img[:,:,self.selected_channels]

  def __repr__(self):
    return self.__class__.__name__ + '(selected_channels={}, output channels ={})'.format(self.selected_channels, len(self.selected_channels))



class RandomHorizontalFlipImage(object):

  """Flips the image horizontally, works on numpy arrays. 

  Attributes
  ----------

  p: float
      Probability of image returned being flipped .
  """

  def __init__(self,p=0.5):

    """
    Parameters
    ----------
    p: float
      Probability of image returned being flipped .

    """
    self.p = p

  def __call__(self, img):
    """
    Parameters
    ----------
    img: numpy.ndarray
      A multi channel image, HxWxnum_channels

    """
    if numpy.random.random() < self.p:

      imgn=numpy.fliplr(img).copy()
    else:
      imgn=img.copy()

    return imgn

  def __repr__(self):
    return self.__class__.__name__ + '(Flipping Probability={})'.format(self.p)



