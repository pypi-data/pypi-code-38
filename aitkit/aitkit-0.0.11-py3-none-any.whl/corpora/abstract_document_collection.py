from abc import ABC, abstractmethod
import logging

CCNA = 1000

class AbstractDocumentCollection(ABC):
    """Абстрактная коллекция документов
    
    Keyword Arguments:
        documents {[]} -- генератор добавляемых документов (default: {None})
    """

    def __init__(self, documents:[]=None):
        """Конструктор
        
        Keyword Arguments:
            documents {[]} -- генератор добавляемых документов (default: {None})
        """
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