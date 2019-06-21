from .abstract_dictionary import AbstractDictionary
from aitkit.utils.save_load import AbstractSaveLoad
import pickle
import logging

class Dictionary(AbstractDictionary, AbstractSaveLoad):
    """Простой словарь, храняший все токены в памяти
    
    Keyword Arguments:
            documents {list} -- исходные документы из которых формируется словарь (default: {[[]]})
    """
    
    @property
    def token2id(self) -> {str, int}:
        """Словарь соответствий токена его идентификатору в словаре"""
        return self.__token2id

    @property
    def id2token(self) -> {int, str}:
        """Словарь соответствия идентификатора токену"""
        return self.__id2token

    @property
    def id2tf(self) -> {int, int}:
        """Словарь term frequeny (частотность) токенов, ключ идентификатор токена в словаре"""
        return self.__id2tf

    @property
    def id2dfs(self) -> {int, int}:
        """Словарь document frequency токенов, ключ идентификатор токена в словаре"""
        return self.__id2dfs

    @property
    def new_id(self) -> int:
        """Получает новый идентификатор"""
        self.__new_id += 1
        return self.__new_id - 1
    
    def __init__(self, documents:[[]]=None):
        """Конструктор словаря
        
        Keyword Arguments:
            documents {list} -- исходные документы из которых формируется словарь (default: {[[]]})
        """

        self.__token2id = {}
        self.__id2token = {}
        self.__id2tf = {}
        self.__id2dfs = {}
        self.__new_id = 0

        super().__init__(documents)

    def save(self, path):
        """Сохраняет словарь
        
        Arguments:
            path {[]} -- путь к файлу, куда сохраняем словарь (если файл существует, он будет перезаписан)
        """
        logging.debug('Dictionary.save : начато сохранение в {}'.format(path))

        d = {}
        d['token2id'] = self.token2id
        d['id2token'] = self.id2token
        d['id2tf'] = self.id2tf
        d['id2dfs'] = self.id2dfs

        with open(path, 'wb+') as dst:
            pickle.dump(d, dst)

        logging.debug('Dictionary.save : завершено сохранение в {}'.format(path))
    
    @staticmethod
    def load(path):
        """Загружает словарь
        
        Arguments:
            path {String} -- путь к файлу
        
        Returns:
            [Dictionary] -- словарь
        """
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