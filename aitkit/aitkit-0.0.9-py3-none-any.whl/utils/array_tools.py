# Нарезает массив окном размера len с шагом stride
#src - разбиваемый массив (список), length - размер окна, stride - шаг с которым окно идет по массиву (списку)
def sliceArray(src:[], length:int=1, stride:int=1) -> [[]]:
    return [src[i:i+length] for i in range(0, len(src), stride) if len(src[i:i+length]) == length]

# Нарезает массив окном размера len c шагом в размер окна
def splitArray(src:[], length:int) -> [[]]:
    return sliceArray(src, length, length)

# Преобразует массив токенов в мешок
def arr2bag(src:[]):
    return [(x, src.count(x)) for x in set(src)]

# Удаляет из массива src токены rem
def removeTokens(src:[], rem:[]) -> []:    
    return [t for t in src if t not in rem]

# Заменяет а массиве множество токенов аскриптора токенами дескриптора
def replaceAscriptor(src:[], asc:[], desc:[]) -> []:
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
