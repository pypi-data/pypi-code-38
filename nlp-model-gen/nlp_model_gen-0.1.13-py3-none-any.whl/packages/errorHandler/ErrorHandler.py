# @Vendors
from ast import literal_eval
import datetime

# @Logger
from nlp_model_gen.packages.logger.Logger import Logger

# @Constants
from nlp_model_gen.constants.constants import STD_TIME_OUTPUT

# @Assets
from .assets.errors import ERROR_DATA, GENERIC_ERROR, UNKNOWN_ERROR

class ErrorHandler:
    def __init__(self):
        pass

    @staticmethod
    def get_timestamp():
        """
        Devuelve una cadena con la fecha y hora actual.

        :return: [String] - Cadena de caracteres con la fecha y hora actual
        """ 
        current_date = datetime.datetime.now()
        return current_date.strftime(STD_TIME_OUTPUT)

    @staticmethod
    def get_error_dict(exception):
        """
        Obtiene el diccionatio que representa el error de una excepción.

        :exception: [Exception] - Excepción de la cual extraer el diccionario.

        :return: [Dict] - Diccionario con los datos del error.
        """
        try:
            return literal_eval(str(exception))
        except:
            return {
                'code': UNKNOWN_ERROR['error_code'], 
                'description': UNKNOWN_ERROR['description'],
                'source': UNKNOWN_ERROR['source'],
                'timestamp': ErrorHandler.get_timestamp()
            }

    @staticmethod
    def log_error(error_data, log_data):
        """
        Loggea los datos de un error

        :error_data: [Dict] - Datos del error

        :log_data: [List] - Datos adicionales de log
        """
        log_code = error_data['log']
        Logger.log(log_code, log_data)

    @staticmethod
    def get_error(code, log_data):
        """
        Obtiene el error a partir del código, si este no existe devuelve
        el error generico.

        :code: [String] - Código del error.

        :log_data: [List] - Datos adicionales del log

        :return: [Dict] - Diccionario con la información del error.
        """
        

        if code in ERROR_DATA.keys():
            error_data = ERROR_DATA[code]
            ErrorHandler.log_error(error_data, log_data)
            return {
                'code': code, 
                'description': error_data['description'],
                'source': error_data['source'],
                'timestamp': ErrorHandler.get_timestamp()
            }
        return {
            'code': GENERIC_ERROR['error_code'], 
            'description': GENERIC_ERROR['description'],
            'source': GENERIC_ERROR['source'],
            'timestamp': ErrorHandler.get_timestamp()
        }

    @staticmethod
    def raise_error(code, log_data=None):
        """
        Dispara una excepción a partir de un código de error determinado.

        :code: [String] - Código del error.

        :log_data: [List] - datos de log
        """
        additional_log_data = log_data if log_data is not None else list([])
        error = ErrorHandler.get_error(code, additional_log_data)
        raise Exception(error)
