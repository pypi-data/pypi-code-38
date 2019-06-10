from chibi.command import command


def echo( text, capture=False ):
    """
    estandar echo de unix

    Parameters
    ==========
    text: string
    capture: bool
        define si se quiere que se capture la salida de echo

    Returns
    =======
    tuple
        regresa lo mismo que :py:func:`chibi.command.command`
    """
    if capture:
        stdout = 'pipe'
    else:
        stdout = None
    return command( 'echo', text, stdout=stdout )
