"""
Module for visualizing spline surfaces fit to 5C counts data.
"""
import warnings

import numpy as np

from lib5c.algorithms.expected import make_poly_log_log_fragment_expected_matrix
from lib5c.util.counts import parallel_divide_counts


def visualize_spline(counts_list, primermap, bias_factor, spline,
                     grid_points=10, sample_rate=100, log=True,
                     asymmetric=False):
    """
    Open an interactive pyplot window showing a visualization of a spline
    surface, overlayed over representative 5C counts data.

    Parameters
    ----------
    counts_list : List[Dict[str, np.ndarray]]
        A list of counts dicts to use as data points to be compared to the
        spline surface.
    primermap : Dict[str, List[Dict[str, Any]]]
        The primermap corresponding to the counts dicts in ``counts_list``.
    bias_factor : str
        The bias factor being plotted. This string must match metadata keys in
        ``primermap``. That is to say, if ``bias_list`` is ``['length']`` then
        we expect ``primermap[region][i]['length']`` to be a number representing
        the length of the ``i`` th fragment in the region specified by
        ``region``.
    spline : scipy.interpolate.BivariateSpline
        The spline object to visualize.
    grid_points : int
        The number of grid points to use when constructing the wireframe of the
        surface represented by ``spline``.
    sample_rate : int
        Only every ``sample_rate`` th real-data point will be included in the
        visualization to reduce computational load.
    log : bool
        Pass True to show counts on a log-scale axis.
    asymmetric : bool
        Pass True to iterate only over the upper-triangular elements of the
        counts matrices, which can lead to asymmetric visualizations. By
        default, the algorithm iterates over all elements of the counts
        matrices, enforcing symmetry in thevisualizations but incurring some
        redundancy in the actual counts information.

    Notes
    -----
    The spline will be displayed in an interactive window via ``plt.show()``. If
    your default matplotlib backend is not interactive, this function will try
    to set your backend to TkAgg. If you prefer to use a different interactive
    backend, set the ``MPLBACKEND`` environment variable before invoking Python.
    """
    # interactive backend shenanigans
    import matplotlib as mpl
    if mpl.get_backend().lower() not in [x.lower()
                                         for x in mpl.rcsetup.interactive_bk]:
        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            try:
                mpl.use('TkAgg')
            except UserWarning:
                import matplotlib.pyplot as plt
                plt.switch_backend('TkAgg')
    from mpl_toolkits.mplot3d import axes3d  # noqa: F401
    import matplotlib.pyplot as plt

    # deduce regions
    regions = counts_list[0].keys()

    # compute distance dependence
    distance_dependences = [make_poly_log_log_fragment_expected_matrix(
        counts, primermap) for counts in counts_list]

    # divide by distance dependence
    counts_list = [
        parallel_divide_counts(counts_list[k], distance_dependences[k])
        for k in range(len(counts_list))]

    # construct arrays of actual data
    x = []
    y = []
    z = []
    for counts in counts_list:
        for region in regions:
            for i in range(len(counts[region])):
                if asymmetric:
                    jrange = range(i + 1)
                else:
                    jrange = range(len(counts[region]))
                for j in jrange:
                    if np.isfinite(counts[region][i, j]):
                        x.append(primermap[region][i][bias_factor])
                        y.append(primermap[region][j][bias_factor])
                        if log:
                            z.append(np.log(counts[region][i, j] + 1))
                        else:
                            z.append(counts[region][i, j])

    # construct arrays of values from spline
    x_grid = np.linspace(min(x), max(x), grid_points)
    y_grid = np.linspace(min(y), max(y), grid_points)
    x_spline = np.zeros([len(x_grid), len(y_grid)])
    y_spline = np.zeros([len(x_grid), len(y_grid)])
    z_spline = np.zeros([len(x_grid), len(y_grid)])
    for i in range(len(x_grid)):
        for j in range(len(y_grid)):
            x_spline[i, j] = x_grid[i]
            y_spline[i, j] = y_grid[j]
            z_spline[i, j] = spline.ev(x_grid[i], y_grid[j])

    # plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(x[::sample_rate], y[::sample_rate], z[::sample_rate])
    ax.plot_wireframe(x_spline, y_spline, z_spline, rstride=1, cstride=1)
    ax.set_zlim([0, max(z)])

    plt.show()
