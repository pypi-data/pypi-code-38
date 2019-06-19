from .abstract_dictionary import AbstractDictionary
from aitkit.utils.save_load import AbstractSaveLoad
import pickle
import logging

# Простой словарь, храняший все токены в памяти
class Dictionary(AbstractDictionary, AbstractSaveLoad):
    
    # Словарь токенов в памяти
    @property
    def token2id(self) -> {str, int}:
        return self.__token2id

    # Словарь идентификаторов в памяти
    @property
    def id2token(self) -> {int, str}:
        return self.__id2token

    # Словарь частотности токенов
    @property
    def id2tf(self) -> {int, int}:
        return self.__id2tf

    # Словарь частотны токенов в документах
    @property
    def id2dfs(self) -> {int, int}:
        return self.__id2dfs

    # Минимальный новый доступный идентификатор
    @property
    def new_id(self) -> int:
        self.__new_id += 1
        return self.__new_id - 1
    
    # Конструктор
    # documents -- массив токенов документов
    def __init__(self, documents:[[]]=None):
        self.__token2id = {}
        self.__id2token = {}
        self.__id2tf = {}
        self.__id2dfs = {}
        self.__new_id = 0

        super().__init__(documents)

    # Сохраняет словарь
    # path -- путь к файлу, куда происходит сохранение
    def save(self, path):
        logging.debug('Dictionary.save : начато сохранение в {}'.format(path))

        d = {}
        d['token2id'] = self.token2id
        d['id2token'] = self.id2token
        d['id2tf'] = self.id2tf
        d['id2dfs'] = self.id2dfs

        with open(path, 'wb+') as dst:
            pickle.dump(d, dst)

        logging.debug('Dictionary.save : завершено сохранение в {}'.format(path))
    
    # Загружает словарь
    # path -- путь к файлу, откуда загружаем словарь
    @staticmethod
    def load(path):
        logging.debug('Dictionary.load : начата загрузка из {}'.format(path))
        with open(path, 'rb') as src:
            d = pickle.load(src)
            res = Dictionary()
            res.__token2id = d['token2id']
            res.__id2token = d['id2token']
            res.__id2tf = d['id2tf']
            res.__id2dfs = d['id2dfs']
            
            # максимальный идентификатор
            x = max(res.id2token.keys())
            res.__new_id = x if x is not None and x >= 0 else 0

            logging.debug('Dictionary.load : завершена загрузка из {}, известных токенов {}'.format(path, len(res.token2id)))

            return res