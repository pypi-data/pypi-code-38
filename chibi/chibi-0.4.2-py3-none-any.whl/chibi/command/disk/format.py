from chibi.command import command


def vfat( device ):
    return command( 'mkfs.vfat', device )


def ext4( device ):
    return command( 'mkfs.ext4', device )
