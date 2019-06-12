def plot_confusion_matrix(cm,
                          labels,
                          title='Confusion matrix',
                          cmap=None,
                          norm=False):
    """
    given a sklearn confusion matrix (cm), create a matplotlib figure

    Arguments
    ---------
    cm:           confusion matrix from sklearn.metrics.confusion_matrix

    labels:       given classification classes such as [0, 1, 2]
                  the class names, for example: ['high', 'medium', 'low']

    title:        the text to display at the top of the matrix

    cmap:         the gradient of the values displayed from matplotlib.pyplot.cm
                  see http://matplotlib.org/examples/color/colormaps_reference.html
                  plt.get_cmap('jet') or plt.cm.Blues

    norm:         If False, plot the raw numbers
                  If True, plot the proportions

    Usage
    -----
    plot_confusion_matrix(cm     = cm,                  # confusion matrix created by
                                                        # sklearn.metrics.confusion_matrix
                          norm   = True,                # show proportions
                          labels = y_labels_vals,       # list of names of the classes
                          title  = best_estimator_name) # title of graph

    Citiation
    ---------
    http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html
    https://www.kaggle.com/grfiv4/plot-a-confusion-matrix

    """
    from matplotlib import colorbar, rcParams
    import matplotlib.pyplot as plt
    import numpy as np
    import itertools

    # Set font params
    rcParams['font.size'] = 20
    rcParams['font.weight'] = 'normal'

    # Calculate accuracy and max value
    accuracy = np.trace(cm) / float(np.sum(cm))
    maximum = 1 if norm else cm.max()

    # Set default colourmap (purple is nice)
    if cmap is None:
        cmap = plt.get_cmap('Purples')

    # Normalise values
    norm_cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    # Create figure
    fig, ax = plt.subplots(figsize=(8, 7))
    im = plt.imshow(norm_cm, interpolation='nearest', cmap=cmap, aspect='auto')
    plt.title(title, fontweight='bold')
    pos = ax.get_position()

    # Add values to figure
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        color = 'white' if cm[i, j] > cm[i].sum() / 2 else 'black'
        text = f"{norm_cm[i,j]:0.4f}" if norm else f"{cm[i,j]:0.0f}"
        plt.text(j, i, text, horizontalalignment='center', va='center', color=color, fontsize=25)
        ax.axhline(i-.5, color='black', linewidth=1.5)
        ax.axvline(j-.5, color='black', linewidth=1.5)

    # Add primary axes
    tick_marks = np.arange(len(labels))

    ax.tick_params(
        axis='both',
        which='both',
        labeltop=False,
        labelbottom=False,
        length=0)
    ax.set_ylabel(f'True\n')
    ax.set_yticks(tick_marks)
    ax.set_yticklabels(labels)
    ax.set_xticks(tick_marks)
    ax.set_xlabel(f'\nOverall Accuracy={accuracy:0.4f}')
    ax.tick_params(axis='both', which='both', pad=15)
    ax.tick_params(axis='y', which='minor', labelrotation=90)

    # Add secondary axes displaying at top of figure
    ax2 = ax.twiny()
    ax2.tick_params(
        axis='both',
        which='both',
        labelbottom=False,
        length=0)
    ax2.tick_params(axis='both', which='both', pad=15)
    ax2.set_xticks(tick_marks)
    ax2.set_xlim(ax.get_xlim())

    ax.autoscale(False)
    ax2.autoscale(False)

    ax2.set_xlabel('\nPredicted\n')
    ax2.set_xticklabels(labels)

    # Add colourbar
    cbax = fig.add_axes([pos.x0+pos.width+.15, pos.y0, 0.08, pos.height])
    cb = colorbar.ColorbarBase(cbax, cmap=cmap, orientation='vertical')
    cb.set_label('Accuracy per label')

    plt.show()

if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt

    cm = np.array([[293, 78, 94], [60, 265, 141], [59, 205, 201]])
    labels = ['Label1', 'Label2', 'Label3']
    title = "Example Confusion Matrix"

    plot_confusion_matrix(cm=cm, title=title, labels=labels)
    plot_confusion_matrix(cm=cm, title=title, labels=labels, norm=True)
