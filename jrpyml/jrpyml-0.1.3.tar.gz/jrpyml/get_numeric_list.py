from numpy.random import uniform, seed
from numpy import round

def get_numeric_list():
    seed(0)
    x = list(round(uniform(-40,90,55748), decimals = 2))
    return x

