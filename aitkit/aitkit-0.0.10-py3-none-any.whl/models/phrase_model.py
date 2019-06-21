from aitkit.utils.array_tools import removeTokens, replaceAscriptor
from collections.abc import Iterable
import logging

class PhraseModel:
    """Фразная модель. Заменяет в тексте аскрипторы дескрипторами (синонимия), удаляет стоп-слова.
    Keyword Arguments:
        stop_tokens {[]} -- стоп-слова (default: {None})

        asc_replacements {[((asc_tokens, [desc_tokens]))]} -- коллекция замен аскрипторов на дескрипторы (default: {None})
    """

    # Конструктор
    # stop_tokens -- стоп-токены
    # asc_replacements -- синонимия массив из (массив токенов аскрипторов и дескрипторы, на которые их нужно заменить)
    def __init__(self, stop_tokens:[]=None, asc_replacements:[((),[])]=None):

        """Фразная модель. Заменяет в тексте аскрипторы дескрипторами (синонимия), удаляет стоп-слова.
        Keyword Arguments:
            stop_tokens {[]} -- стоп-слова (default: {None})

            asc_replacements {[((asc_tokens, [desc_tokens]))]} -- коллекция замен аскрипторов на дескрипторы (default: {None})
        """

        self.stop_tokens = []
        self.asc_replacements = {}

        self.addStopTokens(stop_tokens)
        self.asc_repl_compiled = {}
        for x in asc_replacements:
            self.addAscReplacement(x[0], x[1])
            logging.debug('PhraseModel.__intit__ : добавлен asc = {}, desc = {}'.format(x[0], x[1]))

        self.recompile()


    def addStopTokens(self, tokens:[]):
        """Добавляет стоп-токены в модель
        
        Arguments:
            tokens {[]} -- добавляемые стоп-токены
        """
        if tokens is not None:
            for t in tokens:
                self.stop_tokens.append(t)
                logging.debug('PhraseModel.addStopTokens : добавлен стоп-токен {}'.format(t))

        # после добавления новых токенов -- пересобрать
        self.recompile()

    def removeStopTokens(self, tokens:[]):
        """Удаляет стоп-токены из модели
        
        Arguments:
            tokens {[]} -- удаляемые стоп-токены
        """
        self.stop_tokens = list(removeTokens(self.stop_tokens, tokens))
        self.recompile()

    def addAscReplacement(self, asc:(), desc:[]):
        """Добавляет новую замену аскрипторов дескрипторами
        
        Arguments:
            asc {[type]} -- описание одного аскриптора, кортеж из токенов
            desc {[type]} -- массив дескрипторов
        
        Raises:
            KeyError: недопустимый аскриптор
        """
        # удалить из аскриптора стоп-токены
        if asc is not None:
            self.asc_replacements[asc] = desc
        else:
            raise KeyError(asc)

        self.asc_repl_compiled[tuple(removeTokens(asc, self.stop_tokens))] = desc

    def removeAscReplacement(self, asc:()):
        """Удаляет аскриптор, подлежащий замене из коллекции замен
        
        Arguments:
            asc {[type]} -- кортеж с токенами аскриптора
        """
        if asc in self.asc_replacements:
            del self.asc_replacements[asc]
            self.recompile()

    def recompile(self):
        """Пересобрать все стоп-токены и аскрипторы-дескрипторы (из аскрипторов и дескрипторов нужно выкинуть известные стоп-токены)"""

        logging.debug('PhraseModel.recompile started')
        self.asc_repl_compiled = {}
        for key in self.asc_replacements.keys():
            k = tuple(removeTokens(key, self.stop_tokens))
            self.asc_repl_compiled[k] = self.asc_replacements[key]
        
        logging.debug('PhraseModel.recompile finished')

    def __getitem__(self, key):
        """Возвращает преобразование наборов токенов моделью

        [] -> []'
        [] -> [[]']
        """
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

    def transform(self, tokens:[]) -> []:
        """Трансформация одного набора токенов
        Выкинуть из фразы стоп-слова
        Поочереди заменить аскрипторы дескрипторами
        """
        
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