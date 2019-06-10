from typing import Optional

import numpy as np
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA

from fabulus.unsup.spca import SPCA


def scree(X: np.ndarray, intersect: float = None, scale: bool = True, plot: bool = True,
          save: str = None, transparent: bool = True) -> Optional[int]:
    """
    Scree plot of ``X``

    :param X: data
    :param intersect: desired variance-ratio to be explained
    :param scale: standard-scale ``X`` before plotting
    :param plot: plotting the image
    :param save: path to save image; do not save iff ``None``
    :param transparent: transparency of plot
    :return: minimum components to explain ``intersect`` variance ratio
    """
    if not (0 <= intersect <= 1):
        raise ValueError(f'Intersect needs to be in [0, 1]: {intersect}')

    pca = SPCA().fit(X) if scale else PCA().fit(X)
    norm = pca.explained_variance_ratio_

    min_req = None
    if intersect:
        min_req = np.where(norm.cumsum() >= intersect)[0].min() + 1

    plt.figure(figsize=(10, 10))
    plt.title('Scree plot')
    plt.ylabel('Cumulative explained variance ratio')
    plt.xlabel('Principal component')
    plt.plot(norm)
    plt.plot(norm.cumsum())
    plt.hlines(intersect, xmin=0, xmax=len(norm) - 1, colors='k', linestyles='--', alpha=0.2)

    if intersect:
        plt.vlines(min_req, ymin=0, ymax=1, colors='r', linestyles='--', alpha=0.2)
        plt.legend(
            ['eigenvalues', 'cumulative eigenvalues',
             f'desired explained var-ratio: {intersect}',
             f'minimum components required: {min_req}'])
    else:
        plt.legend(
            ['eigenvalues', 'cumulative eigenvalues',
             f'desired explained var-ratio: {intersect}'])

    if save:
        plt.savefig(save, transparent=transparent)

    if plot:
        plt.show()
    else:
        plt.close()

    if intersect:
        return min_req
