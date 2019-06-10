from chibi.command import command


def ponysay( text, capture=False):
    """
    comando de unix llamado ponysay

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
    return command( 'ponysay', text, stdout=stdout )
