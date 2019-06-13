from mag.np.arr import runs, binarize, nonzero_1d, consecutive
import numpy as np

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
