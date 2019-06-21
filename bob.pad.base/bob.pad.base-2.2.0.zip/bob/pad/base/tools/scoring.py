#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Wed 19 Aug 13:43:21 2015
#


import bob.io.base
import bob.bio.base.score.load as bio_load
import bob.measure
import numpy
import os
import sys
import tarfile

import logging

logger = logging.getLogger("bob.pad.base")

from .FileSelector import FileSelector

from bob.bio.base import utils


def _compute_scores(algorithm, extractor, toscore_objects, allow_missing_files):
    """Compute scores for the given list of objects using provided algorithm.
    """
    # the scores to be computed
    scores = []

    # Loops over the toscore sets
    for i, toscore_element in enumerate(toscore_objects):
        # filter missing files
        if allow_missing_files and not os.path.exists(toscore_element):
            # we keep NaN score for such elements
            scores.insert(i, [numpy.nan])
            continue
        # read toscore
        if algorithm.performs_projection:
            toscore = algorithm.read_feature(toscore_element)
        else:
            toscore = extractor.read_feature(toscore_element)
        # compute score
        if isinstance(toscore, list) or isinstance(toscore[0], numpy.ndarray):
            scores.insert(i, algorithm.score_for_multiple_projections(toscore))
        else:
            scores.insert(i, algorithm.score(toscore))
    # Returns the scores
    return scores


def _open_to_read(score_file):
    """Checks for the existence of the normal and the compressed version of the file,
    and calls :py:func:`bob.bio.base.score.load.open_file` for the existing one."""
    if not os.path.exists(score_file):
        score_file += '.tar.bz2'
        if not os.path.exists(score_file):
            raise IOError("The score file '%s' cannot be found. Aborting!" % score_file)
    return bio_load.open_file(score_file)


def _open_to_write(score_file, write_compressed):
    """Opens the given score file for writing. If write_compressed is set to ``True``, a file-like structure is returned."""
    bob.io.base.create_directories_safe(os.path.dirname(score_file))
    if write_compressed:
        if sys.version_info[0] <= 2:
            import StringIO
            f = StringIO.StringIO()
        else:
            import io
            f = io.BytesIO()
        score_file += '.tar.bz2'
    else:
        f = open(score_file, 'w')

    return f


def _write(f, data, write_compressed):
    """Writes the given data to file, after converting it to the required type."""
    if write_compressed:
        if sys.version_info[0] > 2:
            data = str.encode(data)

    f.write(data)


def _close_written(score_file, f, write_compressed):
    """Closes the file f that was opened with :py:func:`_open_to_read`"""
    if write_compressed:
        f.seek(0)
        tarinfo = tarfile.TarInfo(os.path.basename(score_file))
        tarinfo.size = len(f.buf if sys.version_info[0] <= 2 else f.getbuffer())
        tar = tarfile.open(score_file, 'w')
        tar.addfile(tarinfo, f)
        tar.close()
    # close the file
    f.close()


def _save_scores(score_file, scores, toscore_objects, write_compressed=False):
    """Saves the scores of one model into a text file that can be interpreted by :py:func:`bob.measure.load.split_four_column`."""
    assert len(toscore_objects) == len(scores)

    # open file for writing
    f = _open_to_write(score_file, write_compressed)

    # write scores in four-column format as string
    for i, toscore_object in enumerate(toscore_objects):
        id_str = (str(toscore_object.client_id)).zfill(3)
        sample_name = str(toscore_object.make_path())

        # scores[i] is a list, so
        # each sample is allowed to have multiple scores
        for score in scores[i]:
            if not toscore_object.attack_type or toscore_object.attack_type == "None":
                _write(f, "%s %s %s %.12f\n" % (id_str, id_str, sample_name, score), write_compressed)
            else:
                attackname = toscore_object.attack_type
                _write(f, "%s %s %s %.12f\n" % (id_str, attackname, sample_name, score), write_compressed)

    _close_written(score_file, f, write_compressed)


def _scores_all(algorithm, extractor, group, force, allow_missing_files=False, write_compressed=False):
    """Computes scores for all (real, attack) files in a given group using the provided algorithm."""
    # the file selector object
    fs = FileSelector.instance()

    logger.info("- Scoring: computing scores for group '%s'", group)

    # both real and attack objects
    current_toscore_objects = fs.toscore_objects(group)
    type_objects = ['real', 'attack']

    total_scores = []
    one_score_file_exists = False
    for i in range(0, 2):
        current_objects = current_toscore_objects[i]
        obj_type = type_objects[i]
        logger.info("- Scoring: len of current_objects: %d", len(current_objects))
        logger.info("- Scoring: type of current_objects: %s", obj_type)
        # test if the file is already there
        score_file = fs.score_file_for_type(group, obj_type)
        if utils.check_file(score_file, force):
            logger.warn("Score file '%s' already exists.", score_file)
            total_scores = []
            one_score_file_exists = True
        else:
            # get the attack files
            current_files = fs.get_paths(current_objects, 'projected' if algorithm.performs_projection else 'extracted')
            # compute scores for the list of File objects
            cur_scores = _compute_scores(algorithm, extractor, current_files, allow_missing_files)
            total_scores += cur_scores
            # Save scores to text file
            _save_scores(score_file, cur_scores, current_objects, write_compressed)

    if total_scores != [] and not utils.check_file(fs.score_file_combined(group), force):
        # save all scores together in one file
        if one_score_file_exists:
            logger.warn("Since at least one score file already pre-existed, "
                        "we skip combining individual score files together. "
                        "You can do it manually, using 'cat' or similar utilities.")
        else:
            _save_scores(fs.score_file_combined(group), total_scores,
                         current_toscore_objects[0]+current_toscore_objects[1], write_compressed)


def compute_scores(algorithm, extractor, force=False, groups=['dev', 'eval'], allow_missing_files=False, write_compressed=False):
    """Computes the scores for the given groups.

    This function computes all scores for the experiment and writes them to score files.
    By default, scores are computed for both groups ``'dev'`` and ``'eval'``.

    **Parameters:**

    algorithm : py:class:`bob.bio.base.algorithm.Algorithm` or derived
      The algorithm, used for enrolling model and writing them to file.

    extractor : py:class:`bob.bio.base.extractor.Extractor` or derived

    force : bool
      If given, files are regenerated, even if they already exist.

    groups : some of ``('dev', 'eval')``
      The list of groups, for which scores should be computed.

    write_compressed : bool
      If enabled, score files are compressed as ``.tar.bz2`` files.
    """
    # the file selector object
    fs = FileSelector.instance()

    # load the projector if needed
    if algorithm.requires_projector_training:
        algorithm.load_projector(fs.projector_file)

    for group in groups:
        _scores_all(algorithm, extractor, group, force, allow_missing_files, write_compressed)
