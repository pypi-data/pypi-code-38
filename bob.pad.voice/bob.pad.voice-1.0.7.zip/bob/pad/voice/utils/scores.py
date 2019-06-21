#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Mon 8 Oct 14:09:22 CEST 2015
#

from __future__ import print_function

import numpy
import bob.bio.base
import os.path

import bob.core
logger = bob.core.log.setup("bob.pad.voice")


def load_noattacks_scores(filename):
  # split in positives and negatives
  female_neg = []
  female_pos = []
  male_neg    = []
  male_pos    = []

  # read four column list line by line
  for (client_id, probe_id, filename, score) in bob.bio.base.score.load.four_column(filename):
    if client_id == probe_id:
      if 'female' in filename:
        female_pos.append(score)
      else:
        male_pos.append(score)
    else:
      if 'female' in filename:
        female_neg.append(score)
      else:
        male_neg.append(score)
  results = {}
  results['female'] = (numpy.array(female_neg, numpy.float64), numpy.array(female_pos, numpy.float64))
  results['male']    = (numpy.array(male_neg, numpy.float64), numpy.array(male_pos, numpy.float64))
  return results


#attacks = ['replay_phone1', 'replay_phone2', 'replay_laptop', 'replay_laptop_HQ', 'speech_synthesis_logical_access', 'speech_synthesis_physical_access', 'speech_synthesis_physical_access_HQ', 'voice_conversion_logical_access', 'voice_conversion_physical_access', 'voice_conversion_physical_access_HQ']

# load and split scores in positives and negatives
def load_attack_scores(scores_filename, support="all", adevice="all", recdevice="all"):
  positives = []
  negatives = []

  # read four column list line by line
  for (client_id, probe_id, filename, score) in bob.bio.base.score.load.four_column(scores_filename):
      if client_id == probe_id:
          # if (support in filename or support == "all") and \
          #       (adevice in filename or adevice == "all") and \
          #       (recdevice in filename or recdevice == "all"):
          positives.append(score)
      else:
          correct_attack = False
          if len(probe_id.split('/')) > 1: probe_id = probe_id.split('/')[1]
          if any(s == probe_id for s in support): correct_attack = True
          if (correct_attack or not support or support == "all") and \
                  (adevice in filename or adevice == "all") and \
                  (recdevice in filename or recdevice == "all"):
              negatives.append(score)

  return numpy.array(negatives, numpy.float64), numpy.array(positives, numpy.float64)

# load file with scores into two dictionaries: negative and positive
def scores_to_dict(filename, support="all", adevice="all", recdevice="all"):
  """

  :rtype : dict
  """
  positives = {}
  negatives = {}

  # read four column list line by line
  for (client_id, probe_id, filename, score) in bob.bio.base.score.load.four_column(filename):
      if client_id == probe_id:
          if (support in filename or support == "all") and \
                (adevice in filename or adevice == "all") and \
                (recdevice in filename or recdevice == "all"):
              positives["%03d"%int(client_id) + "%03d"%int(probe_id) + filename] = score
      else:
          # print ("%03d"%int(client_id) + "%03d"%int(probe_id) + filename)
          negatives["%03d"%int(client_id) + "%03d"%int(probe_id) + filename] = score

  return negatives, positives

def accumulate_scores(pad_scores_dir, avs_scores_dir, support="all", attackdevice="all", device="all"):

    all_scores = {}
    systems = ['pad', 'avs']
    groups = ['train', 'dev', 'eval']
    score_types = ['real', 'attack', 'zimp']

    # read score files from PAD and AVS directory
    # make sure all 6 files are present: real and attacks for train, dev, and eval sets
    for system in systems:
        if system == 'pad':
            curdir = pad_scores_dir
        else:
            curdir = avs_scores_dir
        if not os.path.exists(curdir):
            logger.error(" - Score fusion: directory %s with scores does not exist", curdir)
            return None
        all_scores[system] = {}
        # read scores from the current directory with scores
        for group in groups:
            all_scores[system][group] = {}
            # loop through real and attacks only, since zero-imposters are inside real scores
            for type in score_types[0:2]:
                path_scores = os.path.join(curdir, 'scores-' + group + '-' + type)
                if not os.path.exists(path_scores):
                    logger.error(" - Score fusion: score file %s does not exist", path_scores)
                    return None
                if type == 'attack':
                    all_scores[system][group][type] = \
                    scores_to_dict(path_scores, support, attackdevice, device)[
                        1]  # oly positive values
                if type == 'real':
                    # zero imposters - negative set, real - positive set
                    [all_scores[system][group][score_types[2]],
                     all_scores[system][group][type]] = scores_to_dict(path_scores)
                    logger.info("%s %s %s: %d",
                                system, group, score_types[2], len(all_scores[system][group][score_types[2]]))
                logger.info("%s %s %s: %d", system, group, type, len(all_scores[system][group][type]))
    return all_scores
