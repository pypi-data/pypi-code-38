import numpy as np
from mag.np.arr import runs, binarize, nonzero_1d, consecutive
def channel_objects_1d(channel:list, cutoff=0.5):
    #
    channel = binarize(channel, cutoff)
    signal_indicies = nonzero_1d(channel)
    if signal_indicies.size == 0:
        return []
    consec_indicies = consecutive(signal_indicies, stepsize=1)
    return runs(signal_indicies)

def mask_accuracy(outputs, targets, cutoff:float=0.5):
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
    b_mask = binarize(outputs, cutoff)
    return  (b_mask == targets).sum() / len(targets.flatten())

'''-----------------------------------------------------------------------------

EXAMPLE'S CHANNEL LEVEL FUNCTIONS

-----------------------------------------------------------------------------'''






def relative_offset_1d():
    # align

    # score

    # distance

    # aggregate

    # move these two to seperate function
    return [r_start, r_stop]

def false_positive_1d(output_objects, target_objects) -> int:
    # output_object(s) but no target_object
    fp = len(target_objects) == 0 and len(output_objects) > 0
    return len(output_objects) if fp else 0

def false_negative_1d(output_objects, target_objects) -> int:
    # target_object(s) but no output_object
    fn = len(output_objects) == 0 and len(target_objects) > 0
    return len(target_objects) if fn else 0


def channel_metrics_1d(output_channel, target_channel, cutoff:float=0.5):
    assert len(output_channel.shape) == 1, 'output_channel does not have a shape of 1'
    assert len(target_channel.shape) == 1, 'target_channel does not have a shape of 1'
    assert output_channel.shape == target_channel.shape, 'output_channel and target_channel do not have same shape'
    metrics = {}

    # convert to binary (which also ensures numpy ndarray)
    output_channel = binarize(output_channel, cutoff)
    target_channel = binarize(target_channel, cutoff)

    # detect objects
    output_objects = objects_1d(output_channel, cutoff)
    target_objects = objects_1d(target_channel, cutoff)

    # is false positive?
    fp = false_positive_1d(output_objects, target_objects)

    # is false negative?
    fn = false_negative_1d(output_objects, target_objects)


    # has relative offset?
    ro = None if (fp or fn) else relative_offset_1d() # <---- not this function, first align then score


    # store calculated values
    metrics['output_objects'] = output_objects
    metrics['target_objects'] = target_objects
    metrics['number_of_output_objects'] = len(output_objects)
    metrics['number_of_target_objects'] = len(target_objects)
    metrics['number_of_false_positives'] = fp
    metrics['number_of_false_negatives'] = fn
    pass

'''-----------------------------------------------------------------------------

EXAMPLE LEVEL FUNCTIONS

-----------------------------------------------------------------------------'''
def objects_1d(channel_matrix:list, cutoff=0.5):
    return [channel_objects_1d(channel, cutoff) for channel in channel_matrix]
    
def example_metrics_1d(output_channel_matrix, target_channel_matrix, cutoff:float=0.5):
    # convert to binary (which also ensures numpy ndarray)
    output_channel_matrix = binarize(output_channel_matrix, cutoff)
    target_channel_matrix = binarize(target_channel_matrix, cutoff)



'''-----------------------------------------------------------------------------

BATCH LEVEL FUNCTIONS

-----------------------------------------------------------------------------'''


def segmentation_metrics_1d(batched_output_channel_matrices, batched_target_channel_matrices, cutoff:float=0.5):
    metrics = {}


    metrics['binary_accuracy'] # one-to-one coverage of binary outputs to targets.
    metrics['relative_offset'] # relative [start, stop] per channel
    metrics['discovery_error'] # number of prediction with no target per channel
    metrics['recovery_error']  # number of targets with no prediction per channel
    metrics['segmentation_fault'] # number of prediction objects / number of total objects per channel
