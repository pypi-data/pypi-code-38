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

from unittest import TestCase, main
import pandas as pd
import numpy as np
import plotnine
from pyIMD.plotting.figures import plot_fitting, plot_response_shift, plot_mass, create_montage_array, \
    get_montage_array_size


class TestPlotting(TestCase):

    def testPlotMass(self):
        df = pd.DataFrame([[1, 2, 5], [4, 5, 5], [7, 8, 5]], columns=['Time', 'Mass', 'Mass rolling mean'])

        self.assertEqual(type(plot_mass(df, 1)), plotnine.ggplot)

    def testPlotFitting(self):
        df = pd.DataFrame([[1, 2], [4, 5], [7, 8]], columns=['Frequency', 'Phase'])

        resonance_frequency = 70
        parameter = [1, 2, 3]

        self.assertEqual(type(plot_fitting(df.iloc[:, 0], df.iloc[:, 1], resonance_frequency, parameter)),
                         plotnine.ggplot)

    def testPlotFrequencyShift(self):
        df_without = pd.DataFrame([[1, 2], [4, 5], [7, 8]], columns=['Frequency', 'Phase'])

        df_with = pd.DataFrame([[1, 2], [3, 2], [6, 9]], columns=['Frequency', 'Phase'])

        resonance_frequency_without = 70
        resonance_frequency_with = 68
        parameter_without = [1,2,3]
        parameter_with = [1, 2, 3]

        self.assertEqual(type(plot_response_shift(df_without.iloc[:, 0], df_without.iloc[:, 1],
                                                  resonance_frequency_without, parameter_without,
                                                   df_with.iloc[:, 0], df_with.iloc[:, 1],
                                                  resonance_frequency_with, parameter_with
                                                  )), plotnine.ggplot)

    def testCreateMontageArray(self):

        expected_result = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                                    [0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0],
                                    [0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0],
                                    [0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0],
                                    [0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0],
                                    [0, 0, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0],
                                    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
        image1 = np.zeros((7, 7), dtype=np.int)
        image1[1:6, 2:5] = 1
        image2 = np.zeros((7, 7), dtype=np.int)
        image2[1:6, 2:5] = 1

        image_array = []
        for iFile in [image1, image2]:
            image_array.append(iFile)
        image_stack = np.array(image_array)
        figure_rows = 1
        images_to_plot = 2

        size = np.array([figure_rows, np.nan])
        montage = create_montage_array(image_stack[0:images_to_plot, :, :], size)
        self.assertEqual(np.alltrue(montage == expected_result), True)

    def testGetMontageArraySize(self):

        expected_result = [1, 2]
        image1 = np.zeros((7, 7), dtype=np.int)
        image1[1:6, 2:5] = 1
        image2 = np.zeros((7, 7), dtype=np.int)
        image2[1:6, 2:5] = 1

        image_array = []
        for iFile in [image1, image2]:
            image_array.append(iFile)
        image_stack = np.array(image_array)
        figure_rows = 1

        image_row_count = image_stack.shape[1]
        image_col_count = image_stack.shape[2]
        frame_count = image_stack.shape[0]
        size = np.array([figure_rows, np.nan])

        montage_size = get_montage_array_size(size, image_row_count, image_col_count, frame_count)

        self.assertEqual(len(montage_size), 2)
        self.assertEqual(montage_size[0], expected_result[0])
        self.assertEqual(montage_size[1], expected_result[1])


if __name__ == "__main__":
    main()
