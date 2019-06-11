fix_values_of_bool = {
    'true': True,
    'false': False,
    '0': False,
    'y': True,
    'n': False,
}


def link_header( header, link_delimiter=',', param_delimiter=';' ):
    """
    Parsea en dicionario la respusta de las cabezera ``link``

    Parameters
    ----------
    header: string
        contenido de la cabezera ``link``
    link_delimiter: Optional[str]
        caracter que separa los enlaces
    param_delimiter: Optional[str]
        caracter que separa el parametro ``rel`` del link

    Returns
    -------
    dict

    Note
    ----
    enlace a la especificacion del header
    `link header <https://tools.ietf.org/html/rfc5988>`_
    """
    result = {}
    links = header.split( link_delimiter )
    for link in links:
        segments = link.split( param_delimiter )
        if len( segments ) < 2:
            continue
        link_part = segments[0].strip()
        rel_part = segments[1].strip().split( '=' )[1][1:-1]
        if not link_part.startswith( '<' ) and not link_part.endswith( '>' ):
            continue
        link_part = link_part[1:-1]
        result[rel_part] = link_part
    return result


def to_bool( value ):
    """
    tranforma el valor en booleana usando una lista fija

    Arguments
    ---------
    value: any

    Returns
    -------
    bool

    Examples
    >>>to_bool( '0' )
    False
    >>>to_bool( 'false' )
    False
    >>>to_bool( '1' )
    True
    >>>to_bool( 'true' )
    True
    >>>to_bool( object() )
    True
    """
    if isinstance( value, str ):
        return fix_values_of_bool.get( value.lower(), bool( value ) )
    return fix_values_of_bool.get( value, bool( value ) )
