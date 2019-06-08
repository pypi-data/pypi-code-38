# @Vendors
from abc import ABC

class Singleton(type):
    """
    Implementación de Singleton
    """
    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

class Observable:
    """
    Implementación de observable
    """
    def __init__(self):
        self.__observers = list([])

    def add_observer(self, observer):
        """
        Agrega un observador
        """
        self.__observers.append(observer)

    def notify(self, data):
        """
        Notifica a los observadores un evento.

        :data: [Any] - Datos a notificar al observer
        """
        for observer in self.__observers:
            observer.update(data)

class Observer(ABC):
    """
    Implementación de observer (clase abstracta)
    """
    def __init__(self):
        pass

    def update(self, data):
        pass

class ObservableSingleton(metaclass=Singleton):
    """
    Implementación de observable combinado con singleton
    """
    def __init__(self):
        self.__observers = list([])

    def add_observer(self, observer):
        """
        Agrega un observador
        """
        self.__observers.append(observer)

    def notify(self, data):
        """
        Notifica a los observadores un evento.

        :data: [Any] - Datos a notificar al observer
        """
        for observer in self.__observers:
            observer.update(data)

class ObserverSingleton(metaclass=Singleton):
    """
    Implementación de observer combinado con singleton
    """
    def __init__(self):
        pass

    def update(self, data):
        pass
