# https://jira.action-media.ru/browse/AITK-21
# есть массив функций f([токенов])
# каждая возвращает массив тегов
# производим трансформацию корпуса каждой функцией и аппендим результаты
# например, для массива тегов -- навешивать тег D если у документа есть теги из A, но нет тегов из B
 
from collections.abc import Iterable
from itertools import chain
import os
from multiprocessing.pool import Pool
from aitkit.utils.array_tools import splitArray
import logging

class RuleTagging:
    
    def __init__(self, rules:[callable]):
        self.rules = rules

    def __getitem__(self, key):
        if key is None:
            return None
        # [[]]
        elif isinstance(key, Iterable) and any([isinstance(x, Iterable) for x in key]) and any([not isinstance(x, str) for x in key]):
            return self.apply_many(key)
        elif isinstance(key, Iterable):
            return self.apply(key)
        else:
            raise KeyError(key)

    def apply(self, doc:[]) -> []:
        tags = []
        for r in self.rules:
            tags.append(r(doc))        

        rv = list(chain(*tags))
        logging.debug('RuleTagging.apply : документ = {}, теги = {}'.format(doc, rv))
        return rv

    def apply_many(self, docs:[[]]):
        # сеты до 10000 документов обрабатываем последовательно
        # больше И не-debug  -- распараллеливаем 
        if len(docs) <= 10000 or __debug__:
            logging.debug('RuleTagging.apply_many : навешивание тегов на множество документов в однопоточном режиме')
            return [self.apply(x) for x in docs]
        else:
            logging.debug('RuleTagging.apply_many : навешивание тегов на множество документов в многопоточном режиме')
            cpucount = len(os.sched_getaffinity(0))
            csize = int(len(docs) / cpucount)
            d = splitArray(enumerate(docs), csize) # нужно сохранять порядок айтемов, чтобы потом его восстановить
            with Pool() as p:
                res = p.map(self.apply_enum_split, d)
            
            return [y[1] for y in sorted(res, key=lambda x: x[0])]

    def apply_enum_split(self, docs:[(int, [])]) -> [(int, [])]:
        return [(i, self.apply(x)) for i, x in docs]