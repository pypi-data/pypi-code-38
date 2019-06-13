from abc import abstractmethod, ABC

class Base(ABC):
    """
        Clase base para la implementacion de los tipos
        Worker y Fork
    """

    def __init__(self):
        pass
    
    @abstractmethod
    def process(self, request, fnc):
        """
            Metodo que se encargara de procesar los mensajes
            que se enviaran al microservicio.
        """
        return 0