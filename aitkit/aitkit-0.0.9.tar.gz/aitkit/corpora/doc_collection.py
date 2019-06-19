from aitkit.utils.save_load import AbstractSaveLoad
from .abstract_document_collection import AbstractDocumentCollection
from collections.abc import Iterable
import pickle
import logging

# Коллекця документов
class DocumentCollection(AbstractDocumentCollection, Iterable, AbstractSaveLoad):

    # Конструктор
    # documents -- коллекция документов
    def __init__(self, documents:[]=None):
        self.documents = []
        super().__init__(documents)

    # Добавляет новый документ в коллекцию
    # doc -- добавляемый документ
    def appendDocument(self, doc):
        self.documents.append(doc)
        logging.debug('DocumentCollection.appendDocument : добавлен документ {}'.format(doc))

    def __iter__(self):
        return iter(self.documents)

    def __getitem__(self, key):
        try:

            if isinstance(key, int):
                return self.documents[key]
            else:
                raise KeyError(key)

        except IndexError:
            raise KeyError(key)

    def __len__(self):
        return len(self.documents)

    # Сохраняет коллекцию документов
    # path -- путь к файлу, куда записывается сериализованная коллекция
    def save(self, path):
        logging.debug('DocumentCollection.save : начато сохранение в {}'.format(path))
        with open(path, 'wb+') as dst:
            pickle.dump(self.documents, dst)
        logging.debug('DocumentCollection.save : завершено сохранение в {}'.format(path))

    # Загружает коллекцию документов
    # path -- путь к файлу с сериализованной коллекцией
    @staticmethod
    def load(path):
        logging.debug('DocumentCollection.load : начата загрузка из {}'.format(path))
        with open(path, 'rb') as src:
            docs = pickle.load(src)
            rv = DocumentCollection(documents=docs)

        logging.debug('DocumentCollection.load : закончена загрузка из {}, количество документов {}'.format(path, rv.len))
        return rv

    # Удаляет документ
    def removeId(self, id:int):
        logging.debug('DocumentCollection.removeId : удаление документа {}'.format(id))
        try:
            del self.documents[id]
        except IndexError:
            raise KeyError(id)