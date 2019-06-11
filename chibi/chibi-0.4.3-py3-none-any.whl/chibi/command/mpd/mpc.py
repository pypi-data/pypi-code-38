from chibi.command import command


def mpc( *args ):
    return command( 'mpc', *args )


def pause():
    return mpc( 'pause' )


def stop():
    return mpc( 'stop' )


def play():
    return mpc( 'play' )


def play_toggle():
    return mpc( 'toggle' )


def next():
    return mpc( 'next' )


def prev():
    return mpc( 'prev' )
