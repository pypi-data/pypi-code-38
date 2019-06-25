#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import torch
from bob.learn.pytorch.datasets import DataFolder
from torch.utils.data import DataLoader
from torch import nn
import logging
logger = logging.getLogger("bob.learn.pytorch")


def get_parameter(args, configuration, keyword, default):
  """ Get the right value for a parameter

  The parameters are either defined in a separate configuration file
  or given directly via command-line. Note that the command-line
  has priority over the configuration file.

  As a convention, parameters made with more than one word (i.e. batch size)
  are provided with an underscore in the configuration file, and with an
  hyphen in the command-line:

    - configuration:  batch_size=64
    - command line:   --batch-size=64

  Parameters
  ----------
  args: dictionary
    The arguments as parsed from the command line.
  configuration: object
    The arguments given by the configuration file.
  keyword: string
    the keyword for the parameter to process (in the "configuration" style)
  default:
    The default value of the parameter

  Returns
  -------
  arg:
    The right value for the given keyword argument

  """

 # get the keyword in a "docopt" friendly format
  args_kw = '--' + keyword.replace('_', '-')

  # get the type of this argument
  _type = type(default)

  # get the default value
  arg_default = default

  # get the argument in the configuration file
  if hasattr(configuration, keyword):
    arg_config = getattr(configuration, keyword)

  # get the argument from the command-line
  arg_command = _type(args[args_kw])

  # if the argument was not specified in the config file
  if not hasattr(configuration, keyword):
    return arg_command
  else:
    if (arg_command == arg_default):
      return arg_config
    else:
      return arg_command


# =============================================================================
def comp_bce_loss_weights(target):
    """
    Compute the balancing weights for the BCE loss function.

    Arguments
    ---------
    target : Tensor
        Tensor containing class labels for each sample.
        Tensor of the size: ``[num_patches]``

    Returns
    -------
    weights : Tensor
        A tensor containing the weights for each sample.
    """

    weights = np.copy(target.cpu().numpy())

    pos_weight = 1-np.sum(weights)/len(weights)
    neg_weight = 1-pos_weight

    weights[weights==1]=pos_weight
    weights[weights==0]=neg_weight

#    weights = weights/np.sum(weights)

    weights = torch.Tensor(weights)

    return weights


# =============================================================================
def mean_std_normalize(features,
                       features_mean=None,
                       features_std=None):
    """
    The features in the input 2D array are mean-std normalized.
    The rows are samples, the columns are features. If ``features_mean``
    and ``features_std`` are provided, then these vectors will be used for
    normalization. Otherwise, the mean and std of the features is
    computed on the fly.

    Parameters
    ----------

    features : 2D :py:class:`numpy.ndarray`
        Array of features to be normalized.

    features_mean : 1D :py:class:`numpy.ndarray`
        Mean of the features. Default: None.

    features_std : 2D :py:class:`numpy.ndarray`
        Standart deviation of the features. Default: None.

    Returns
    -------

    features_norm : 2D :py:class:`numpy.ndarray`
        Normalized array of features.

    features_mean : 1D :py:class:`numpy.ndarray`
        Mean of the features.

    features_std : 1D :py:class:`numpy.ndarray`
        Standart deviation of the features.
    """

    features = np.copy(features)

    # Compute mean and std if not given:
    if features_mean is None:
        features_mean = np.mean(features, axis=0)

        features_std = np.std(features, axis=0)

    features_std[features_std==0.0]=1.0

    row_norm_list = []

    for row in features:  # row is a sample

        row_norm = (row - features_mean) / features_std

        row_norm_list.append(row_norm)

    features_norm = np.vstack(row_norm_list)

    return features_norm, features_mean, features_std


# =============================================================================
def compute_mean_std_bf_class(kwargs):
    """
    Compute mean-std normalization parameters using samples of the real class.
    The mean-std parameters are computed sample-wise / each feature has
    individual mean-std normalizers.

    Parameters
    ----------

    kwargs : dict
        Kwargs to initialize the DataFolder class.

    Returns
    -------
    features_mean: numpy array
        1D numpy array containing mean of the features computed using bona-fide
        samples of the training set.

    features_std: numpy array
        1D numpy array containing std of the features computed using bona-fide
        samples of the training set.
    """

    kwargs_copy = kwargs.copy()

    def transform(x): return x # don't do any transformationson on data

    kwargs_copy["transform"] = transform # no transformation
    kwargs_copy["purposes"] = ['real'] # use only real samples

    data_folder = DataFolder(**kwargs_copy) # initialize the DataFolder with new arguments

    dataloader = DataLoader(dataset = data_folder,
                            batch_size = data_folder.__len__(), # load all samples
                            shuffle = False)

    all_real_data = next(iter(dataloader)) # get all data as tensor

    all_real_data_np = all_real_data[0].numpy().squeeze() # get data in numpy format
    # the dimensions of "all_real_data_np" now is (n_samples x n_features)

    features_norm, features_mean, features_std = mean_std_normalize(all_real_data_np)

    return features_mean, features_std


# =============================================================================
class MeanStdNormalizer():
    """
    The functionality of this class can be split into sub-tasks:

    1. When **first** called, the mean-std normalization parameters are
    pre-computed using **bona-fide** samples from the training set of the
    database defined above.

    2. In the next calls, the pre-computed mean-std normalizers are used
    for normalization of the of the input training feature vectors.

    Arguments
    ---------
    kwargs : dict
        The kwargs used to inintialize an instance of the DataFolder class.
    """
    def __init__(self, kwargs):

        self.kwargs = kwargs
        self.features_mean = None
        self.features_std = None

    def __call__(self, x):
        """
        Pre-compute normalizers and use them for mean-std normalization.
        Also, converts normalized features to Tensors.

        Arguments
        ---------
        x : 1D :py:class:`numpy.ndarray`
            Feature vector to be normalizaed. The size is ``(n_features, )``

        Returns
        -------
        x_norm : :py:class:`torch.Tensor`
            Normalized feature vector of the size ``(1, n_features)``
        """

        if self.features_mean is None or self.features_std is None: # pre-compute normalization parameters

            logger.info ("Computing mean-std normalization parameters using real samples of the training set")
            # compute the normalization parameters on the fly:
            features_mean, features_std = compute_mean_std_bf_class(self.kwargs)

            # save normalization parameters:
            logger.info ("Setting the normalization parameters")
            self.features_mean = features_mean
            self.features_std = features_std

        # normalize the sample
        x_norm, _, _ = mean_std_normalize(features = np.expand_dims(x, axis=0),
                                          features_mean = self.features_mean,
                                          features_std = self.features_std)
        x_norm.squeeze()

        return torch.Tensor(x_norm).unsqueeze(0)


# =============================================================================
def weighted_bce_loss(output, img, target):
    """
    Returns a weighted BCE loss.

    Parameters
    ----------
    output : :py:class:`torch.Tensor`
        Tensor of the size: ``[num_patches, 1]``

    img : :py:class:`torch.Tensor`
        This argument is not used in current loss function, but is here to
        match the signature expected by the training script.

    target : :py:class:`torch.Tensor`
        Tensor containing class labels for each sample in ``img``.
        Tensor of the size: ``[num_patches]``

    Returns
    -------
    loss : :py:class:`torch.Tensor`
        Tensor containing loss value.
    """

    loss_type = nn.BCELoss()

    target = target.float()  # make sure the target is float, not int

    # convert "target" tensor from size [num_patches] to [num_patches, 1], to match "output" dimensions:
    target = target.view(-1, 1)

    weight = comp_bce_loss_weights(target)

    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    weight = weight.to(device)

    loss_type.weight = weight

    loss = loss_type(output, target)

    return loss

