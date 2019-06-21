""" Утилитарные функции над массивами """

def sliceArray(src:[], length:int=1, stride:int=1) -> [[]]:
    """Нарезает массив окном размера len c шагом stride

    sliceArray([0, 1, 2, 3, 4, 5], 3, 1) = [[0,1,2], [1,2,3], [2,3,4], [3,4,5]]
    
    sliceArray([0, 1, 2, 3, 4, 5], 4, 2) = [[0,1,2,3], [2,3,4,5]]

    Arguments:
        src {[]} -- нарезаемый массив
    
    Keyword Arguments:
        length {int} -- размер окна (default: {1})
        stride {int} -- шаг, с которым нарезаем (default: {1})
    
    Returns:
        [[]] -- нарезку src окном len с шагом stride
    """
    return [src[i:i+length] for i in range(0, len(src), stride) if len(src[i:i+length]) == length]

def splitArray(src:[], length:int) -> [[]]:
    """Нарезает массив окном размера len с шагом в размер окна

    splitArray([0,1,2,3,4,5,6,7,8,9], 3) = [[0,1,2], [3,4,5], [6,7,8], [9]]
    
    Arguments:
        src {[]} -- нарезаемый массив
        length {int} -- размер окна
    
    Returns:
        [[]] -- нарезку массива окном len
    """
    return sliceArray(src, length, length)

def arr2bag(src:[]):
    """Преобразует массив токенов в мешок (каждый токен представлен кортежем -- (токен, сколько раз встречается в массиве))

    arr2bag([0, 1, 1, 2, 3, 3, 3]) = [(0, 1), (1, 2), (2, 1), (3, 3)]

    Arguments:
        src {[]} -- массив токенов
    
    Returns:
        [()] -- мешок токенов
    """
    return [(x, src.count(x)) for x in set(src)]

def removeTokens(src:[], rem:[]) -> []:    
    """Возвращает массив токенов src за исключением rem

    removeTokens([0, 1, 2, 2, 3], [0, 2]) = [1, 3]
    
    Arguments:
        src {[]} -- исходный массив токенов
        rem {[type]} -- токены, которые необходимо исключить
    
    Returns:
        [] -- токены из src за исключением токенов, перечисленных в rem
    """
    return [t for t in src if t not in rem]

def replaceAscriptor(src:[], asc:[], desc:[]) -> []:
    """Заменяет в массиве src множество токенов аскриптора asc дексрипторами токена (синонимия)

    replaceAscriptor([0, 1, 2, 3, 4, 5], [1,2], [99, 23, 96]) = [0, 99, 23, 96, 3, 4, 5]
    
    Arguments:
        src {[]} -- исходный массив
        asc {[]} -- токены аскриптора (токены, которые заменяем)
        desc {[]} -- токены дескрипторов (токены, которые записываем вместо акриптора)
    
    Returns:
        [] -- результат замены в массиве src токенов аскрипторов дескрипторами
    """
    src_repl = []
    length = len(asc)
    src_ = [src[i:i+length] for i in range(0, len(src), 1)]
    i = 0
    while i < len(src_):
        if src_[i] == asc:
            src_repl = src_repl + desc
            i+=length
        else:
            src_repl.append(src_[i][0])
            i+=1
    return src_repl
