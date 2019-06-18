"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import numpy
import pandas as pd
from PyQt5 import QtWidgets

from pyjamas.rimage.rimutils import rimutils
from pyjamas.rutils import RUtils
import pyjamas.dialogs.measurepoly as measurepoly
import pyjamas.rannotations.rpolyline as rpolyline
from pyjamas.rcallbacks.rcallback import RCallback


class RCBMeasurePoly(RCallback):
    def cbMeasurePoly(self, firstSlice: int = None, lastSlice: int = None, measurements: dict = None, filename: str = None) -> dict:
        '''
                Measures a set of polygons.
                first_slice and last_slice are slice numbers (start at 1), not indeces (start at zero).
                measurements is a dictionary of the form {'area': True|False, 'perimeter': True|False, 'pixels': True
                |False, 'image': True|False}.
                The function has a number of parameters that can be used to call it from a script.
                :return: Dictionary with measurement results? Does skimage.measure have a measurement structure. Define
                measurement class?
        '''

        theresults = {}

        # Create and open dialog for measuring polygons.
        if filename == '' or filename is False or filename is False or \
                firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None:
            # Create a measurement dialog that allows input of all this at once (unless all the parameters are given as arguments).
            dialog = QtWidgets.QDialog()
            ui = measurepoly.MeasurePolyDialog()

            firstSlice = self.pjs.curslice + 1
            if self.pjs.n_frames == 1:
                lastSlice = 1
            else:
                lastSlice = self.pjs.slices.shape[0]

            ui.setupUi(dialog, savepath=self.pjs.cwd, firstslice=firstSlice, lastslice=lastSlice)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            themeasurements = ui.measurements()
            dialog.close()

        else:
            if firstSlice > lastSlice:
                firstSlice, lastSlice = lastSlice, firstSlice

            filename = RUtils.set_extension(filename, '.csv')

            if measurements is False or measurements is None:
                themeasurements = {
                    'path': filename,
                    'first': firstSlice,
                    'last': lastSlice,
                    'area': True,
                    'perimeter': True,
                    'pixels': True,
                    'image': True
                }

            else:
                themeasurements = {
                    'path': filename,
                    'first': firstSlice,
                    'last': lastSlice,
                    'area': measurements.get('area', False),
                    'perimeter': measurements.get('perimeter', False),
                    'pixels': measurements.get('pixels', False),
                    'image': measurements.get('image', False)
                }

            continue_flag = True

        if continue_flag:
            theslicenumbers = numpy.arange(themeasurements['first'] - 1, themeasurements['last'])

            theresults = self.measurePolygons_pandas(themeasurements, theslicenumbers)

            # If a file name was entered, save the data.
            if themeasurements["path"] != '':
                #RUtils.write_dict_csv(filename, theresults)
                #results_df = pd.DataFrame(theresults)
                theresults.to_csv(filename)

            else:
                print(theresults)

        return theresults

    def measurePolygons(self, measurements: dict, slices: numpy.ndarray) -> dict:
        # todo: add other measurements: heterogeneity, shape factor, edge-to-centre distance profile, etc.
        # todo: change lists from dictionary into numpy.ndarrays.
        """
        DEPRECATED: delete.
        :param measurements:
        :param slices: slice indexes -start at 0-, not numbers -start at 1-.
        :return:
        """

        # Create dictionary with results.
        theresults = {'area': [], 'perimeter': [], 'pixel_values_perimeter': [], 'pixel_values_interior': [], 'image_mean': [], 'image_mode': []}

        n_measurements = max(slices)+1

        theareas = [[] for i in range(n_measurements)]
        theperimeters = [[] for i in range(n_measurements)]
        thepixvalsperi = [[] for i in range(n_measurements)]
        thepixvalsinterior = [[] for i in range(n_measurements)]
        theimagemeans = [numpy.nan for i in range(n_measurements)]
        theimagemodes = [numpy.nan for i in range(n_measurements)]

        # For every slice ...
        for i in slices:
            theimage = self.pjs.slices[i]

            # Find the polylines in this slice.
            polygon_slice = self.pjs.polylines[i]

            n_polylines = len(polygon_slice)

            # For every polyline ...
            for j in range(n_polylines):
                # Create a polyline and measure it:
                thepolyline = rpolyline.RPolyline(polygon_slice[j])

                # Areas.
                if measurements['area']:
                    # Create a polyline and calculate the area.
                    theareas[i].append(thepolyline.area())

                # Perimeters.
                if measurements['perimeter']:
                    theperimeters[i].append(thepolyline.perimeter())

                # Pixel values.
                if measurements['pixels']:
                    intensities = thepolyline.pixel_values(theimage, self.pjs.brush_size)
                    thepixvalsperi[i].append(intensities[0])
                    thepixvalsinterior[i].append(intensities[1])

            # Image statistics.
            if measurements['image']:
                theimagemeans[i] = numpy.mean(theimage)

                # This is way slower than the following: themode = scipy.stats.mode(theimage, axis=None)[0][0]
                imhist = numpy.histogram(theimage, numpy.arange(numpy.max(theimage)+2))
                themode = imhist[1][numpy.argmax(imhist[0])]
                theimagemodes[i] = themode

        theresults['area'] = theareas
        theresults['perimeter'] = theperimeters
        theresults['pixel_values_perimeter'] = thepixvalsperi
        theresults['pixel_values_interior'] = thepixvalsinterior
        theresults['image_mean'] = theimagemeans
        theresults['image_mode'] = theimagemodes

        return theresults

    def measurePolygons_pandas(self, measurements: dict, slices: numpy.ndarray) -> pd.DataFrame:
        # todo: add other measurements: heterogeneity, shape factor, edge-to-centre distance profile, etc.
        # todo: change lists from dictionary into numpy.ndarrays.
        """
        Returns a pandas DataFrame in which columns represent time points and rows correspond to image statistics or polylines.
        :param measurements:
        :param slices: slice indexes -start at 0-, not numbers -start at 1-.
        :return:
        """
        # Create dictionary with results.
        n_image_metrics: int = 3
        n_polyline_metrics: int = 4
        # Find the maximum number of polygons in a slice
        max_n_polylines = 0
        for i in slices:
            polygon_slice = self.pjs.polylines[i]
            max_n_polylines = max(max_n_polylines, len(polygon_slice))

        row_names = ['slice_number', 'image_mean', 'image_mode']
        row_names.extend(['area_' + str(i) for i in range(1, max_n_polylines+1)])
        row_names.extend(['perimeter_' + str(i) for i in range(1, max_n_polylines+1)])
        row_names.extend(['pixel_values_perimeter_' + str(i) for i in range(1, max_n_polylines+1)])
        row_names.extend(['pixel_values_interior_' + str(i) for i in range(1, max_n_polylines+1)])

        rows: int = n_image_metrics + n_polyline_metrics * max_n_polylines
        columns: int = slices.shape[0]

        measurement_df: pd.DataFrame = pd.DataFrame(numpy.nan * numpy.zeros((rows, columns)), columns=slices+1, index=row_names)

        # For every slice ...
        for i in slices:
            # When indexing a DataFrame, the i+1 is the name of the column, not an index.
            measurement_df.loc['slice_number', i + 1] = i+1

            theimage = self.pjs.slices[i]

            # Find the polylines in this slice.
            polygon_slice = self.pjs.polylines[i]

            n_polylines = len(polygon_slice)

            # For every polyline ...
            for j in range(n_polylines):
                # Create a polyline and measure it:
                thepolyline = rpolyline.RPolyline(polygon_slice[j])

                # Areas.
                if measurements['area']:
                    # Create a polyline and calculate the area.
                    measurement_df.loc['area_' + str(j+1), i + 1] = thepolyline.area()

                # Perimeters.
                if measurements['perimeter']:
                    measurement_df.loc['perimeter_' + str(j+1), i + 1] = thepolyline.perimeter()

                # Pixel values.
                if measurements['pixels']:
                    intensities = thepolyline.pixel_values(theimage, self.pjs.brush_size)
                    measurement_df.loc['pixel_values_perimeter_' + str(j+1), i + 1] = intensities[0]
                    measurement_df.loc['pixel_values_interior_' + str(j+1), i + 1] = intensities[1]

            # Image statistics.
            if measurements['image']:
                measurement_df.loc['image_mean', i + 1] = numpy.mean(theimage)

                # This is way slower than the following: themode = scipy.stats.mode(theimage, axis=None)[0][0]
                themode = rimutils.mode(theimage)
                measurement_df.loc['image_mode', i + 1] = themode

        return measurement_df