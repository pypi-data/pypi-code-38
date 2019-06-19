# функции сравнения

# Функция схожести множеств на основе коэф Жаккара
# https://ru.wikipedia.org/wiki/Коэффициент_Жаккара
def JaccardFunc(left:[], right:[]) -> float:

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