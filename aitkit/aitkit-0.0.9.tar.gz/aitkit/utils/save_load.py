from abc import ABC, abstractmethod, abstractstaticmethod

# Абстрактный SaveLoad
class AbstractSaveLoad(ABC):

    # Сохраняет объект
    @abstractmethod
    def save(self, **kwargs):
        pass

    # Загружает объект
    @abstractstaticmethod
    def load(path, **kwargs):
        pass