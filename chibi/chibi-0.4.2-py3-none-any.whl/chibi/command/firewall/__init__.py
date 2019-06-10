from chibi.command import command


def cmd( *args ):
    return command( 'firewall-cmd', *args )


def add_port( ports, kind='tcp', permanent=True ):
    """
    agrega un puerto usando firewall-cmd

    Parameters
    ==========
    ports: str
        formato de puertos puede ser el numero o un rango
        25672, 5671-5672
    kind: str
        tipo del puerto tcp o udp
    permanent: bool
    """
    if not permanent:
        raise NotImplementedError
    else:
        permanent = '--permanent'
    return cmd( permanent, "--add-port={}/{}".format( ports, kind ) )


def reload():
    return cmd( '--reload' )
