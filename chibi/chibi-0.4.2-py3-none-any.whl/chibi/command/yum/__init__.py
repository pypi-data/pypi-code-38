from chibi.command import command


def yum( option, *args ):
    """
    invoca el comando de yum, ya sabes para instalar cosas en centos y otros

    Parameters
    ==========
    option: string
        opcion del comando, como install o update

    Returns
    =======
    tuple
        regresa lo mismo que :py:func:`chibi.command.command`
    """
    return command( 'yum', option, '-y', *args )


def update():
    """
    invoca el comando de yum para actualizar paquetes

    Returns
    =======
    tuple
        regresa lo mismo que :py:func:`chibi.command.command`
    """
    return yum( 'update' )


def install( *pkgs ):
    """
    invoca el comando de yum para instalar paquetes

    Parameters
    ==========
    pkgs: tuple of strings
        lista de los paquetes que se quieren installar

    Returns
    =======
    tuple
        regresa lo mismo que :py:func:`chibi.command.command`
    """
    return yum( 'install', *pkgs )


def local_install( *pkgs ):
    """
    invoca el comando de yum para instalar paquetes locales

    Parameters
    ==========
    pkgs: tuple of strings
        lista de los paquetes que se quieren installar

    Returns
    =======
    tuple
        regresa lo mismo que :py:func:`chibi.command.command`
    """
    return yum( 'localinstall', *pkgs )


def clean():
    return yum( 'clean', 'all' )
