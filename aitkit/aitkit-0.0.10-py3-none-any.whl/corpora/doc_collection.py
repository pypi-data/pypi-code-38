from aitkit.utils.save_load import AbstractSaveLoad
from .abstract_document_collection import AbstractDocumentCollection
from collections.abc import Iterable
import pickle
import logging

class DocumentCollection(AbstractDocumentCollection, Iterable, AbstractSaveLoad):
    """Коллекця документов в памяти
    
    Keyword Arguments:
            documnts {[]} -- генератор добавляемых документов (default: {None})
    """

    def __init__(self, documents:[]=None):
        """Конструктор
        
        Keyword Arguments:
            documnts {[]} -- генератор добавляемых документов (default: {None})
        """
        self.documents = []
        super().__init__(documents)

    def appendDocument(self, doc):
        """Добавляет новый документ в коллекцию
        
        Arguments:
            doc {[]} -- добавляемый документ
        """
        self.documents.append(doc)
        logging.debug('DocumentCollection.appendDocument : добавлен документ {}'.format(doc))

    def __iter__(self):
        """Итератор документов в коллекции"""
        return iter(self.documents)

    def __getitem__(self, key:int):
        """Получает документ из коллекции по индексу
        
        Arguments:
            key {int} -- индекс документа в коллекции
        
        Raises:
            KeyError: индекс не в массиве
        
        Returns:
            [] -- документ по указанному индексу
        """
        try:

            if isinstance(key, int):
                return self.documents[key]
            else:
                raise KeyError(key)

        except IndexError:
            raise KeyError(key)

    def __len__(self):
        """Размер коллекции
        
        Returns:
            [int] -- размер коллекции
        """
        return len(self.documents)

    def save(self, path:str):
        """Сохраняет коллекцию документов
        
        Arguments:
            path {[String]} -- путь к файлу, куда записывается сериализованная коллекция (если файл существует, он будет перезаписан)
        """
        logging.debug('DocumentCollection.save : начато сохранение в {}'.format(path))
        with open(path, 'wb+') as dst:
            pickle.dump(self.documents, dst)
        logging.debug('DocumentCollection.save : завершено сохранение в {}'.format(path))

    @staticmethod
    def load(path:str):
        """Загружает коллекцию документов
        
        Arguments:
            path {[String]} -- путь к файлу с сериализованной коллекцией
        
        Returns:
            [DocumentCollection] -- десериализованная коллекция документов
        """
        logging.debug('DocumentCollection.load : начата загрузка из {}'.format(path))
        with open(path, 'rb') as src:
            docs = pickle.load(src)
            rv = DocumentCollection(documents=docs)

        logging.debug('DocumentCollection.load : закончена загрузка из {}, количество документов {}'.format(path, len(rv)))
        return rv

    def removeId(self, id:int):
        """Удаляет документ
        
        Arguments:
            id {int} -- индекс документа в коллекции
        
        Raises:
            KeyError: документ с указанным индексом в коллекции отсутствует
        """
        logging.debug('DocumentCollection.removeId : удаление документа {}'.format(id))
        try:
            del self.documents[id]
        except IndexError:
            raise KeyError(id)