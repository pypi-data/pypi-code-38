def key( *args ):
    """
    join the arguments in the format of donkey

    Arguments
    ---------
    args: list of string

    Examples
    --------
    >>>key( 'a', 'b', 'c' )
    'a__b__c'
    """
    return '__'.join( args )


def partion( key ):
    """
    split the key have the format of donkey

    Arguments
    ---------
    key: string

    Examples
    --------
    >>>partion( 'a__b__c' )
    [ 'a', 'b', 'c' ]
    """
    return key.split( '__' )
    parts = key.rsplit( '__', 1 )
    return tuple( parts ) if len( parts ) > 1 else ( parts[0], None )


def init( key ):
    """
    get the first key

    Arguments
    ---------
    key: string

    Examples
    --------
    >>>init( 'a__b__c' )
    a
    """
    return partion( key )[0]


def last( key ):
    """
    get the last part of the key

    Arguments
    ---------
    key: string

    Examples
    --------
    >>>last( 'a__b__c' )
    c
    """
    return partion( key )[-1]


def get( key, d ):
    """
    get the value from a dict

    Arguments
    ---------
    key: string
    d: dict

    Returns
    -------
    object
        the value of in the key

    Raises
    ------
    KeyError: if cannot find the key

    Examples
    --------
    >>>d = { 'c': { 'd': { 'f': 20 } }, }
    >>>get( 'c__d__f', d )
    20
    """
    keys = partion( key )
    value = d
    for k in keys:
        value = value[ k ]
    return value


def setter( key, d, value ):
    """
    set the value in the dict in the key
    if no exitst the path is going to maked

    Arguments
    ---------
    key: string
    d: dict
    value: object

    Examples
    >>>d = { }
    >>>set( 'c__d__f', d, 20 )
    >>>d
    { 'c': { 'd': { 'f': 20 } } }
    """
    keys = partion( key )
    v = d
    for k in keys[:-1]:
        try:
            v = v[ k ]
        except KeyError:
            v[ k ] = {}
            v = v[ k ]
    v[ keys[-1] ] = value


def inflate( d ):
    """
    inflate a dict

    Arguments
    ---------
    d: dict

    Returns
    -------
    dict

    Examples
    --------
    >>>inflate( { 'a': 10, 'b__c': 30 } )
    { 'a': 10, 'b': { 'c': 30 } }
    """
    result = {}
    for k, value in d.items():
        try:
            get( k, result )
            raise ValueError(
                "Conflict with the donkey '{}' ".format( k ) )
        except KeyError:
            pass
        except TypeError:
            raise ValueError(
                "Conflict with the donkey '{}' ".format( k ) )
        setter( k, result, value )
    return result


def compress( d ):
    """
    compress a dict using donkey format

    Arguments
    ---------
    d: dict

    Returns
    -------
    dict

    Examples
    --------
    >>>inflate( { 'a': 10, 'b: { 'c': 30 } } )
    { 'a': 10, 'b__c': 30 }
    """
    result = {}
    for k, v in d.items():
        if isinstance( v, dict ):
            r = _compress( k, v )
            result.update( r )
        else:
            result[ k ] = _compress( k, v )
    return result


def _compress( init_key, d ):
    """
    """
    if isinstance( d, dict ):
        result = {}
        for k, v in d.items():
            if init_key != '':
                current_key = key( init_key, k )
            else:
                current_key = k
            result[ current_key ] = _compress( '', v )
        result = compress( result )
        return result
    elif isinstance( d, list ):
        return [ a for a in d ]
    elif isinstance( d, tuple ):
        return tuple( a for a in d )
    return d
