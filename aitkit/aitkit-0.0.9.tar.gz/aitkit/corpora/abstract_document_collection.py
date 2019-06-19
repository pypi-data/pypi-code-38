from abc import ABC, abstractmethod
import logging

CCNA = 1000

# Абстрактная коллекция документов
class AbstractDocumentCollection(ABC):
    
    # Конструктор
    # documents -- генератор добавляемых документов
    def __init__(self, documents:[]=None):
        if documents is not None:
            cnt = 0
            for d in documents:
                self.appendDocument(d)

                cnt += 1
                if cnt % CCNA == 0:
                    logging.info('AbstractDocumentCollection.__init__ : добавлено документов в коллекцию {}'.format(cnt))

            logging.info('AbstractDocumentCollection.__init__ : завершено, добавлено документов в коллекцию {}'.format(cnt))

    @abstractmethod
    def __getitem__(self, key):
        pass

    # Добавляет новый документ в коллекцию
    # doc -- добавляемый документ
    @abstractmethod
    def appendDocument(self, doc):
        pass

    # Удаляет документ
    @abstractmethod
    def removeId(self, id:int):
        pass

    @abstractmethod
    def __len__(self):
        pass