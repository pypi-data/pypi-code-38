"""
Summary.

    Parallel processing module

"""
from multiprocessing.dummy import Pool


def split_list(monolith, n):
    """
    Summary.

        splits a list into equal parts as allowed, given n segments

    Args:
        :monolith (list):  a single list containing multiple elements
        :n (int):  Number of segments in which to split the list
    Returns:
        generator object

    """
    k, m = divmod(len(monolith), n)
    return (monolith[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))


def assemble_args(container, process_ct):
    """
    Summary.

        Assumbles pool args for multiprocessing

    Args:
        :container (list):  list containing multiple elements
        :process_ct (int): number of concurrent processes
    Returns:
        pool_args (list) for use in multiprocessing array

    """
    pool_args = []
    for x in split_list(container, process_ct):
        pool_args.append(x)
    return pool_args


def process(input_list, function_object, count):
    with Pool(processes=count) as pool:
        pool.starmap(function_object, assemble_args(input_list))
