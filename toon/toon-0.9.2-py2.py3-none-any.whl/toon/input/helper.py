from numbers import Number
import numpy as np


def check_and_fix_dims(input):
    """
    Helper function to ensure data dimensions are consistent and unambiguous.
    Args:
        input: Scalar, list, or list of lists.
    Returns:
        List of lists.
    """
    # handle special-case, single scalar
    if isinstance(input, Number):
        input = [[input]]
    elif isinstance(input, (list, tuple, np.ndarray)):
        # special-case num 2, where we have a single scalar in a list
        if len(input) == 1 and isinstance(input[0], Number):
            input = [input]
        elif len(input) != 1 and any([isinstance(x, Number) for x in input]):
            raise ValueError('Ambiguous dimensions. There should be one list per expected piece of data' + \
                             ' from the input device.')
        # coerce array-like things to lists
        input = [list(x) for x in input]
        # now we're relatively comfortable we have a list of lists
    else:
        raise ValueError('Something is wrong with the input.')
    return input


def shared_to_numpy(mp_arr, dims, dtype):
    """Convert a :class:`multiprocessing.Array` to a numpy array.
    Helper function to allow use of a :class:`multiprocessing.Array` as a numpy array.
    Derived from the answer at:
    <https://stackoverflow.com/questions/7894791/use-numpy-array-in-shared-memory-for-multiprocessing>
    """
    return np.frombuffer(mp_arr.get_obj(), dtype=dtype).reshape(dims)