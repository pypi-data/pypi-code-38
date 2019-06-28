import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib_venn import venn2


def get_venn(array_a, array_b, name_a, name_b):
    set_a = set(array_a)
    set_b = set(array_b)
    n_a = len(set_a)
    n_b = len(set_b)
    n_a_b = len(set_a.intersection(set_b))

    n_a_notb = n_a - n_a_b
    n_b_nota = n_b - n_a_b

    sns.set()
    plt.figure(figsize=(15, 5))
    venn2(subsets=(n_a_notb, n_b_nota, n_a_b), set_labels=(name_a, name_b))
    plt.show()


def get_quantile(array, intervals=0.01):
    for interval in np.arange(intervals, 1 + intervals, intervals):
        print("Quantile {:.3f} : {}".format(interval, array.quantile(interval)))
