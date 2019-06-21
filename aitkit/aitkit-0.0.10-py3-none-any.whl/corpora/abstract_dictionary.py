from abc import ABC, abstractmethod
from collections.abc import Iterable
from aitkit.utils.array_tools import arr2bag
import logging

CCNA = 1000

class AbstractDictionary(ABC, Iterable):
    """Абстрактный словарь
    
    Keyword Arguments:
            documents {list} -- исходные документы из которых формируется словарь (default: {[[]]})
    """

    @property
    @abstractmethod
    def token2id(self):
        """Словарь соответствий токена его идентификатору в словаре"""
        pass

    @property
    @abstractmethod
    def id2token(self):
        """Словарь соответствия идентификатора токену"""
        pass

    @property
    @abstractmethod
    def id2tf(self):
        """Словарь term frequeny (частотность) токенов, ключ идентификатор токена в словаре"""
        pass

    @property
    @abstractmethod
    def id2dfs(self):
        """Словарь document frequency токенов, ключ идентификатор токена в словаре"""
        pass

    @property
    @abstractmethod
    def new_id(self) -> int:
        """Получает новый идентификатор"""
        pass

    def __init__(self, documents=[[]]):
        """Конструктор словаря
        
        Keyword Arguments:
            documents {list} -- исходные документы из которых формируется словарь (default: {[[]]})
        """
        cnt = 0
        if documents is not None:
            for d in documents:
                self.addDocument(d)
                
                cnt += 1
                if cnt % CCNA == 0:
                    logging.info('AbstractDictionary.__init__ :  добавлено в словарь документов {}'.format(cnt))

            logging.info('AbstractDictionary.__init__ :  завершено, добавлено в словарь документов {}'.format(cnt))

    def addDocument(self, document:[]):
        """Добавляет новый документ в словарь
        
        Arguments:
            document {[]} -- массив токенов добавляемого документа
        """
        if document is not None:
            for w in set(document):
                self.addToken(w, document.count(w))
            
            logging.debug('AbstractDictionary.addDocument : {}'.format(document))

    def addToken(self, token, tf:int = 1):
        """Добавляет новый токен в словарь
        
        Arguments:
            token {object} -- добавляемый токен
        
        Keyword Arguments:
            tf {int} -- частота токена в документе (default: {1})
        """
        if token not in self.token2id:
            id = self.new_id
            self.token2id[token] = id
            logging.debug('AbstractDictionary.addToken : новый токен {} с id {}'.format(token, id))
        else:
            id = self.token2id[token]

        if id not in self.id2token:
            self.id2token[id] = token

        if id not in self.id2dfs:
            self.id2dfs[id] = 0

        if id not in self.id2tf:
            self.id2tf[id] = 0

        self.id2tf[id] += tf
        self.id2dfs[id] += 1

        logging.debug('AbstractDictionary.addToken : обновлен токен {} с id {} -> tf = {}, dfs = {}'.format(token, id, self.id2tf[id], self.id2dfs[id]))
        
    def deleteToken(self, token):
        """Удаляет токен из словаря
        
        Arguments:
            token {str} -- уаляемый токен
        
        Raises:
            KeyError: если указанного токена нет в словаре
        """
        if token in self.token2id:
            id = self.token2id[token]
            self.id2dfs.pop(id, None)
            self.id2tf.pop(id, None)
            self.id2token.pop(id, None)
            self.token2id.pop(token, None)
        else:
            notFound = True
            for k, v in self.id2token.items():
                if v == token:
                    notFound = False
                    id = k
                    self.id2dfs.pop(id, None)
                    self.id2tf.pop(id, None)
                    self.id2token.pop(id, None)
                    break
            if notFound:
                raise KeyError("Token " + token + " not in dictionary")

    def deleteId(self, id:int):
        """Удаляет ключ из словаря
        
        Arguments:
            id {int} -- ключ (идентификатор) токена в словаре
        
        Raises:
            KeyError: если указанный идентификатор в словаре не найден
        """

        logging.debug('AbstractDictionary.deleteId : удаление токена {}'.format(id))

        self.id2dfs.pop(id, None)
        self.id2tf.pop(id, None)
        if id in self.id2token:
            token = self.id2token[id]
            self.id2token.pop(id, None)
            self.token2id.pop(token, None)
        else:
            notFound = True
            for k, v in self.token2id.items():
                if v == id:
                    notFound = False
                    token = k
                    self.token2id.pop(token, None)
                    break
            if notFound:
                raise KeyError("ID " + str(id) + " not in dictionary")

    # 
    # ignore_unknown -- игнорировать ли неизвестные токены (True -- неизвестные токены будут проигнорированы, False -- будут замененты на -1)
    def idfy(self, tokens:[], ignore_unknown:bool=True) -> []:
        """Преобразует массив токенов в массив идентификаторов
        
        Arguments:
            tokens {[]} -- преобразуемый массив токенов
        
        Keyword Arguments:
            ignore_unknown {bool} -- игнорировать незнакомые токены (True = вместо незнакомого токена не будет ничего, False -- на месте незнакомого токена напишем -1) (default: {True})
        
        Returns:
            [] -- замена токенов ключами в словаре
        """
        z = [self.token2id[x] if x in self.token2id else -1 for x in tokens]
        if ignore_unknown:
            rv =  [x for x in z if x > 0]
            logging.debug('AbstractDictionary.idfy : {}'.format(rv))
            return rv
        else:
            logging.debug('AbstractDictionary.idfy : {}'.format(z))
            return z

    # Преобразует документ в мешок слов
    # tokens -- токены документа
    def doc2bow(self, tokens:[], ignore_unknown:bool = True) -> []:
        """Преобразует токены в мешок слов с ключами в словаре
        
        Arguments:
            tokens {[]} -- преобразуемый массив токенов
        
        Keyword Arguments:
            ignore_unknown {bool} -- игнорировать незнакомые токены (True = вместо незнакомого токена не будет ничего, False -- на месте незнакомого токена напишем -1) (default: {True})
        
        Returns:
            [] -- мешок слов с ключами в словаре
        """
        z = self.idfy(tokens, ignore_unknown)
        rv = arr2bag(z)
        logging.debug('AbstractDictionary.doc2bow : {}'.format(rv))
        return rv

    def __iter__(self):
        return iter(self.token2id)

    def __getitem__(self, key):
        try:
            if key in self.token2id:
                return self.token2id[key]
            else:
                raise KeyError(key)
        except:
            raise KeyError(key)

    def __contains__(self, key):
        return self.token2id.__contains__(key)

    def __len__(self):
        return len(self.token2id)

    def reduceId(self, id_with_df:()):
        """Уменьшает присутствие ключа в словаре (и подчищает, если удалено навсегда)
        
        Arguments:
            id_with_df {(int, int)} -- кортеж ключ документа и в скольких документах он встречается
        
        Raises:
            KeyError: ключ не найден
        """
        
        if id_with_df is None:
            return

        id = id_with_df[0]
        if id in self.id2token:
            token = self.id2token[id]
        else:
            raise KeyError(id)
            
        # dfs
        if id in self.id2dfs:
            if self.id2dfs[id] <= 1:
                del self.id2dfs[id]
            else:
                self.id2dfs[id] -= 1

        # tf
        if id in self.id2tf:
            if self.id2tf[id] - id_with_df[1] < 1:
                del self.id2tf[id]
            else:
                self.id2tf[id] -= id_with_df[1]

        # если токен больше не встречается ни в одном документе, удаляем из словарей id2token и token2id
        if id not in self.id2tf and id not in self.id2dfs:
            del self.id2token[id]
            del self.token2id[token]