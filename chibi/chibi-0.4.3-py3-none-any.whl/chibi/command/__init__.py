from subprocess import Popen, PIPE


def build_popen( str_command, *args, stdout=None, stderr=None ):
    """
    contrulle el popen para los comandos

    Parameters
    ==========
    str_command: string
        comando que se quiere usar
    args: tuple
        argumentos para el comando
    stdout: string
        usa `pipe` si se queire sar el PIPE por default
    stderr: string
        usa `pipe` si se queire sar el PIPE por default

    Returns
    =======
    Popen
    """
    if isinstance( stdout, str) and stdout.lower() == 'pipe':
        stdout = PIPE
    if isinstance( stderr, str) and stderr.lower() == 'pipe':
        stdout = PIPE

    proc = Popen( ( str_command, *args ), stdout=stdout, stderr=stdout )
    return proc


def command( str_command, *args, stdout=None, stderr=None ):
    """
    ejecuta un comando

    Parameters
    ==========
    str_command: string
        comando que se quiere usar
    args: tuple
        argumentos para el comando
    stdout: string
        usa `pipe` si se queire sar el PIPE por default
    stderr: string
        usa `pipe` si se queire sar el PIPE por default

    Returns
    =======
    tuple
        el primer valor seria stdout y el segundo stderr
    """
    proc = build_popen( str_command, *args, stdout=stdout, stderr=stderr)
    result, error = proc.communicate()
    if result is not None:
        result = result.decode( 'utf-8' )
    if error is not None:
        error = error.decode( 'utf-8' )
    return result, error, proc.returncode
