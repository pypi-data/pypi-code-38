# /********************************************************************************
# * Copyright © 2018-2019, ETH Zurich, D-BSSE, Andreas P. Cuny & Gotthold Fläschner
# * All rights reserved. This program and the accompanying materials
# * are made available under the terms of the GNU Public License v3.0
# * which accompanies this distribution, and is available at
# * http://www.gnu.org/licenses/gpl
# *
# * Contributors:
# *     Andreas P. Cuny - initial API and implementation
# *******************************************************************************/

import math
import warnings
import numpy as np
from pandas import concat, melt
from pyIMD.analysis.curve_fit import fit_function
from plotnine import ggplot, aes, geom_line, geom_point, theme_bw, labs, xlab, ylab, theme, theme_seaborn, \
    element_line, element_rect

__author__ = 'Andreas P. Cuny'

warnings.filterwarnings("ignore")


def plot_fitting(x, y, resonance_frequency, parameter):
    """ Plots the phase response and the corresponding fit of the harmonic damped oscillator.

    Args:
        x (`float array`):                       X coordinates (frequency in kHz)
        y (`float array`):                       Y coordinates (phase in radians)
        resonance_frequency (`float array`):     Resonance frequency given by the fit of x and y
        parameter (`float array`):               Others parameters of function fit (Q factor, offset, linear background)

    Returns:
        p (`ggplot object`):                     Returns a ggplot object
    """

    y_fit = fit_function(x, resonance_frequency, parameter[0], parameter[1], parameter[2])
    y_fit.name = 'Phase fit'
    x.name = 'Frequency (kHz)'
    y.name = 'Phase (rad)'
    data = concat([x, y, y_fit], axis=1)
    col_names = list(data)

    # Plot data
    p = ggplot(aes(x=col_names[0], y=col_names[1]), data=data) + \
        geom_point() + \
        geom_line(aes(x=col_names[0], y=col_names[2]),  color='red', size=0.5) + \
        theme_seaborn(style='ticks', context='talk', font_scale=0.75) + \
        theme(figure_size=(15, 7), strip_background=element_rect(fill='white'), axis_line_x=element_line(color='black'),
              axis_line_y=element_line(color='black'), legend_key=element_rect(fill='white', color='white'))
    return p


def plot_response_shift(x, y, resonance_frequency_without, parameter_without, xx, yy, resonance_frequency_with,
                        parameter):
    """ Plots the phase response of pre start data without and with cell attached to cantilever with the
    respective function fit.

    Args:
        x (`float array`):                               X coordinates w/o cell (frequency in kHz)
        y (`float array`):                               Y coordinates w/o cell (phase in radians)
        xx (`float array`):                              X coordinates w/ cell(frequency in kHz)
        yy (`float array`):                              Y coordinates w/ cell (phase in radians)
        resonance_frequency_without (`float array`):     Resonance frequency given by the fit of x and y  w/o cell
        resonance_frequency_with (`float array`):        Resonance frequency given by the fit of x and y w/ cell
        parameter (`float array`):                       Others parameters of function fit (Q factor, offset, linear
                                                         background) w/o cell
        parameter_without (`float array`):               Others parameters of function fit (Q factor, offset, linear
                                                         background) w/ cell

    Returns:
        p (`ggplot object`):                             Returns a ggplot object
    """

    y_fit_without = fit_function(x, resonance_frequency_without, parameter_without[0], parameter_without[1],
                                 parameter_without[2])
    y_fit_with = fit_function(xx, resonance_frequency_with, parameter[0], parameter[1], parameter[2])
    y_fit_without.name = 'Phase fit w/o cell att.'
    y_fit_with.name = 'Phase fit w cell att.'
    x.name = 'Frequency without (kHz)'
    y.name = 'Raw phase w/o cell att.'
    xx.name = 'Frequency with (kHz)'
    yy.name = 'Raw phase w cell att.'
    data = concat([x, y, y_fit_without, xx, yy, y_fit_with], axis=1)
    df = melt(data, id_vars=['Frequency with (kHz)'], value_vars=['Phase fit w cell att.',
                                                                  'Phase fit w/o cell att.'])
    df.loc[df['variable'] == 'Phase fit w/o cell att.', 'Frequency with (kHz)'] = x.values
    df2 = melt(data, id_vars=['Frequency with (kHz)'], value_vars=['Raw phase w cell att.',
                                                                   'Raw phase w/o cell att.'])
    df2.loc[df2['variable'] == 'Raw phase w/o cell att.', 'Frequency with (kHz)'] = x.values
    # Plot data
    p = ggplot(data=df) + \
        geom_point(aes(x="Frequency with (kHz)", y='value', fill='variable'), data=df2, alpha=0.6) + \
        geom_line(aes(x="Frequency with (kHz)", y='value', color='variable')) + \
        xlab('Frequency (kHz)') + \
        ylab('Phase (rad)') + \
        labs(fill='Raw data', color='Function fits') + \
        theme_seaborn(style='ticks', context='talk', font_scale=0.75) + \
        theme(figure_size=(15, 7), strip_background=element_rect(fill='white'), axis_line_x=element_line(color='black'),
              axis_line_y=element_line(color='black'), legend_key=element_rect(fill='white', color='white'))
    return p


def plot_mass(calculated_cell_mass, plot_every_nth_point):
    """ Plots the resulting mass

    Args:
        calculated_cell_mass (`pandas data frame`):  Pandas data frame [Nx3] with time and calculated cell mass and
                                                     rolling mean averaged cell mass
        plot_every_nth_point (`int`):                If 1 all data points are plotted. Otherwise every nth data point is
                                                     used for plotting.

    Returns:
        p (`ggplot object`):                         Returns a ggplot plot object

    """

    col_names = list(calculated_cell_mass)
    col_names[0] = 'Time (h)'
    calculated_cell_mass.columns = col_names
    calculated_cell_mass = calculated_cell_mass.iloc[::plot_every_nth_point, :]

    # Plot data
    p = ggplot(aes(x=col_names[0], y=col_names[1]), data=calculated_cell_mass) + \
        geom_point(alpha=0.1) + \
        geom_line(aes(y=col_names[2]), color='red') + \
        theme_bw()
    return p


def get_montage_array_size(size, image_row_count, image_col_count, frame_count):
    """ Calculates the final size of a numpy array needed to hold a the number of specified image frames given the \
    row and column count of the final array.

    Args:
        size (`numpy array`):           Array specifying the amount of images displayed in the montage per row and \
                                        column. If one argument is replaced with np.nan, the needed amount of rows or \
                                        columns is calculated automatically. E. g. [5, np.nan]
        image_row_count (`int`):        Number of rows per image
        image_col_count (`int`):        Number of columns per image
        frame_count (`int`):            Number of image frames in the stack

    Returns:
        montage_size (`numpy array`):   Array with the number of rows and columns needed in the montage array for the \
                                        images
    """

    if len(size) == 0 or np.isnan(size).all():
        col = math.sqrt(image_row_count * frame_count / image_col_count)

        col = math.ceil(col)
        row = math.ceil(frame_count / col)
        montage_size = [row, col]

    elif any(np.isnan(size)):
        montage_size = size
        nan_idx = np.isnan(size)
        montage_size[nan_idx] = np.ceil(frame_count / size[~nan_idx])

    elif size[0] * size[1] < frame_count:
        return

    else:
        montage_size = size

    return montage_size


def create_montage_array(img_stack, size):
    """
    Creates an image montage of a 3D numpy array with the shape [image frames, image row, image col] for the specified
    size.

    Args:
        img_stack (`3D numpy array`):       3D numpy image array [image row, image col, image frames].
        size (`numpy array`):               Array specifying the amount of images displayed in the montage per row and \
                                            column. If one argument is replaced with np.nan, the needed amount of rows \
                                            or columns is calculated automatically. E. g. [5, np.nan]

    Returns:
        montage (`2D numpy array`):         2D numpy array with the image montage
    """

    image_row_count = img_stack.shape[1]
    image_col_count = img_stack.shape[2]
    frame_count = img_stack.shape[0]

    montage_size = get_montage_array_size(size, image_row_count, image_col_count, frame_count)

    montage_size = list(np.int_(montage_size))
    montage_row_count = montage_size[0]
    montage_col_count = montage_size[1]

    montage_image_size = [montage_row_count * image_row_count, montage_col_count * image_col_count]

    montage_image_size = list(np.int_(montage_image_size))
    montage = np.zeros(montage_image_size)

    rows = list(range(0, image_row_count))
    cols = list(range(0, image_col_count))
    i_frame = 0

    for i in range(0, montage_row_count):
        for j in range(0, montage_col_count):
            if i_frame < frame_count:
                r = list(np.asarray(rows) + i * image_row_count)
                c = list(np.asarray(cols) + j * image_col_count)
                montage[np.ix_(r, c)] = img_stack[i_frame, :, :]

            else:
                montage = montage
            i_frame = i_frame + 1

    return montage
