from aitkit.utils.array_tools import sliceArray, splitArray, arr2bag
from aitkit.utils.save_load import AbstractSaveLoad
from aitkit.utils.compare_funcs import JaccardFunc
from aitkit.corpora import Dictionary, DocumentCollection
from collections.abc import Iterable
from multiprocessing.pool import Pool
import os, pickle, logging

CCNA = 1000

# Представление документов шинглами (n-граммами)
class ShingleModel(Iterable):
    
    # Конструктор шингл-модели
    # tokens -- токены документов
    # win_len -- размер окна шингла
    # diff_func -- функция сравнения наборов шинглов (напр., коэффифиент Жаккара)
    def __init__(self, documents:[[]], win_len:int, diff_func=None):
        logging.info('ShingleModel.__init__ : формирование шингл-представление с окном {} на коллекции документов длинной {}'.format(win_len, len(documents)))

        self.comparer = Comparer(self, JaccardFunc if diff_func is None else diff_func)
        self.dic = Dictionary()
        self.docs = DocumentCollection()
        self.winlen = win_len

        cnt = 0
        for d in documents:
            self.addDocument(d)

            cnt += 1
            if cnt % CCNA == 0:
                logging.info('ShingleModel.__init__ : добавлено документов {}'.format(cnt))

        logging.info('ShingleModel.__init__ : завершено, добавлено документов {}'.format(cnt))

    # Добавляет токены документа в коллекцию
    # doc -- токены, которыми представлен документ
    def addDocument(self, doc:[]):
        shingle_doc = [tuple(x) for x in sliceArray(doc, self.winlen)]
        self.dic.addDocument(shingle_doc)
        self.docs.appendDocument(self.dic.idfy(shingle_doc, False))
        logging.debug('ShingleModel.addDocument : добавлен документ {}'.format(doc))

    # Итератор документов в представлении
    def __iter__(self):
        return self.docs.__iter__()

    def __len__(self):
        return self.docs.__len__()

    # Геттер элементов предсталения
    # key is int -- возвращает шинглы key документа в коллекции
    # [] -> []' известными шинглами
    # [[]] -> [[]'] известными шинглами
    def __getitem__(self, key):
        if key is None:
            return None
        # [[]]
        elif isinstance(key, Iterable) and any([isinstance(x, Iterable) for x in key]) and any([not isinstance(x, str) for x in key]):
            logging.debug('ShingleModel.__getitem__ : трансформация множества документов')
            return [self.transform(x) for x in key]
        elif isinstance(key, Iterable):
            logging.debug('ShingleModel.__getitem__ : трансформация одного документа : {}'.format(key))
            return self.transform(key)
        elif isinstance(key, int):
            logging.debug('ShingleModel.__getitem__ : запрос документа {}'.format(key))
            return self.docs[key]
        else:
            raise KeyError(key)

    def transform(self, tokens:[]) -> []:
        if tokens is None:
            return None

        shingle_doc = [tuple(x) for x in sliceArray(tokens, self.winlen)]
        return self.dic.idfy(shingle_doc, False)

    # Сохраняет представление по указанному пути
    def save(self, path):
        logging.debug('ShingleModel.save : начало сохранения в {}'.format(path))
        with open(path, 'wb+') as dst:
            self.save_io(dst)
        logging.debug('ShingleModel.save : завершено сохранения в {}'.format(path))

    def save_io(self, file):
        pickle.dump(self, file)

    # Загружает модель из указанного файла
    @staticmethod
    def load(path):
        logging.debug('ShingleModel.save : начало загрузки из {}'.format(path))
        with open(path, 'rb') as src:
            rv = ShingleModel.load_io(src)
            logging.debug('ShingleModel.save : завершена загрузка из {}'.format(path))
            return rv
    
    @staticmethod
    def load_io(file):
        return pickle.load(file)

############

# Cравниватель шинглов
class Comparer:

    # Конструктор
    # diff_func -- функция сравнения наборов шинглов (напр., коэффифиент Жаккара)
    def __init__(self, parent, diff_func=JaccardFunc):
        self.diff_func = diff_func
        self.parent = parent

    # Сравнивает два набора токенов с помощью функции сравнения diff_func
    def compare(self, left:[], right:[]) -> float:
        logging.debug('Comparer.compare : сравнение {} vs {}'.format(left, right))
        return self.diff_func(left, right)

    # key is []
    # key is [[]]
    def __getitem__(self, key):
        if key is None:
            return None
        # [[]]
        elif isinstance(key, Iterable) and any([isinstance(x, Iterable) for x in key]) and any([not isinstance(x, str) for x in key]):
            
            # В ptvsd не поддерживается отладка многопоточных операций
            # Может выполняться долго и медленно
            if __debug__:
                logging.debug('Comparer.__getitem__ : transform many DEBUG MODE (single threaded)')
                return self.transform_many(key)
            else:
                logging.debug('Comparer.__getitem__ : transform many PROD MODE (multi threaded)')
                cpucount = len(os.sched_getaffinity(0))
                csize = int(len(key) / cpucount)
                with Pool() as p:
                    d = splitArray(key, csize)
                    res = p.map(self.transform_many, d)

            return res
        elif isinstance(key, Iterable):
            logging.debug('Comparer.__getitem__ : transform single')
            return self.transform(key)
        else:
            raise KeyError(key)
    
    def transform_many(self, docs:[]):
        logging.debug('Comparer.transform_many : преобразуемых документов = {}'.format(len(docs)))
        return [self.transform(x) for x in docs]

    def transform(self, tokens:[]) -> []:
        logging.debug('Comparer.transform : tokens = {}'.format(tokens))
        shingled = self.parent.transform(tokens)
        return [self.compare(shingled, x) for x in self.parent.docs]