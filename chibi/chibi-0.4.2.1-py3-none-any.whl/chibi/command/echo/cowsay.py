from chibi.command import command


def cowsay( text, capture=False ):
    """
    comando de unix llamado cowsay

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
    return command( 'cowsay', text, stdout=stdout )
