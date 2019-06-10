import glob
import hashlib
import os
import re
import shutil

from chibi import b64
from chibi.atlas import Chibi_atlas
from chibi.file.path import Chibi_path
from chibi.nix import get_passwd, get_group
from chibi.snippet import regex


def current_dir():
    """
    regresa el directorio actual de trabajo

    Returns
    =======
    py:class:`chibi.file.Chibi_path`
    """
    return Chibi_path( os.getcwd() )


def file_dir( f ):
    return os.path.dirname( os.path.realpath( f ) )


def base_name( path ):
    return os.path.basename( path )


def cd( to ):
    """
    cambia el directorio actual

    Parameters
    ==========
    to: string
        dirrecion a la que se quiere cambiar

    Returns
    =======
    None
    """
    to = inflate_dir( to )
    os.chdir( to )


def inflate_dir( src ):
    """
    infla la dirrecion para obtner la ruta absoluta

    Parameters
    ==========
    src: string
        direcion que se quiere inflar

    Returns
    =======
    string
    """
    if '~' in src:
        return os.path.expanduser( src )
    else:
        return os.path.abspath( src )


def is_dir( src ):
    """
    revisa si una direcion es un directorio

    Returns
    =======
    bool
    """
    return os.path.isdir( src )


def is_file( src ):
    """
    revisa si una direcion es un archivo

    Returns
    =======
    bool
    """
    return os.path.isfile( src )


def get_file_from_path( src ):
    s = os.path.split( src )
    return s[-1]


def ls( src=None, recursive=False ):
    """
    lo mismo que ls en unix

    Returns
    =======
    iterador of strings
    """
    if src is None:
        src = current_dir()
    else:
        src = Chibi_path( src )
    if not recursive:
        dirs = glob.iglob( src )
        for d in dirs:
            try:
                for name in os.listdir( d ):
                    yield src + name
            except NotADirectoryError:
                yield d
    else:
        for r in ls( src ):
            yield r
            if is_a_folder( r ):
                for rr in ls( r, recursive=True ):
                    yield rr


def find( src=None, search_term=r'.*' ):
    name = re.compile( search_term )
    for f in ls( src, recursive=True ):
        last_part = base_name( f )
        if regex.test( name, last_part ):
            yield f


def find_only_files( src=None, search_term=r'.*' ):
    return (
        f for f in find( src, search_term=search_term )
        if is_a_file( f ) )


def find_only_folders( src=None, search_term=r'.*' ):
    return (
        f for f in find( src, search_term=search_term )
        if is_a_folder( f ) )


def ls_only_files( src=None ):
    """
    lo mismo que ls en unix pero solo archivos

    Returns
    =======
    iterador of strings
    """
    return ( f for f in ls( src ) if is_file( f ) )


def ls_only_dir( src=None ):
    """
    lo mismo que ls en unix pero solo directorios

    Returns
    =======
    iterador of strings
    """
    return ( name for name in ls( src ) if name.is_a_folder )


def mkdir( new_dir, is_ok_exists=True, verbose=True ):
    """
    crea un nuevo directiorio

    Parameters
    ==========
    new_dir: string
        nombre o direcion del nuevo directorio
    is_ok_exists: bool
        define si esta bien is el directorio ya existe
        y no lanza una exception
    """
    try:
        os.makedirs( inflate_dir( new_dir ), )
        if verbose:
            print( "se creo el directorio '{}'".format( new_dir ) )
    except OSError:
        if not is_ok_exists:
            raise


def join( *patch ):
    """
    une los argumentes en una direcion

    Parameters
    ==========
    patch: list of strings

    Returns
    =======
    string
    """
    patch = tuple( str( a ) for a in patch )
    return Chibi_path( os.path.join( *patch ) )


def exists( file_name ):
    """
    revisa si el archivo existe en la ruta

    Parameters
    ==========
    file_name: string

    Returns
    =======
    bool
    """
    return os.path.exists( file_name )


def move( source, dest, verbose=False ):
    """
    mueve archivos

    Parameters
    ==========
    source: string
        ruta del archivo original
    dest: string
        ruta del destine
    verbose: bool

    Returns
    =======
    None
    """
    g = glob.glob( source )
    if len( g ) > 1 and not is_a_folder( dest ):
        raise ValueError( "'{}' was expected be a dir".format( dest ) )
    for f in g:
        shutil.move( f, dest )
        if verbose:
            print( f, '->', dest )


def is_a_folder( dir ):
    return os.path.isdir( dir )


def is_a_file( f ):
    return os.path.isfile( f )


def copy( source, dest, verbose=False ):
    """
    copia el contenido de un archivo al destino

    Parameters
    ==========
    source: string
        ruta del archivo original
    dest: string
        ruta del destine del nuevo archivo
    verbose: bool

    Returns
    =======
    Non
    """
    g = glob.glob( source )
    if len( g ) > 1 and not is_a_folder( dest ):
        raise ValueError( "'{}' was expected be a dir".format( dest ) )
    for f in g:
        shutil.copy( f, dest )
        if verbose:
            print( f, '->', dest )


def copy_folder( source, dest ):
    shutil.copytree( str( source ), str( dest ) )


def ln( source, dest, verbose=True ):
    os.symlink( source, dest )
    if verbose:
        print( source, '->', dest )


def _print_verboce_chown( path, old_stat, current_stat ):
    user_change = old_stat.user.name != current_stat.user.name
    group_change = old_stat.group.name != current_stat.group.name

    if user_change or group_change:
        print(
            "el propietario de '{path}' cambio de '{old}' a '{new}'"
            .format(
                path=path, new="{user}:{group}".format(
                    user=current_stat.user.name,
                    group=current_stat.group.name ),
                old="{user}:{group}".format(
                    user=old_stat.user.name, group=old_stat.group.name ) ) )
    else:
        print(
            "el propietario de '{path}' permanece '{old}'"
            .format(
                path=path, new="{user}:{group}".format(
                    user=current_stat.user.name,
                    group=current_stat.group.name ),
                old="{user}:{group}".format(
                    user=old_stat.user.name, group=old_stat.group.name ) ) )


def read_in_chunks( file_name, prop='rb', chunk_size=4096 ):
    with open( file_name, prop ) as f:
        while True:
            current_read = f.read( chunk_size )
            if not current_read:
                break
            yield current_read


def check_sum_md5( file_name, check_sum ):
    md5 = hashlib.md5()
    for chunk in read_in_chunks( file_name ):
        md5.update( chunk )
    md5_bin = md5.digest()
    return b64.encode( md5_bin ) == check_sum


def delete( path ):
    if is_file( path ):
        os.remove( path )
    else:
        shutil.rmtree( path )


def chown(
        *paths, verbose=True, user_name=None, group_name=None,
        recursive=False ):
    if user_name is None:
        user = None
        uid = -1
    else:
        user = get_passwd( name=user_name )
        uid = user.uid

    if group_name is None:
        group = None
        gid = -1
    else:
        group = get_group( name=group_name )
        gid = group.gid

    for path in paths:
        old_stat = stat( path )
        os.chown( path, uid, gid )
        current_stat = stat( path )
        if verbose:
            _print_verboce_chown( path, old_stat, current_stat )

        if recursive and is_dir( path ):
            inner_paths = (
                join( path, dir )
                for dir in ls( inflate_dir( path ) ) )
            chown(
                *inner_paths, user=user, group=group, verbose=verbose,
                recursive=True )


def stat( src ):
    s = os.stat( src )
    result = Chibi_atlas( dict(
        mode=s.st_mode, ino=s.st_ino, dev=s.st_dev,
        nlink=s.st_nlink, size=s.st_size, atime=s.st_atime, mtime=s.st_mtime,
        ctime=s.st_ctime ) )
    result.user = get_passwd( uid=s.st_uid )
    result.group = get_group( gid=s.st_gid )

    return result


def add_extensions( file_name, *extensions ):
    """
    agrega extenciones al nombre del archivo

    Parameters
    ==========
    file_name: str
    extensions: tuple of str

    Returns
    =======
    str

    Examples
    ========
    >>>add_extensions( "image.jpg", "thumbnail" )
    "image.thumbnail.jpg"
    """
    file_name, ext = os.path.splitext( file_name )
    extensions = ".".join( extensions )
    file_name = ".".join( ( file_name, extensions ) )
    return Chibi_path( file_name + ext )


def common_root( *paths ):
    """
    encuentra el la carpeta raiz en comun

    Parameters
    ==========
    paths: tuple of str or Chibi_path

    Returns
    =======
    py:class:`chibi.file.Chibi_path`

    Examples
    ========
    >>>common_root( '/usr/var/log', '/usr/var/security' )
    '/usr/var/'
    """
    return Chibi_path( os.path.commonprefix( paths ) )


def get_relative_path( *paths, root=None ):
    """
    regresa los path relativos

    Parameters
    ==========
    paths: tuple of str or Chibi_path
    root: string

    Returns
    =======
    list of strings
        cuando se manda mas de path
    string
        cuando solo se envia 1 path

    Examples
    ========
    >>>get_relative_path( '/usr/var/log', '/usr/var/security' )
    [ 'log', 'security' ]
    >>>get_relative_path( '/usr/var/log', root='/usr/var/' )
    'log'
    """
    if len( paths ) > 1:
        if root is None:
            root = common_root( *paths )
    else:
        if root is None:
            raise NotImplementedError
    root = inflate_dir( root )

    result = [
        os.path.relpath( inflate_dir( path ), start=root )
        for path in paths ]
    if len( result ) == 1:
        return result[0]
    return result
