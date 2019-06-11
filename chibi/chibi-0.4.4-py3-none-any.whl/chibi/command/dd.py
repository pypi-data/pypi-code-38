from chibi.command import command


def dd( in_f, out_f, bs='1M', *args ):
    return command(
        'dd', 'if={}'.format( in_f ), 'of={}'.format( out_f ),
        'bs={}'.format( bs ), 'status=progress', *args )
