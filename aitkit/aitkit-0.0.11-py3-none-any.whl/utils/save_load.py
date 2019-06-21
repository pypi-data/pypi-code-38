from abc import ABC, abstractmethod, abstractstaticmethod

class AbstractSaveLoad(ABC):
    """Абстрактный метод для унификации классов, поддерживающих сохранение и загрузку состояния"""

    @abstractmethod
    def save(self, **kwargs):
        pass

    # Загружает объект
    @abstractstaticmethod
    def load(path, **kwargs):
        pass