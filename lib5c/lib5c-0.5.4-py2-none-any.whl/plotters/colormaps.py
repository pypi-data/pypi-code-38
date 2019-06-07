"""
Module for resolving string identifiers to matplotlib colormaps.
"""

import matplotlib as mpl
import matplotlib.pyplot as plt


def get_colormap(name, reverse=False, set_bad=None):
    """
    Get a colormap given its name.

    Parameters
    ----------
    name : str
        The name of the colormap. See the Notes for special values.
    reverse : bool
        Pass True to reverse the colormap.
    set_bad : str, optional
        Color to set as the ``set_bad`` color on the returned colormap. This is
        commonly used to represent NaN or undefined values.

    Returns
    -------
    matplotlib.colors.Colormap
        The requested colormap.

    Notes
    -----
    If ``name`` matches a built-in matplotlib colormap, that colormap will be
    returned. If ``name`` matches one of the following special values, the
    corresponding specialized colomap will be returned:

        * 'obs_over_exp': a colormap for visualizing fold changes in interaction
          frequencies
        * 'is': a colormap for plotting interaction score heatmaps
        * 'obs': a colormap for visualizing observed interaction frequencies
        * 'bias': a colormap for plotting bias factor heatmaps

    You can append '_bad_<color>' to any of these to set the set_bad color, for
    example: 'abs_obs_bad_green'
    """
    # resolve <name>_bad_<color> formatted names
    if '_bad_' in name:
        name, set_bad = name.split('_bad_')

    # get base colormap
    if name == 'obs_over_exp':
        cmap = mpl.colors.LinearSegmentedColormap.from_list(
            'pvalue_obs_over_exp', colors=['darkblue', 'blue', 'lightblue',
                                           'white', 'white', 'white', 'white',
                                           'white', 'white', 'orange', 'red',
                                           'black'])
    elif name == 'red7':
        cmap = mpl.colors.LinearSegmentedColormap.from_list(
            'red7', colors=['white', '#fee5d9', '#fdc7b2', '#fca486', '#fc7f5f',
                            '#f6583e', '#e43027', '#c3161b', '#9d0d14',
                            '#67000d', 'black'])
    elif name == 'red8':
        cmap = mpl.colors.LinearSegmentedColormap.from_list(
            'red8', colors=['white', 'white', '#fee5d9', '#fdc7b2', '#fca486',
                            '#fc7f5f', '#f6583e', '#e43027', '#c3161b',
                            '#9d0d14', '#67000d', 'black'])
    elif name == 'is':
        cmap = mpl.colors.LinearSegmentedColormap.from_list(
            'interaction_score', colors=['#0049e6', '#4d85ff', 'lightblue',
                                         'white', 'white', 'white', 'white',
                                         'white', 'white', 'white', 'orange',
                                         'red', 'red', 'darkred', 'black'])
    elif name == 'obs':
        cmap = mpl.colors.LinearSegmentedColormap.from_list(
            'pvalue_obs', colors=['#666666', '#767676', '#858585', '#959595',
                                  '#A4A4A4', '#B4B4B4', '#C3C3C3', '#D3D3D3',
                                  '#E3E3E3', 'orange', '#e60000', 'black'])
    elif name == 'abs_obs':
        cmap = mpl.colors.LinearSegmentedColormap.from_list(
            'abs_obs', colors=['#666666', '#797979', '#858585', '#a6a6a6',
                               '#d9d9d9', 'white', '#ffb833', 'red', 'black'])
    elif name == 'bworb':
        cmap = mpl.colors.LinearSegmentedColormap.from_list(
            'buworb', colors=['#666666', '#797979', '#858585', '#a6a6a6',
                              '#d9d9d9', 'white', '#ffb833', 'red', 'black'])
    elif name == 'tetris':
        cmap = mpl.colors.LinearSegmentedColormap.from_list(
            'tetris', colors=['#333333', '#333333'])
    elif name == 'tnr':
        cmap = mpl.colors.LinearSegmentedColormap.from_list(
            'tnr', colors=['0.2', '0.4', '0.6', '0.8', 'white',
                           '#f97306', '#fd3c06', '#980002', 'black'])
    elif name == 'bias':
        cmap = mpl.colors.LinearSegmentedColormap.from_list(
            'bias', colors=['darkblue', 'mediumblue', 'deepskyblue', 'white',
                            'orange', 'orangered', 'red'])
    elif name == 'pvalue':
        cmap = mpl.colors.LinearSegmentedColormap.from_list(
            'pvalue', colors=['#000000', '#ff0000', '#ff0000', '#bfbf00',
                              '#bfbf00', '#bfbf00'] + list('w'*100)[::-1])
    else:
        cmap = plt.cm.get_cmap(name)

    # reverse colormap
    if reverse:
        cmap._segmentdata = plt.cm.revcmap(cmap._segmentdata)

    # set under
    if set_bad:
        cmap.set_bad(set_bad)

    return cmap
