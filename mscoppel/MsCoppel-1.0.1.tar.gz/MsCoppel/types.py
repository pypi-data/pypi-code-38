from enum import Enum, unique

@unique
class Types(Enum):
    """
        Tipos de elementos soportados en los microservicios
    """
    WORKER = 1
    FORK = 2

@unique
class TypesActions(Enum):
    CREATE = 1
    GET = 2
    DELETE = 3
    LIST = 4
    LISTENER = 5
    UPDATE = 6
    ERRORS = 7