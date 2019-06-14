def diff(a, b):
    """
    Returns the relative complement (A\B)
    (i.e. everything in A that is NOT in B)
    """
    return [item for item in a if item not in b]
