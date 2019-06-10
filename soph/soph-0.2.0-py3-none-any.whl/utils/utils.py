import hashlib
import inspect
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn import metrics

from pylint import epylint as lint


def pylint(code, print_pylint=True, print_code=False):
    """
    convenience function to lint code.
    
    INPUTS
        code: Can be one of
            - python callable. in this case the inspect module will be used to recover source code. Note that a boilerplate module docstring will be added.
            - string. in this case the function assumes that the string is the source code to be analyzed.
        print_pylint: by default, pylint output will be printed. suppress by setting this argument to false.
    
    OUTPUTS
        rating:
            - float, pylint code rating
    
    """

    module_docstring = """\"\"\"This is just a general module docstring
\"\"\"\n\n"""

    if callable(code):

        code_str = module_docstring + inspect.getsource(code).strip() + "\n"
        cmd_arg = " --msg-template='" + code.__name__ + ":{line}:{column}: {msg_id}: {msg} ({symbol}) http://pylint-messages.wikidot.com/messages:{msg_id}'"
    else:
        code_str = code
        cmd_arg = " --msg-template='{line}:{column}: {msg_id}: {msg} ({symbol}) http://pylint-messages.wikidot.com/messages:{msg_id}'"

    if print_code:
        print(code_str)

    code_file = Path(tempfile.NamedTemporaryFile(delete=False).name)
    code_file.write_text(code_str)

    (pylint_stdout,
     pylint_stderr) = lint.py_run(str(code_file) + cmd_arg, return_std=True)

    code_file.unlink()

    stdout = pylint_stdout.read()

    if print_pylint:
        print(stdout)

    rating_str = stdout.split("Your code has been rated at ")[-1]
    rating = float(rating_str[:-7])

    return rating


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
