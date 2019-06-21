# import matplotlib
# # matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.animation as animation
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
import numpy as np
# import seaborn as sns
# import colours
import gaga.Results as Results

plt.style.use('ggplot')

class mcfost(Results):

    def __init__(self):

        Results.__init__(self)

