#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Wed 19 Aug 13:43:21 2015
#


import bob.io.base
import os

import logging

logger = logging.getLogger("bob.pad.base")

from .FileSelector import FileSelector
from .extractor import read_features
from bob.bio.base import utils


def train_projector(algorithm, extractor, allow_missing_files=False, force=False):
    """Trains the feature projector using extracted features of the ``'train'`` group, if the algorithm requires projector training.

    This function should only be called, when the ``algorithm`` actually requires projector training.
    The projector of the given ``algorithm`` is trained using extracted features.
    It writes the projector to the file specified by the :py:class:`bob.pad.base.tools.FileSelector`.
    By default, if the target file already exist, it is not re-created.

    **Parameters:**

    algorithm : py:class:`bob.pad.base.algorithm.Algorithm` or derived
      The algorithm, in which the projector should be trained.

    extractor : py:class:`bob.bio.base.extractor.Extractor` or derived
      The extractor, used for reading the training data.

    force : bool
      If given, the projector file is regenerated, even if it already exists.
    """
    if not algorithm.requires_projector_training:
        logger.warn("The train_projector function should not have been called, "
                    "since the algorithm does not need projector training.")
        return

    # the file selector object
    fs = FileSelector.instance()

    if utils.check_file(fs.projector_file, force, 1000):
        logger.info("- Projection: projector '%s' already exists.", fs.projector_file)
    else:
        bob.io.base.create_directories_safe(os.path.dirname(fs.projector_file))
        # train projector
        logger.info("- Projection: loading training data")
        train_files = fs.training_list('extracted', 'train_projector')
        train_features = read_features(train_files, extractor, True, allow_missing_files)
        logger.info("- Projection: training projector '%s' using %d real files and %d attack files: ", fs.projector_file,
                    len(train_files[0]), len(train_files[1]))

        # perform training
        algorithm.train_projector(train_features, fs.projector_file)


def project(algorithm, extractor, groups=None, indices=None, allow_missing_files=False, force=False):
    """Projects the features for all files of the database.

    The given ``algorithm`` is used to project all features required for the current experiment.
    It writes the projected data into the directory specified by the :py:class:`bob.pad.base.tools.FileSelector`.
    By default, if target files already exist, they are not re-created.

    The extractor is only used to load the data in a coherent way.

    **Parameters:**

    algorithm : py:class:`bob.pad.base.algorithm.Algorithm` or derived
      The algorithm, used for projecting features and writing them to file.

    extractor : py:class:`bob.bio.base.extractor.Extractor` or derived
      The extractor, used for reading the extracted features, which should be projected.

    groups : some of ``('train', 'dev', 'eval')`` or ``None``
      The list of groups, for which the data should be projected.

    indices : (int, int) or None
      If specified, only the features for the given index range ``range(begin, end)`` should be projected.
      This is usually given, when parallel threads are executed.

    force : bool
      If given, files are regenerated, even if they already exist.
    """

    if not algorithm.performs_projection:
        logger.warn(
            "The project function should not have been called, since the algorithm does not perform projection.")
        return

    fs = FileSelector.instance()  # the file selector object

    # load the projector
    algorithm.load_projector(fs.projector_file)

    feature_files = fs.feature_list(groups=groups)
    projected_files = fs.projected_list(groups=groups)

    # select a subset of indices to iterate
    if indices is not None:
        index_range = range(indices[0], indices[1])
        logger.info("- Projection: splitting of index range %s", str(indices))
    else:
        index_range = range(len(feature_files))
    logger.info("- Projection: projecting %d features from directory '%s' to directory '%s'", len(index_range),
                fs.directories['extracted'], fs.directories['projected'])

    # extract the features
    for i in index_range:
        feature_file = str(feature_files[i])
        projected_file = str(projected_files[i])

        if not os.path.exists(feature_file):
            if allow_missing_files:
                logger.debug("... Cannot find extracted feature file %s; skipping", feature_file)
                continue
            else:
                raise RuntimeError("Cannot find extracted feature file %s" % feature_file)

        if not utils.check_file(projected_file, force, 1000):
            logger.debug("... Projecting features for file '%s'", feature_file)

            # load feature
            feature = extractor.read_feature(feature_file)
            # project feature
            projected = algorithm.project(feature)

            if projected is None:
                if allow_missing_files:
                    logger.debug("... Projection for extracted file %s failed; skipping", feature_file)
                    continue
                else:
                    raise RuntimeError("Projection of file '%s' was not successful" % feature_file)
            # write it
            bob.io.base.create_directories_safe(os.path.dirname(projected_file))
            algorithm.write_feature(projected, projected_file)

        else:
            logger.debug("... Skipping feature file '%s' since projected file '%s' exists", feature_file, projected_file)

