from chibi.command import command


def tar( *args ):
    return command( 'tar', *args )


def bsdtar( *args ):
    return command( 'bsdtar', *args )
