from chibi.command import command


def rpm( *args ):
    return command( 'rpm', *args )


def rpm_import( repository ):
    return rpm( '--import', repository )
