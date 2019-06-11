from git import Repo
from chibi.file.snippets import current_dir


def clone( url, dest=None ):
    """
    clona el repositorio de la url

    Parameters
    ==========
    url: string
        url del repositorio
    dest: string ( optional )
        destino de donde se clonara el repositorio
        por default es el directorio de trabajo
    """
    if dest is None:
        dest = current_dir()
    Repo.clone_from( url, dest )


def pull( src=None ):
    """
    hace pull a un repositorio

    Parameters
    ==========
    src: string
        ruta del repositorio que se quiere hacer pull
    """
    if src is None:
        src = current_dir()
    Repo( src ).remote().pull()
