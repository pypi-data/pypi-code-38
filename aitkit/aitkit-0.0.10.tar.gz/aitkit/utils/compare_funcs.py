"""Функции сравнения множеств, векторов и пр."""

def JaccardFunc(left:[], right:[]) -> float:
    """Сравнение множеств функцией Жаккара

    https://ru.wikipedia.org/wiki/Коэффициент_Жаккара
    
    Arguments:
        left {[]} -- левое множество
        right {[]} -- правое множество
    
    Returns:
        float -- насколько массивы похожи друг на друга на основе функции Жаккара (0 = совсем не похоже, 1 = идентичны)
    """

    if left is None and right is None:
        return 1.
    elif left is None and right is not None:
        return 0.
    elif left is not None and right is None:
        return 0.
    elif len(left) == 0 and len(right) == 0:
        return 1.
    else:

        set1 = set(left)
        set2 = set(right)
        x = len(set1.intersection(set2))
        y = len(set1.union(set2))

        if y == 0:
            return 0.
        else:
            return x / float(y)