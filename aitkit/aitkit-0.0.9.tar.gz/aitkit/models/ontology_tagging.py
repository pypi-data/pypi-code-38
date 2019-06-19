# https://jira.action-media.ru/browse/AITK-20
# Принимает коллекцию документов и массив из (онтология, массив тегов для навешивания)
# Возвращает массив массивов тегов, навешанных на коллекцию документов согласно заданным онтрлогиям

from collections import defaultdict
from collections.abc import Iterable
from aitkit.utils.array_tools import sliceArray, splitArray
from itertools import chain
import os
from multiprocessing.pool import Pool
import logging

class OntologyTagging:

    # ontology: [([массив токенов онтологии],[массив тегов, которые надо навесить, если онтология встретилась])]
    def __init__(self, ontology:[([],[])]):
        # онтологии группируем по длинне фразы так, чтобы под каждую длинну единыжды разбивать фразу окном
        logging.debug('OntologyTagging.__init__ : группировка онтологий по длинне фраз')
        self.ontology_dic = defaultdict(list)
        for ont in ontology:
            ln = len(ont[0])
            self.ontology_dic[ln].append(ont)
            logging.debug('OntologyTagging.__init__ : {} : добавлена онтология {}'.format(len(ont[0]), ont))

    def __getitem__(self, key):
        if key is None:
            return None
        # [[]]
        elif isinstance(key, Iterable) and any([isinstance(x, Iterable) for x in key]) and any([not isinstance(x, str) for x in key]):
            return self.tag_many(key)
        elif isinstance(key, Iterable):
            return self.tag(key)
        else:
            raise KeyError(key)

    # Тегирует один документ
    def tag(self, doc:[]) -> []:
        tags = []
        for ln in self.ontology_dic.keys():
            parts = sliceArray(doc, ln) # нарезка токенов doc окном пригодным для онтологий [[]]
            for ont in self.ontology_dic[ln]:
                if OntologyTagging.checkOntology(parts, ont[0]):
                    tags.append(ont[1])
        
        rv = list(chain(*tags))
        logging.debug('OntologyTagging.tag : фраза = {}, теги = {}'.format(doc, rv))
        return rv

    def tag_many(self, docs:[[]]) -> [[]]:
        # сеты до 10000 документов обрабатываем последовательно
        # больше И не-debug  -- распараллеливаем 
        if len(docs) <= 10000 or __debug__:
            logging.debug('OntologyTagging.tag_many : теггирование в один поток')
            return [self.tag(x) for x in docs]
        else:
            logging.debug('OntologyTagging.tag_many : мультипоточное теггирование')
            cpucount = len(os.sched_getaffinity(0))
            csize = int(len(docs) / cpucount)
            d = splitArray(enumerate(docs), csize) # нужно сохранять порядок айтемов, чтобы потом его восстановить
            with Pool() as p:
                res = p.map(self.tag_enum_split, d)
            
            return [y[1] for y in sorted(res, key=lambda x: x[0])]

    def tag_enum_split(self, docs:[(int, [])]) -> [(int, [])]:
        return [(i, self.tag(x)) for i, x in docs]



    # Проверяет есть ли в нарезке токены онтологии
    @staticmethod
    def checkOntology(parts:[[]], ont:[]) -> bool:
        return any([x == ont for x in parts])
