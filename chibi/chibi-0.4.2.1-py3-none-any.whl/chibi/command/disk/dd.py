from chibi.command import command


def dd( i_file, o_file, bs='1M' ):
    return command(
        'dd', 'if={}'.format( i_file ), 'of={}'.format( o_file ),
        'bs={}'.format( bs ) )


def dd_zero_to( o_file, bs='1M' ):
    dd( '/dev/zero', o_file=o_file, bs=bs )
