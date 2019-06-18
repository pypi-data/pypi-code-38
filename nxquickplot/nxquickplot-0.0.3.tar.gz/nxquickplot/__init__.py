name = 'nxquickplot'

import networkx
import matplotlib.pyplot as plt

def quickplot(g):
    plt.clf()
    networkx.draw_networkx(g, pos=networkx.kamada_kawai_layout(g))
    plt.show()

