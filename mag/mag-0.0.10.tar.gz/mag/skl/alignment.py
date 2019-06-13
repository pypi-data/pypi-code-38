import numpy as np
from numpy import mean, subtract
from scipy.spatial.distance import euclidean
from .iou import iou_1d

def align_channel_object(
    output_object:list,
    target_objects:list,
    alignment_scoring_fn=iou_1d,
    tie_breaking_fn=euclidean,
    alignment_scoring_optimal=min,
    tie_breaking_optimal=min
) -> int:
    '''Attepts to align a given object to a list of other objects

    Args:
        output_object (list): an object in form [start, stop]

        target_objects (list): a list of objects in form [[start, stop],...]

        alignment_scoring_fn (function): a function which is passed the
            output_object and a target_object and should return a singular
            numeric value. Defaults to iou_1d

        tie_breaking_fn (function): a function which is passed the output_object
            and a target_object and should return a singular numeric value.
            Defaults to euclidean. Only called if there are more than one optimal
            alignment score.

        alignment_scoring_optimal (function): a function which returns the optimal
            alignment score from a list of scores. Defaults to min.

        tie_breaking_optimal (function): a function which returns the optimal
            tie breaking score from a list of scores. Defaults to min.


    Returns:
        alignment_index (int): the index of the object in target_objects which
            is the best alignment for output_object given the alignment_scoring
            and  putatively invoked tie_breaking functions

    '''
    # calculate output object's alignment scores for every target object
    alignment_scores = [
        alignment_scoring_fn(output_object, target_object)
        for target_object in target_objects
    ]

    # find the best score
    best_score = alignment_scoring_optimal(alignment_scores)

    # find occurances of the best
    occurances = np.where(np.array(alignment_scores) == best_score)[0]

    # only one optimal aligment
    if occurances.size == 1:
        alignment_index = occurances[0]

    # tie breaking can drastically improve alignment results
    else:
        # calculate the tie breaking scores only for the best scoring targets
        tie_breaking_scores = [
            tie_breaking_fn(output_object, target_object)
            for i, target_object in enumerate(target_objects)
            if i in occurances
        ]
        # find the new best score
        best_score = tie_breaking_optimal(tie_breaking_scores)

        alignment_index = tie_breaking_scores.index(best_score)
        alignment_index = occurances[alignment_index]

    # return the alignment index
    return alignment_index


def align_channel_objects(
    output_objects, target_objects,
    alignment_scoring_fn=iou_1d,
    tie_breaking_fn=euclidean,
    alignment_scoring_optimal=min,
    tie_breaking_optimal=min
) -> dict:
    '''Attepts to align each object of a list of objects to a list of different objects

    Args:
        output_objects (list): a list of objects in form [[start, stop],...]

        target_objects (list): a list of objects in form [[start, stop],...]

        alignment_scoring_fn (function): a function which is passed the
            output_object and a target_object and should return a singular
            numeric value. Defaults to iou_1d

        tie_breaking_fn (function): a function which is passed the output_object
            and a target_object and should return a singular numeric value.
            Defaults to euclidean. Only called if there are more than one optimal
            alignment score.

        alignment_scoring_optimal (function): a function which returns the optimal
            alignment score from a list of scores. Defaults to min.

        tie_breaking_optimal (function): a function which returns the optimal
            tie breaking score from a list of scores. Defaults to min.


    Returns:
        metrics (dict): the metrics of alignment. Current metrics include:

            perfect_absences, perfect_coverages, false_negatives, false_positives,
            aligned, offsets, ious, average_iou, average_offset

    '''
    metrics = {
        'perfect_absences': 0,
        'false_negatives': 0,
        'false_positives': 0,
        'perfect_coverages': 0,
        'aligned': [],
        'offsets': [],
        'ious': [],
        'average_iou': float('nan'),
        'average_offset': [float('nan'), float('nan')]
    }

    number_of_output_objects = len(output_objects)
    number_of_target_objects = len(target_objects)

    # at least one object in both output and target
    is_alignable       = all([number_of_output_objects, number_of_target_objects])
    # no objects in the output or the target
    is_perfect_absence = (number_of_output_objects == number_of_target_objects == 0)
    # no objects in the output or but objects in the target
    is_false_negative  = (not is_perfect_absence and number_of_output_objects == 0)
    # no objects in the target or but objects in the output
    is_false_positive  = (not is_perfect_absence and number_of_target_objects == 0)

    if is_perfect_absence: metrics['perfect_absences'] += 1
    if is_false_negative:  metrics['false_negatives']  += number_of_target_objects
    if is_false_positive:  metrics['false_positives']  += number_of_output_objects

    if is_alignable:
        for output_object in output_objects:
            aligned_index  = align_channel_object(
                output_object, target_objects,
                alignment_scoring_fn, tie_breaking_fn,
                alignment_scoring_optimal, tie_breaking_optimal
            )

            aligned_object = target_objects[aligned_index]

            metrics['aligned'] += [(output_object, aligned_object)]

            if output_object == aligned_object: metrics['perfect_coverages'] += 1

            offset = subtract(output_object, aligned_object)
            iou = iou_1d(output_object, aligned_object)

            metrics['offsets'].append(offset)
            metrics['ious'].append(iou)

    if len(metrics['offsets']):
        metrics['average_offset'] = [mean(errors) for errors in zip(*metrics['offsets'])]
    if len(metrics['ious']):
        metrics['average_iou'] = mean(metrics['ious'])
    return metrics
