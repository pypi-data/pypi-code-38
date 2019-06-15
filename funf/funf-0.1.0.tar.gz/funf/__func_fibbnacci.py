from math import sqrt


def Fibb_rec(x):
    if x <= 1:
        return x
    else:
        return Fibb_rec(x-1) + Fibb_rec(x - 2)


def Find_Fibb(x):
    assert x > 0, ValueError(f"Values is Not Desired>> {x}")
    sqrt_five = sqrt(5)
    return int((((1+sqrt_five)/2)**x - ((1-sqrt_five)/2)**x)/sqrt_five)


def Fibb_Store(x, series=[1, 1]):
    """Optimized version for frequently used .
        it Generate Fibb List and Store it the fibb number range found in this 
        then it return or it extends list
    """
    z = len(series)
    if x < z:
        return series[x]
    else:
        for i in range(z, x):
            series.append(series[i-2]+series[i-1])
        return series[x - 1]


def Fibb_List(x, series):
    assert x > 0, ValueError
    for i in range(2, x-2):
        series.append(series[i-2]+series[i-1])
    return series


def Fibb_series(start=1, end=10):
    """Generate Custom Range of Fibbnocci number list"""
    a = Find_Fibb(start)
    b = Find_Fibb(start + 1)
    return Fibb_List(end - start, series=[a, b])
