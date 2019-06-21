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

import os
from pandas import DataFrame
from tqdm import trange
from pyIMD.error.error_handler import ArgumentError
from pyIMD.io.read_from_disk import read_from_dat

__author__ = 'Andreas P. Cuny'


def write_to_png(plot_object, file, **kwargs):
    """
    Method to write figures in png format to current directory

    Args:
        plot_object (`ggplot obj`):   ggplot object
        file (`str`):                 File path + file name of the figure to save

    Keyword Args:
         width (`int`):               Figure width (optional)
         height (`int`):              Figure height (optional)
         units (`str`):               Figure units (optional) 'in', 'mm' or 'cm'
         resolution (`int`):          Figure resolution in dots per inch [dpi] (optional)

    Returns:
           png file (`void`):         Writes figure to disk as png
    """
    if 'width' and 'height' and 'units' and 'resolution' in kwargs:
        width = kwargs.get('width')
        height = kwargs.get('height')
        units = kwargs.get('units')
        resolution = kwargs.get('resolution')
        plot_object.save(filename='{}.png'.format(file), width=width, height=height, units=units, dpi=resolution)
    elif not kwargs:
        plot_object.save(filename='{}.png'.format(file))
    else:
        raise ArgumentError(write_to_png.__doc__)


def write_to_pdf(plot_object, file, **kwargs):
    """
    Method to write figures in pdf format to current directory

    Args:
        plot_object (`ggplot object`):  ggplot object
        file (`str`):                   File path + file name of figure to save

    Keyword Args:
         width (`int`):                 Figure width (optional)
         height (`int`):                Figure height (optional)
         units ('str`):                 Figure units (optional) 'in', 'mm' or 'cm'
         resolution (`int`):            Figure resolution in dots per inch [dpi] (optional)

    Returns:
          pdf file (`void`):            Writes figure to disk as pdf

    """
    if 'width' and 'height' and 'units' and 'resolution' in kwargs:
        width = kwargs.get('width')
        height = kwargs.get('height')
        units = kwargs.get('units')
        resolution = kwargs.get('resolution')
        plot_object.save(filename='{}.pdf'.format(file), width=width, height=height, units=units, dpi=resolution)
    elif not kwargs:
        plot_object.save(filename='{}.pdf'.format(file))
    else:
        raise ArgumentError(write_to_pdf.__doc__)


def write_to_disk_as(file_format, plot_object, file, **kwargs):
    """
    Method to write figures in various file formats

    Args:
        file_format (`str`):            File format identifier i.e. png or pdf
        plot_object (`ggplot object`):  ggplot object
        file (`str`):                   File path + file name of the figure to save

    Keyword Args:
         width (`int`):                 Figure width (optional)
         height (`int`):                Figure height (optional)
         units ('str`):                 Figure units (optional) 'in', 'mm' or 'cm'
         resolution (`int`):            Figure resolution in dots per inch [dpi] (optional)

    Returns:
          file (`void`):                Writes figure to disk in the respective file format

    """
    if file_format == 'pdf':
        write_to_pdf(plot_object, file, **kwargs)
    elif file_format == 'png':
        write_to_png(plot_object, file, **kwargs)
    else:
        raise Exception("This figure format is currently not supported.")


def write_concat_data(directory, delimiter, time_interval):
    """
    Method to write concatenate data from single dat files (i.e data logger from Nanonis software).

    Args:
        directory (`str`):                Directory containing files to concatenate.
        delimiter (`str`):                Delimiter to be used in the data file to separate columns.
        time_interval (`int`):            Measurement time interval in milliseconds.

    Returns:
          file (`void`):                  Writes concatenated data to single .csv file.

    """
    files = os.listdir(directory)
    appended_data = DataFrame()
    for iFile in trange(0, len(files)):
        data = read_from_dat(directory + os.sep + files[iFile], delimiter=delimiter)
        appended_data = appended_data.append(DataFrame(data=data), ignore_index=True)

    time = [x * time_interval for x in range(0, appended_data.shape[0])]
    appended_data['Time (ms)'] = time
    appended_data = appended_data.iloc[:, ::-1]
    appended_data.to_csv(directory + os.sep + 'DataLoggerConCat.csv', sep='\t', index=False, header=False)
