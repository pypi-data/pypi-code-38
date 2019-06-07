import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

__author__ = "AUMA"
__copyright__ = "Copyright 2018, OCTO Technology"
__version__ = "1.1"
__email__ = "auma@octo.com"


def print_confusion_matrix(confusion_matrix, classes_list, normalize=True, figsize=(10, 7), fontsize=14, cmap="Blues"):
    """
    Display a pretty confusion matrix.

    Parameters
    ----------
    confusion_matrix : array-like

    classes_list : list,
        classes list of the confusion matrix

    normalize : boolean,
        normalize confusion matrix

    figsize : tuple, optional (default=(10,7))
        set the figure size

    fontsize : int, optional (default=14)
        set the font size

    cmap : str, optional (default="Blues")
        set the colormap

    Returns
    -------
    Confusion matrix figure


    Examples
    --------
    from bdacore.visualization.metrics import print_confusion_matrix
    array = [[ 8458,   227,  1730], \
             [ 1073, 37590,  1613], \
             [ 2390,  1159, 17540]]
    classes_list = ["A", "B", "C"]
    confusion_fig = print_confusion_matrix(array, classes_list)
   """
    fig = plt.figure(figsize=figsize)
    if normalize:
        normalized_cm = np.array(confusion_matrix).astype('float') / np.array(confusion_matrix).sum(axis=1)[:,
                                                                     np.newaxis]
        df_cm = pd.DataFrame(
            normalized_cm, index=classes_list, columns=classes_list,
        )
        heatmap = sns.heatmap(df_cm, annot=True, cmap=cmap)
    else:
        df_cm = pd.DataFrame(
            confusion_matrix, index=classes_list, columns=classes_list,
        )
        heatmap = sns.heatmap(df_cm, annot=True, fmt='d', cmap=cmap)
    heatmap.yaxis.set_ticklabels(heatmap.yaxis.get_ticklabels(), rotation=0, ha='right', fontsize=fontsize)
    heatmap.xaxis.set_ticklabels(heatmap.xaxis.get_ticklabels(), rotation=0, ha='right', fontsize=fontsize)
    plt.ylabel('True labels')
    plt.xlabel('Predicted labels')
    return fig
