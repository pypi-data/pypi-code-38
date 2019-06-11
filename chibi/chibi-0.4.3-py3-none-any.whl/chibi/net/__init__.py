from chibi.file.snippets import current_dir, join
from urllib import request


def download( url, directory=None, file_name=None ):
    """
    descarga archivos o lo que sea de una url

    Parameters
    ==========
    url: string
        url de la descarga
    directory: string ( optional )
        directorio en que se descarga el archivo
        por default es el actual directorio de trabajo
    file_name: string ( optional )
        nombre del archivo de la descarga
        por default es la ultima parte de la url

    Returns
    =======
    string
        direcion del archivo descargado
    """
    if directory is None:
        directory = current_dir()

    if file_name is None:
        file_name = url.rsplit( '/', 1 )[1]
    response = request.urlopen( url, timeout=30 )
    patch = join( directory, file_name )
    with open( patch, 'wb' ) as file:
        file.write( response.read() )
    return patch
