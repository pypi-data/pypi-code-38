class Error(Exception):
    """Clase base para los errres"""
    pass

class ErrorMs(Error):
    """
        Clase para la definicion de errores dentro de
        los microservicios
    """
    def __init__(self, errorCode, message = ''):
        self.errorCode = errorCode
        self.message = message