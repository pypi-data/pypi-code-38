"""
Module containing useful colorscales with which to plot 5C heatmaps.

These colormaps are deprecated in favor of the colormap interface provided by
``lib5c.plotters.colormaps.get_colormap()``.
"""

import matplotlib as mpl

obs_colorscale = mpl.colors.LinearSegmentedColormap.from_list(
    'buworb',
    colors=['#666666', 'lightgrey', 'white', 'orange', 'red', 'darkred',
            'black'])
obs_colorscale.set_under('#333333')

obs_over_exp_colorscale = mpl.colors.LinearSegmentedColormap.from_list(
    'buworb',
    colors=['darkblue', 'darkblue', 'blue', 'lightblue', 'white', 'white',
            'orange', 'red', 'darkred', 'black'])
obs_over_exp_colorscale.set_under('#333333')

thresholded_v1_colorscale = mpl.colors.LinearSegmentedColormap.from_list(
    'buworb',
    colors=['#666666', 'darkblue', 'blue', 'lightblue', 'white', 'white',
            'orange', 'red', 'darkred', 'black'])
thresholded_v1_colorscale.set_under('#333333')

thresholded_v2_colorscale = mpl.colors.LinearSegmentedColormap.from_list(
    'buworb',
    colors=['#666666', 'orange', 'red', 'darkred', 'black'])
thresholded_v2_colorscale.set_under('#333333')
