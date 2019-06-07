import numpy as np
from sklearn.decomposition import PCA, KernelPCA, FastICA, FactorAnalysis
from sklearn.manifold import MDS
from sklearn.preprocessing import scale

from lib5c.util.counts_superdict import counts_superdict_to_matrix
from lib5c.algorithms.correlation import \
    make_pairwise_correlation_matrix_from_counts_matrix


def compute_pca_from_counts_superdict(counts_superdict, rep_order=None,
                                      **kwargs):
    """
    Convenience function for performing PCA on a counts superdict data
    structure.

    Parameters
    ----------
    counts_superdict : Dict[str, Dict[str, np.ndarray]]
        The counts superdict structure to compute PCA on.
    rep_order : Optional[List[str]]
        The order in which the replicates in ``counts_superdict`` should be
        considered when filling in the rows of the design matrix.
    kwargs : Dict[str, Any]
        Additional kwargs to be passed to ``compute_pca()``.

    Returns
    -------
    Tuple[np.ndarray]
        The first element is the matrix of PCA-projected replicates. The second
        element is the PVE for each component, or None if the PCA method
        selected doesn't provide a PVE estimate. The third element is a matrix
        of the principle component vectors, or None if the PCA method selected
        doesn't provide a set of principle component vectors.
    """
    matrix = counts_superdict_to_matrix(counts_superdict, rep_order=rep_order,
                                        discard_nan=True)
    return compute_pca(matrix, **kwargs)


def compute_pca(matrix, scaled=True, logged=False, kernel=None,
                kernel_kwargs=None, variant='pca', pf=1):
    """
    Performs PCA on a matrix.

    Parameters
    ----------
    matrix : np.ndarray
        The design matrix, whose rows are observations (replicates) and whose
        columns are features (interaction values at each position).
    scaled : bool
        Pass True to scale the features to unit variance.
    logged : bool
        Pass True to log the features before PCA.
    kernel : Optional[str]
        Pass a kernel accepted by ``sklearn.decomposition.KernelPCA()`` to
        perform KPCA.
    kernel_kwargs : Optional[Dict[str, Any]]
        Kwargs to use for the kernel.
    variant : {'pca', 'ica', 'fa', 'mds'}
        Select which variant of PCA to use.
    pf : int
        Specify an integer number of pure polynomial features to use in the PCA.

    Returns
    -------
     Tuple[np.ndarray]
        The first element is the matrix of PCA-projected replicates. The second
        element is the PVE for each component, or None if the PCA method
        selected doesn't provide a PVE estimate. The third element is a matrix
        of the principle component vectors, or None if the PCA method selected
        doesn't provide a set of principle component vectors.
    """
    # adjust matrix
    if variant != 'pca':
        matrix = matrix[:, ~np.all(matrix == matrix[0], axis=0)]
    if pf != 1:
        matrix = np.concatenate([np.power(matrix, p)
                                 for p in range(1, pf + 1)], axis=1)
    if logged:
        matrix = np.log2(matrix + 1)
    if scaled:
        matrix = scale(matrix)

    if variant == 'pca':
        print 'performing pca'
        if kernel is not None:
            default_kernel_kwargs = {'degree': 3,
                                     'gamma': 1.0 / matrix.shape[1],
                                     'coef0': 0 if kernel == 'sigmoid' else 1}
            if kernel_kwargs is None:
                kernel_kwargs = {}
            default_kernel_kwargs.update(kernel_kwargs)
            kernel_kwargs = default_kernel_kwargs
            kernel_kwargs['n_components'] = len(matrix)
            kernel_kwargs['kernel'] = kernel
            pca_object = KernelPCA(**kernel_kwargs)
            proj = pca_object.fit(matrix).transform(matrix)
            pve = None
            pcs = pca_object.alphas_
        else:
            pca_object = PCA()
            proj = pca_object.fit(matrix).transform(matrix)
            pve = pca_object.explained_variance_ratio_
            pcs = pca_object.components_
    elif variant == 'ica':
        print 'performing ica'
        ica_object = FastICA()
        proj = ica_object.fit(matrix).transform(matrix)
        pve = None
        pcs = ica_object.components_
    elif variant == 'fa':
        print 'performing factor analysis'
        fa_object = FactorAnalysis(n_components=len(matrix),
                                   svd_method='lapack')
        proj = fa_object.fit(matrix).transform(matrix)
        pve = None
        pcs = fa_object.components_
    elif variant == 'mds':
        print 'performing multidimensional scaling'
        dissimilarity = 1 - make_pairwise_correlation_matrix_from_counts_matrix(
            matrix)
        mds_object = MDS(dissimilarity='precomputed')
        proj = mds_object.fit_transform(dissimilarity)
        pve = None
        pcs = None
    else:
        raise ValueError('variant %s not supported' % variant)

    return proj, pve, pcs
