import sys

def Loggs(name):
    """
        Metodo para generar un elemento de logger
        @params name Nombre del modulo/libreria
    """
    from logbook import Logger, StreamHandler
    StreamHandler(sys.stdout).push_application()
    return Logger(name)