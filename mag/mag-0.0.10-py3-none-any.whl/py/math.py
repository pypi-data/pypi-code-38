def domain(array:list) -> list:
    '''Returns the min and max of the array

    Args:
        array (list): a list of at least one element

    Returns:
        domain (list): [min, max]
    '''
    return [min(array), max(array)]
