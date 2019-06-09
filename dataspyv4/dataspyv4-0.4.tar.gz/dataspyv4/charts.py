import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from . import utils

def normality_plot(x, col, ax=0):
    ax1 = plt.subplot(ax)
    stats.probplot(x[col], plot=plt)
    plt.show()


def bar_plot(x, col):
    sns.catplot(y=col, kind="count", data=x)
    plt.show()


def dist_plot(x, col):
    sns.distplot(x[col])
    plt.show()


def box_plot(x, col, ax=0):
    sns.boxplot(x=x[col], ax=ax)
    plt.show()


def anomalies_graph(x, col):
    f, axes = plt.subplots(1, 2)
    box_plot(x, col, axes[0])
    normality_plot(x, col, axes[1])
    plt.show()


def catg_graph(x, col):
    bar_plot(x, col)


def continous_graph(x, col,pct, catg):
    if utils.isContinous(x[col], pct, catg):
        dist_plot(x, col)
    else:
        bar_plot(x, col)
