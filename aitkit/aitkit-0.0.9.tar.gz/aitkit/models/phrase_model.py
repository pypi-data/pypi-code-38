from aitkit.utils.array_tools import removeTokens, replaceAscriptor
from collections.abc import Iterable
import logging

# Фразный преобразователь
# Удаляет стоп-токены
# Заменяет аскрипторы дескрипторами
class PhraseModel:

    # Конструктор
    # stop_tokens -- стоп-токены
    # asc_replacements -- синонимия массив из (массив токенов аскрипторов и дескрипторы, на которые их нужно заменить)
    def __init__(self, stop_tokens:[]=None, asc_replacements:[((),[])]=None):
        self.stop_tokens = []
        self.asc_replacements = {}

        self.addStopTokens(stop_tokens)
        self.asc_repl_compiled = {}
        for x in asc_replacements:
            self.addAscReplacement(x[0], x[1])
            logging.debug('PhraseModel.__intit__ : добавлен asc = {}, desc = {}'.format(x[0], x[1]))

        self.recompile()


    # Добавляет новыe стоп-токены
    def addStopTokens(self, tokens:[]):
        if tokens is not None:
            for t in tokens:
                self.stop_tokens.append(t)
                logging.debug('PhraseModel.addStopTokens : добавлен стоп-токен {}'.format(t))

        # после добавления новых токенов -- пересобрать
        self.recompile()

    # Удаляет стоп-токены из модели
    def removeStopTokens(self, tokens:[]):
        self.stop_tokens = list(removeTokens(self.stop_tokens, tokens))
        self.recompile()

    # Заменяет массив токенов, описывающих аскриптор токенами дескриптора
    def addAscReplacement(self, asc:(), desc:[]):
        # удалить из аскриптора стоп-токены
        if asc is not None:
            self.asc_replacements[asc] = desc
        else:
            raise KeyError(asc)

        self.asc_repl_compiled[tuple(removeTokens(asc, self.stop_tokens))] = desc

    # Удаляет аскриптор, подлежащий замене из коллекции аскрипторов
    def removeAscReplacement(self, asc:()):
        if asc in self.asc_replacements:
            del self.asc_replacements[asc]
            self.recompile()

    # Пересобрать все стоп-токены и аскрипторы-дескрипторы (из аскрипторов и дескрипторов нужно выкинуть известные стоп-токены)
    def recompile(self):
        logging.debug('PhraseModel.recompile started')
        self.asc_repl_compiled = {}
        for key in self.asc_replacements.keys():
            k = tuple(removeTokens(key, self.stop_tokens))
            self.asc_repl_compiled[k] = self.asc_replacements[key]
        
        logging.debug('PhraseModel.recompile finished')

    # Возвращает преобразование наборов токенов моделью
    # [] -> []'
    # [] -> [[]']
    def __getitem__(self, key):
        if key is None:
            return None
        elif isinstance(key, Iterable) and any([isinstance(x, Iterable) for x in key]) and any([not isinstance(x, str) for x in key]):
            # трансформация для [[токенов]]
            return [self.transform(x) for x in key]
        elif isinstance(key, Iterable):
            # трансформация для [токенов]
            return self.transform(key)
        else:
            raise KeyError(key)

    # Трансформация одного набора токенов
    # Выкинуть из фразы стоп-слова
    # Поочереди заменить аскрипторы дескрипторами
    def transform(self, tokens:[]) -> []:
        logging.debug('PhraseModel.transform : {}'.format(tokens))
        if tokens is None:
            return []
        
        t = tokens
        if self.stop_tokens is not None:
            t = removeTokens(t, self.stop_tokens)

        if self.asc_repl_compiled is not None:
            for key in self.asc_repl_compiled.keys():
                t = replaceAscriptor(t, list(key), self.asc_repl_compiled[key])

        return list(t)