import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn import metrics
import hashlib


def hash(answer):
    """
    Compares an answer to a given hash according to https://github.com/davidcorbin/euler-offline
    """
    return hashlib.md5(bytes(str(answer), 'ascii')).hexdigest()


def imshow(im, ax=None):

    if ax is None:
        ax = plt.gca()

    # scale
    im_min = np.min(im)
    im_max = np.max(im)
    im_scale = im_max - im_min
    if im_scale == 0:
        im_scale = 1
    im = (im - im_min) / im_scale

    cmap = "gray"

    if len(im.shape) == 3:

        # for grayscale (single color channel)
        if im.shape[2] == 1:
            im = np.squeeze(im)

        else:
            assert (im.shape[2] == 3
                    ), "image should have either 0, 1, or 3 color channels"
            cmap = None

    ax.imshow(im, cmap=cmap)
    ax.axis(False)


def plot_decision_boundary(pred_func, x, y, ax=None, points=1e3,
                           pal=dict(enumerate(sns.color_palette("husl", 4))),
                           margin_func=None, alpha=.1):
    """Plots the decision boundary for a function that generates a prediction.

    Args:
        pred_func (function): Function that returns integer category labels for `x`.
        x (array): [2 x n] array.
        y (array): any-dimensional array (will be flattened)
        ax (axis): matplotlib axis. None generates our own.
        points (floatlike): number of points we wish to generate
        pal: pallete of colors for each class label
        margin_func: optional function for generating margins (drawn at margin = ±1)
        alpha: transparency of scatterplot points

    Returns:
        None
    """
    if ax is None:
        fig, ax = plt.subplots()

    y_pred = pred_func(x)
    score = metrics.accuracy_score(y_pred.flatten(), y.flatten())

    sns.scatterplot(x=x[:, 0], y=x[:, 1], hue=y, alpha=alpha, edgecolor=None,
                    palette=pal, ax=ax)

    side_pts = int(np.sqrt(points))

    x0_min, x0_max = ax.get_xlim()
    x1_min, x1_max = ax.get_ylim()
    xx, yy = np.meshgrid(np.linspace(x0_min, x0_max, num=side_pts),
                         np.linspace(x1_min, x1_max, num=side_pts))

    Z = pred_func(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)

    ax.text((x0_min + x0_max) / 2, x1_min + (x1_max - x1_min) * .1,
            f"acc: {score:.1%}", bbox=dict(boxstyle="round", fc="white",
                                           ec="black"))

    ax.contourf(xx, yy, Z, alpha=0.2, colors=list(pal.values()), zorder=-1)

    if not (margin_func is None):
        Z = margin_func(np.c_[xx.ravel(), yy.ravel()]).reshape(xx.shape)

        # plot decision boundary and margins
        ax.contour(xx, yy, Z, colors='k', levels=[-1, 1], alpha=0.5,
                   linestyles=['--', '--'], zorder=0)
