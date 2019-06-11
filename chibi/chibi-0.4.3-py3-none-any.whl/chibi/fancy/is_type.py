def is_iter( obj ):
    """
    evalua si el objeto se puede iterar

    Arguments
    ---------
    obj: any type

    Returns
    -------
    bool
        True if the object is iterable
    """
    try:
        iter( obj )
        return True
    except TypeError:
        return False


def is_number( obj ):
    """
    evalua si es objecto es un numero

    Arguments
    ---------
    obj: any type

    Returns
    -------
    bool
        True if the object is a number
    """
    return isinstance( obj, ( int, float ) )
