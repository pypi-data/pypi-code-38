import array

import numpy as np
from Orange.widgets.utils.annotated_data import create_annotated_table, create_groups_table


def pack_selection(selection_group):
    if selection_group is None:
        return None
    nonzero_indices = np.flatnonzero(selection_group)
    if len(nonzero_indices) == 0:
        return None
    if len(nonzero_indices) < 1000:
        return [(a, b) for a, b in zip(nonzero_indices, selection_group[nonzero_indices])]
    else:
        # much faster than array.array("B", selection_group)
        a = array.array("B")
        a.frombytes(selection_group.tobytes())
        return a


def unpack_selection(saved_selection):
    """ Return an numpy array of np.uint8 representing the selection.
    The array can be smaller than the size of data."""
    if saved_selection is None or len(saved_selection) == 0:
        return np.array([], dtype=np.uint8)
    if isinstance(saved_selection, array.array):
        return np.array(saved_selection, dtype=np.uint8)
    else:  # a list of tuples
        # the size that is needed for this number of elements
        a = np.array(saved_selection)
        maxi = np.max(a[:, 0])
        r = np.zeros(maxi + 1, dtype=np.uint8)
        r[a[:, 0]] = a[:, 1]
        return r


def selections_to_length(selection_group, length):
    """
    Make selection size equal to length (add zeros or remove elements)
    """
    add_zeros = length - len(selection_group)
    if add_zeros > 0:
        return np.append(selection_group, np.zeros(add_zeros, dtype=np.uint8))
    else:
        return selection_group[:length].copy()


def groups_or_annotated_table(data, selection):
    """
    Use either Orange's create_annotated_table (for at most 1 selected class
    or create_groups_table (for more selected classes)
    :param data: Orange data table
    :param selection: classes for selected indices (0 for unselected)
    :return: Orange data table with an added column
    """
    if len(selection) and np.max(selection) > 1:
        return create_groups_table(data, selection)
    else:
        return create_annotated_table(data, np.flatnonzero(selection))
