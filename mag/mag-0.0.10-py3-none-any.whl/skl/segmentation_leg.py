import numpy as np
from mag.np.arr import runs, binarize, nonzero_1d
def detect_binary_objects(channel:list):
    # ensure np.ndarray
    channel = np.array(channel)
    # indicies of signal
    signal_indicies = nonzero_1d(channel)
    # if no signal
    if signal_indicies.size == 0:
        # return list devoid of object
        return []
    # else, group indicies by consecutive integers
    consec_indicies = consecutive(signal_indicies, stepsize=1)
    # return the domain of each group of consecutive indicies (object specifier)
    return runs(signal_indicies)



def detect_sequence_binary_objects(channel_matrix, cutoff:float=0.5):
    channel_matrix = np.array(channel_matrix)
    return [detect_binary_objects(channel) for channel in binarize(channel_matrix, cutoff)]



def binary_boundaries_1d(labels, cutoff:float=0.5):
    ''' Gives the boundaries of the labels
    Args:
        labels (list): a list of list of values, where the value of each sublist
            is the probability of an item at that position belongs to the class
            corresponding to the sublist's index.
        cutoff (float): a value bounded by [0, 1] specifying the minimum
            probability required to consider a position belong to the label of
            a given class.

    Returns:
        boundaries (list): a list of list of boundaries where each sublist
            contains the boundaries belonging the class assocatied with the
            sublists index.

    '''
#   return [consecutive_integers(channel) for channel in binarize(labels, cutoff)]
    return [runs(nonzero_1d(channel)) for channel in binarize(labels, cutoff)]



def mask_accuracy(predictions, labels, cutoff:float=0.5):
    '''Calculates the one-to-one accuracy of the binary mask with the specified
    cuttoff of the predictions to the labels

    Args:
        predictions (np.ndarray): an arbitrary array, with the same shape as
            labels containing the predicted probabilities of each position
            belonging the corresponding label.

        labels (np.ndarray): an arbitrary array of binary values

        cutoff (float): a value bounded by [0, 1] specifying the minimum
            probability required to consider a position belong to the label of
            a given class.

    Returns:
        accuracy (float): how many binarized predictions corresponding directly
            to labels
    '''
    b_mask = binarize(predictions, cutoff)
    return  (b_mask == labels).sum() / len(labels.flatten())

# labels
# box 1: x----y
# box 2: x++++y
# 0  1  2  3  4  5  6  7  8  9  10 11 12 13 14 15 16 17 18 19 20
#             x--------y        x+++++++++++++++++++++++++++++y     TRUTH
#             a-----------b                                         PRED 1, BOX 1
#                   a+++++++++++++++++b                             PRED 2, BOX 2
#                a++++++++++++++++++++++++++++++++b                 PRED 3, BOX 2
from scipy.spatial.distance import euclidean
from numpy import mean, subtract
def iou_1d(predicted_boundary, target_boundary):
    '''Calculates the intersection over union (IOU) based on a span.

    Notes:
        boundaries are provided in the the form of [start, stop].
        boundaries where start = stop are accepted
        boundaries are assumed to be only in range [0, int < inf)

    Args:
        predicted_boundary (list): the [start, stop] of the predicted boundary
        target_boundary (list): the ground truth [start, stop] for which to compare

    Returns:
        iou (float): the IOU bounded in [0, 1]
    '''

    p_lower, p_upper = predicted_boundary
    t_lower, t_upper = target_boundary

    # boundaries are in form [start, stop] and 0 <= start <= stop
    assert 0<= p_lower <= p_upper
    assert 0<= t_lower <= t_upper

    # no overlap, pred is too far left or pred is too far right
    if p_upper < t_lower or p_lower > t_upper:
        return 0

    if predicted_boundary == target_boundary:
        return 1

    intersection_lower_bound = max(p_lower, t_lower)
    intersection_upper_bound = min(p_upper, t_upper)

    intersection = intersection_upper_bound - intersection_lower_bound

    max_upper = max(t_upper, p_upper)
    min_lower = min(t_lower, p_lower)

    union = max_upper - min_lower

    union = union if union != 0 else 1
    return min(intersection / union, 1)


def safe_alignment_score(predicted_boundary, target_boundary, alignment_scoring_fn=iou_1d, default=0):
    if predicted_boundary == [] or target_boundary == []:
        return default
    return alignment_scoring_fn(predicted_boundary, target_boundary)


def no_prediction_distance(predicted_boundary, target_boundary, distance_fn=subtract):
    return target_boundary

def no_target_distance(predicted_boundary, target_boundary,distance_fn=subtract):
    return [0, 0]

def safe_distance(predicted_boundary, target_boundary, distance_fn=subtract, no_prediction_penalty=no_prediction_distance, no_target_penalty=no_target_distance):
    if predicted_boundary == []:
        return no_prediction_penalty(predicted_boundary, target_boundary, distance_fn)
    if target_boundary ==  []:
        return no_target_penalty(predicted_boundary, target_boundary, distance_fn)

    distance = distance_fn(predicted_boundary, target_boundary)
    return distance if distance is not [] else [0, 0]


def align_1d(
    predicted_boundary,
    target_boundaries,
    alignment_scoring_fn=iou_1d,
    take=max
):
    '''Aligns predicted_bondary to the closest target_boundary based on the
    alignment_scoring_fn

    Args:
        predicted_boundary (list): the predicted boundary in form of [start, stop]

        target_boundaries (list): a list of all valid target boundaries each having
            form [start, stop]

        alignment_scoring_fn (function): a function taking two arguments each of
            which is a list of two elements, the first assumed to be the predicted
            boundary and the latter the target boundary. Should return a single number.

        take (function): should either be min or max. Selects either the highest or
            lower score according to the alignment_scoring_fn. Can be custom if
            returns an integer (index) in range [0, len(target_boundaries) - 1].

    Returns:
        aligned_boundary (list): the aligned boundary in form [start, stop]
    '''
    scores = [
        safe_alignment_score(predicted_boundary, target_boundary)
        for target_boundary in target_boundaries
    ]

    # boundary did not align to any boxes. Use fallback to break tie.
    if not any(scores):
        scores = [
          safe_alignment_score(predicted_boundary, target_boundary, lambda p, t: 1 / euclidean(p, t))
          for target_boundary in target_boundaries
        ]

    aligned_index = scores.index(take(scores))
    aligned = target_boundaries[aligned_index]
    return aligned


def aligned_offset_1d(
    predicted_boundaries:list,
    target_boundaries:list,
    alignment_scoring_fn:function=iou_1d,
    take:function=max,
    distance_fn:function=subtract,
    aggregate_fn:function=mean
):
    '''Returns the aggregated distance of predicted boundings boxes to their aligned bounding box based on alignment_scoring_fn and distance_fn
    Notes:
        The function



    Args:
        predicted_boundaries (list): a list of all valid target boundaries each
            having form [start, stop]

        target_boundaries (list): a list of all valid target boundaries each having
            form [start, stop]

        alignment_scoring_fn (function): a function taking two arguments each of
            which is a list of two elements, the first assumed to be the predicted
            boundary and the latter the target boundary. Should return a single number.

        take (function): should either be min or max. Selects either the highest or
            lower score according to the alignment_scoring_fn

        distance_fn (function): a function taking two lists and should return a
            single value.

        aggregate_fn (function): a function taking a list of numbers (distances
            calculated by distance_fn) and returns a single value (the aggregated
            distance)

    Returns:
        aggregated_distnace (float): return the aggregated distance of the
            aligned predicted_boundaries

        aggregated_fn([distance_fn(pair) for pair in paired_boundaries(predicted_boundaries, target_boundaries)])
    '''
    pairs = []
    for predicted_boundary in predicted_boundaries:
        paired_target_boundary = align_1d(
            predicted_boundary=predicted_boundary,
            target_boundaries=target_boundaries,
            alignment_scoring_fn=alignment_scoring_fn, take=take
        )

        pair = (predicted_boundary, paired_target_boundary)

        pairs.append(pair)

    distances = [safe_distance(*pair, distance_fn) for pair in pairs]
    aggregated = [aggregate_fn(error) for error in zip(*distances)]
    return aggregated


def offset_per_class_1d(
    predicted_boundaries:list,
    target_boundaries:list,
    alignment_scoring_fn:function=iou_1d,
    take:function=max,
    distance_fn:function=subtract,
    aggregate_fn:function=mean
):
    '''Returns the aggregated distance of predicted boundings boxes to their aligned bounding box based on alignment_scoring_fn and distance_fn

    Args:
        predicted_boundaries (list): a list of all valid target boundaries each
            having form [start, stop] for each class e.g.
                [
                    [
                        [start, stop], # boundary 1
                        [start, stop], # boundary 2
                    ], # class 1
                ]

        target_boundaries (list): a list of all valid target boundaries each having
            form [start, stop]  for each class

        alignment_scoring_fn (function): a function taking two arguments each of
            which is a list of two elements, the first assumed to be the predicted
            boundary and the latter the target boundary. Should return a single number.

        take (function): should either be min or max. Selects either the highest or
            lower score according to the alignment_scoring_fn

        distance_fn (function): a function taking two lists and should return a
            single value.

        aggregate_fn (function): a function taking a list of numbers (distances
            calculated by distance_fn) and returns a single value (the aggregated
            distance)

    Returns:
        aggregated_distnace (float): return the aggregated distance of the
            aligned predicted_boundaries

        aggregated_fn([distance_fn(pair) for pair in paired_boundaries(predicted_boundaries, target_boundaries)])
    '''
    offsets = []
    for class_index in range(len(target_boundaries)):
        class_offset = aligned_offset_1d(
            predicted_boundaries=predicted_boundaries[class_index],
            target_boundaries=target_boundaries[class_index],
            alignment_scoring_fn=alignment_scoring_fn,
            take=take, distance_fn=distance_fn, aggregate_fn=aggregate_fn
        )
        offsets.append(class_offset)

    return offsets



def batched_offset_1d(
    batched_outputs:list,
    batched_targets:list,
    cutoff:float=0.5,
    alignment_scoring_fn=iou_1d,
    take=max,
    distance_fn=subtract,
    aggregate_fn=mean
):
    '''

    '''
    batched_offsets = []
    for index in range(len(batched_targets)):

        outputs = batched_outputs[index]
        targets = batched_targets[index]

        output_boundaries = binary_boundaries_1d(output, cutoff)
        target_boundaries = binary_boundaries_1d(target, cutoff)

        offsets = offset_per_class_1d(
            predicted_boundaries=output_boundaries,
            target_boundaries=target_boundaries,
            alignment_scoring_fn=alignment_scoring_fn,
            take=take, distance_fn=distance_fn, aggregate_fn=aggregate_fn
        )
        batched_offsets.append(offsets)

    return batched_offsets

def segmentation_metrics_1d(
    batched_outputs:list,
    batched_targets:list,
    cutoff:float=0.5,
    alignment_scoring_fn:function=iou_1d,
    take:function=max,
    distance_fn:function=subtract,
    aggregate_fn:function=mean
) -> dict:
    '''

    '''
    metrics = {};

    batched_outputs = batched_offset_1d(
        batched_outputs=batched_outputs, batched_targets=batched_targets,
        cutoff=cutoff, alignment_scoring_fn=alignment_scoring_fn,
        take=take, distance_fn=distance_fn, aggregate_fn=aggregate_fn
    )



    metrics['masked_accuracy'] = mask_accuracy(batched_outputs, batched_targets, cutoff)
    metrics['aggregated_offsets'] = np.sum(batched_offsets, axis=0)
    metrics['individual_offsets'] = batched_offsets


    return metrics
