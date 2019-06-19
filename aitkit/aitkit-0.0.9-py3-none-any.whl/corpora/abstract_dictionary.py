from abc import ABC, abstractmethod
from collections.abc import Iterable
from aitkit.utils.array_tools import arr2bag
import logging

CCNA = 1000

# Абстрактный 
class AbstractDictionary(ABC, Iterable):

    # Словарь идентификатороа
    @property
    @abstractmethod
    def token2id(self):
        pass

    # Словарь токенов
    @property
    @abstractmethod
    def id2token(self):
        pass

    # Словарь частотности токенов
    @property
    @abstractmethod
    def id2tf(self):
        pass

    # Словарь частотны токенов в документах
    @property
    @abstractmethod
    def id2dfs(self):
        pass

    # геттер, минимальный новый доступный идентификатор
    @property
    @abstractmethod
    def new_id(self) -> int:
        pass

    def __init__(self, documents=[[]]):
        cnt = 0
        if documents is not None:
            for d in documents:
                self.addDocument(d)
                
                cnt += 1
                if cnt % CCNA == 0:
                    logging.info('AbstractDictionary.__init__ :  добавлено в словарь документов {}'.format(cnt))

            logging.info('AbstractDictionary.__init__ :  завершено, добавлено в словарь документов {}'.format(cnt))

    # Добавляет в словарь новый документ
    def addDocument(self, document:[object]):
        if document is not None:
            for w in set(document):
                self.addToken(w, document.count(w))
            
            logging.debug('AbstractDictionary.addDocument : {}'.format(document))

    # Добавляет новый токен в словарь
    def addToken(self, token:object, tf:int = 1):
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
        
    # Удаляет токен из словаря
    def deleteToken(self, token:str):
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

    # Удаляет ключ из словаря
    def deleteId(self, id:int):

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

    # Преобразует массив токенов документа в массив идентификаторов
    # tokens -- токены документа
    # ignore_unknown -- игнорировать ли неизвестные токены (True -- неизвестные токены будут проигнорированы, False -- будут замененты на -1)
    def idfy(self, tokens:[], ignore_unknown:bool=True) -> []:
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

    # Уменьшает пресутствие ключа в словаре (и подчищает, если удалено навсегда)
    def reduceId(self, id_with_df:()):
        
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