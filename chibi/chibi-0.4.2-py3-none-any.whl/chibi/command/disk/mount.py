from chibi.command import command


def mount( device, destiny ):
    return command( 'mount', device, destiny )


def umount( mount_dir ):
    return command( 'umount', mount_dir )
