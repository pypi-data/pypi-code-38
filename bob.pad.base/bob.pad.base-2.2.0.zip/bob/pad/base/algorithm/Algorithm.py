#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Wed 19 Aug 13:43:21 2015
#

import numpy
import os
from bob.bio.base import utils


class Algorithm(object):
    """This is the base class for all anti-spoofing algorithms.
    It defines the minimum requirements for all derived algorithm classes.

    Call the constructor in derived class implementations.
    If your derived algorithm performs feature projection, please register this here.
    If it needs training for the projector, please set this here, too.

    **Parameters:**

    performs_projection : bool
      Set to ``True`` if your derived algorithm performs a projection.
      Also implement the :py:meth:`project` function, and the :py:meth:`load_projector` if necessary.

    requires_projector_training : bool
      Only valid, when ``performs_projection = True``.
      Set this flag to ``False``, when the projection is applied, but the projector does not need to be trained.

    kwargs : ``key=value`` pairs
      A list of keyword arguments to be written in the `__str__` function.

    """

    def __init__(
            self,
            performs_projection=False,  # enable if your tool will project the features
            requires_projector_training=True,  # by default, the projector needs training, if projection is enabled
            **kwargs  # parameters from the derived class that should be reported in the __str__() function
    ):
        self.performs_projection = performs_projection
        self.requires_projector_training = performs_projection and requires_projector_training
        self._kwargs = kwargs

    def __str__(self):
        """__str__() -> info

        This function returns all parameters of this class (and its derived class).

        **Returns:**

        info : str
          A string containing the full information of all parameters of this (and the derived) class.
        """
        return "%s(%s)" % (str(self.__class__), ", ".join(
            ["%s=%s" % (key, value) for key, value in self._kwargs.items() if value is not None]))

    def project(self, feature):
        """project(feature) -> projected

        This function will project the given feature.
        It must be overwritten by derived classes, as soon as ``performs_projection = True`` was set in the constructor.
        It is assured that the :py:meth:`load_projector` was called once before the ``project`` function is executed.

        **Parameters:**

        feature : object
          The feature to be projected.

        **Returns:**

        projected : object
          The projected features.
          Must be writable with the :py:meth:`write_feature` function and readable with the :py:meth:`read_feature` function.

        """
        raise NotImplementedError("Please overwrite this function in your derived class")

    def score(self, toscore):
        """score(toscore) -> score

        This function will compute the score for the given object ``toscore``.
        It must be overwritten by derived classes.

        **Parameters:**

        toscore : object
          The object to compute the score for. This will be the output of
          extractor if performs_projection is False, otherwise this will be the
          output of project method of the algorithm.

        **Returns:**

        score : float
          A score value for the object ``toscore``.
        """
        raise NotImplementedError("Please overwrite this function in your derived class")

    def score_for_multiple_projections(self, toscore):
        """scorescore_for_multiple_projections(toscore) -> score

        This function will compute the score for a list of objects in ``toscore``.
        It must be overwritten by derived classes.

        **Parameters:**

        toscore : [object]
          A list of objects to compute the score for.

        **Returns:**

        score : float
          A score value for the object ``toscore``.
        """
        raise NotImplementedError("Please overwrite this function in your derived class")

    ############################################################
    ### Special functions that might be overwritten on need
    ############################################################

    def write_feature(self, feature, feature_file):
        """Saves the given *projected* feature to a file with the given name.
        In this base class implementation:

        - If the given feature has a ``save`` attribute, it calls ``feature.save(bob.io.base.HDF5File(feature_file), 'w')``.
          In this case, the given feature_file might be either a file name or a bob.io.base.HDF5File.
        - Otherwise, it uses :py:func:`bob.io.base.save` to do that.

        If you have a different format, please overwrite this function.

        Please register 'performs_projection = True' in the constructor to enable this function.

        **Parameters:**

        feature : object
          A feature as returned by the :py:meth:`project` function, which should be written.

        feature_file : str or :py:class:`bob.io.base.HDF5File`
          The file open for writing, or the file name to write to.
        """
        utils.save(feature, feature_file)

    def read_feature(self, feature_file):
        """read_feature(feature_file) -> feature

        Reads the *projected* feature from file.
        In this base class implementation, it uses :py:func:`bob.io.base.load` to do that.
        If you have different format, please overwrite this function.

        Please register ``performs_projection = True`` in the constructor to enable this function.

        **Parameters:**

        feature_file : str or :py:class:`bob.io.base.HDF5File`
          The file open for reading, or the file name to read from.

        **Returns:**

        feature : object
          The feature that was read from file.
        """
        return utils.load(feature_file)

    def train_projector(self, training_features, projector_file):
        """This function can be overwritten to train the feature projector.
        If you do this, please also register the function by calling this base class constructor
        and enabling the training by ``requires_projector_training = True``.

        **Parameters:**

        training_features : [object] or [[object]]
          A list of *extracted* features that can be used for training the projector.
          Features will be provided in a single list

        projector_file : str
          The file to write.
          This file should be readable with the :py:meth:`load_projector` function.
        """
        raise NotImplementedError(
            "Please overwrite this function in your derived class, or unset the 'requires_projector_training' option in the constructor.")

    def load_projector(self, projector_file):
        """Loads the parameters required for feature projection from file.
        This function usually is useful in combination with the :py:meth:`train_projector` function.
        In this base class implementation, it does nothing.

        Please register `performs_projection = True` in the constructor to enable this function.

        **Parameters:**

        projector_file : str
          The file to read the projector from.
        """
        pass
