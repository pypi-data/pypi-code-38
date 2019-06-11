from dateutil.parser import parse


def is_date( string ):
    """
    check is a string is a date

    Arguments
    ---------
    string: str
        string to evaluate if is a date

    Returns
    -------
    data, datetime
        if the date is a date or datetime format
    bool
        if the string is not a date return False
    """
    try:
        return parse( string )
    except ValueError:
        return False


def is_iter( obj ):
    """
    evaluate if the object can be iterate

    Arguments
    ---------
    obj: object

    Returns
    -------
    bool
    """
    try:
        iter( obj )
        return True
    except TypeError as e:
        return False


def is_like_list( obj ):
    """
    evaluate if the object is like a list

    Arguments
    ---------
    obj: object

    Returns
    -------
    bool
    """
    return isinstance( obj, ( list, tuple, set ) )
