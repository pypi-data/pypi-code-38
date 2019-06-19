from aitkit.corpora.dictionary import Dictionary
from aitkit.corpora.doc_collection import DocumentCollection
from .phrase_model import PhraseModel
from aitkit.utils.array_tools import arr2bag
import logging

CNNA = 1000

# Есть коллекция документов (массив массивов слов)
# И фразная модель
# Текстпроцессор append only
# Каждый добавляемый в него документ преобразуется фразной моделью, добавляется в словарь, айдифицируется и запоминается
# Можно получить массив идентификаторов слов документа
# Можно получить мешки слов документов
# Можно получить словарь

class Textprocessor:
    
    def __init__(self, phrase_model:PhraseModel=None):
        self.dictionary = Dictionary()  # словарь
        self.phrase_model = phrase_model  # фразная модель (если не передана, то преобразования не будет)
        self.documents = DocumentCollection()  # коллекция сформированных документов

    # добавляет новый документ
    # преобразует его фразной моделью
    # добавляет в словарь
    # идифицирует
    # добавляет в коллекцию документов
    def append(self, doc:[]):
        
        # если нет фразной модели, тогда оставляем массив токенов as is
        transformed = self.phrase_model.transform(doc) if self.phrase_model is not None else doc

        self.dictionary.addDocument(transformed)
        ids = self.dictionary.idfy(transformed)
        self.documents.appendDocument(ids)

    # добавляет в процессор коллекцию документов
    def append_docs(self, docs:DocumentCollection):
        cnt = 0
        for doc in docs:
            self.append(doc)
            cnt += 1
            if cnt % CNNA == 0:
                logging.info('Textprocessor.append_docs : добавлено документов {}'.format(cnt))

            logging.info('Textprocessor.append_docs : добавлено документов {}'.format(cnt))

    # Возвращает генератор с мешком слов
    @property
    def bow(self) -> []:
        return [arr2bag(x) for x in self.documents]