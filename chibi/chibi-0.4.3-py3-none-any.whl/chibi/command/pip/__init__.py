import pip


def install( *packages, upgrade=False ):
    """
    instala los paquetes de python

    Arguments
    =========
    packages: tuple of strings
        lista de paquetes que se quieren instalar
    """
    if upgrade:
        return pip.main( [ 'install', '--upgrade', *packages] )
    else:
        return pip.main( [ 'install', *packages] )


def upgrade( *packages ):
    """
    actualiza los paquetes de python

    Arguments
    =========
    packages: tuple of strings
        lista de paquetes que se quieren actualizar
    """
    return pip.main( [ 'install', '--upgrade', *packages] )


def uninstall( *packages ):
    """
    elimina los paquetes de python

    Arguments
    =========
    packages: tuple of strings
        lista de paquetes que se quieren eliminar
    """
    return pip.main( [ 'uninstall', '--yes', *packages] )
