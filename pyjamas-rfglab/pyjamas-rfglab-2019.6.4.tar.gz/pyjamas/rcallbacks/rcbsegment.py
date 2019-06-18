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

# todo:
# move gaussian filtering INSIDE the rimutils functions (find_seeds or waterseed)?

import numpy
from PyQt5 import QtWidgets
from shapely.geometry import Point
from scipy import ndimage
from scipy.spatial import ConvexHull
import skimage.filters

import pyjamas.dialogs as dialogs
from pyjamas.pjsthreads import ThreadSignals
from pyjamas.rcallbacks.rcallback import RCallback
from pyjamas.rimage.rimutils import rimutils
from pyjamas.rutils import RUtils


class RCBSegment(RCallback):
    DEFAULT_WINDOW_SZ: int = 64
    DEFAULT_SMOOTHING_SIGMA: float = 0.8
    DEFAULT_BINARY_DILATIONS: int = -4  # positive to segment dark objects with brigh background, negative for the opposite.
    DEFAULT_MINIMUM_DISTANCE_TRANSFORM: float = 5.0
    DEFAULT_MAX_SEED_NUMBER: int = 100
    DEFAULT_PREVIEW: bool = False
    DEFAULT_ALPHA_CONCAVE_HULL: int = 25  # Trial and error ...
    _MIN_CELL_AREA: int = 10
    _MAX_CELL_AREA: int = 10000
    CENTER_SEEDS_CLOSER_TO_THE_EDGE: float = 6.0

    # Smallest possible value for firstSlice is 1.
    def cbFindSeeds(self, firstSlice: int = None, lastSlice: int = None, sigma: float = None, window_size: int = None,
                    bindilation: int = None, mindist: float = None, preview: bool = None) -> bool:

        # If not enough parameters, open a dialog.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None or
            window_size is False or window_size is None or sigma is False or sigma is None or bindilation is False or
            bindilation is None or mindist is False or mindist is None or preview is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.findseeds.FindSeedsDialog(self.pjs)
            if self.pjs.n_frames == 1:
                lastSlice = 1
            else:
                lastSlice = self.pjs.slices.shape[0]

            ui.setupUi(dialog, firstslice=self.pjs.curslice + 1, lastslice=lastSlice,
                       gaussian_sigma=dialogs.findseeds.FindSeedsDialog.gaussianSigma,
                       winsz=dialogs.findseeds.FindSeedsDialog.window_size,
                       bindilation=dialogs.findseeds.FindSeedsDialog.binary_dilation_number,
                       mindist=dialogs.findseeds.FindSeedsDialog.min_distance_transform,
                       preview_flag=dialogs.findseeds.FindSeedsDialog.preview)

            # If you try to make this dialog non-modal, make sure to switch from dialog to using self.dialog.
            # Otherwise, when you delete the exec line and the method ends, there are no references to the
            # dialog object and it will disappear.
            # You will also need to comment out the dialog.close() below.
            dialog.exec_()
            dialog.show()

            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        # Otherwise, continue with the supplied parameters.
        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'window_size': window_size, 'sigma': sigma,
                             'binary_dilation_number': bindilation,
                             'min_distance_transform': mindist, 'preview': preview}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Propagate forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Propagate backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO propagate!!
            self.launch_thread(self.findSeeds, {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True}, finished_fn=self.finished_fn, progress_fn=self.progress_fn)

            return True
        else:
            return False

    def cbSegmentDetectedObjects(self, firstSlice: int = None, lastSlice: int = None, sigma: float = None) -> bool:

        continue_flag: bool = False

        # If not enough parameters, open a dialog.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None or
            sigma is False or sigma is None) and self.pjs is not None:

            firstSlice = self.pjs.curslice + 1

            if self.pjs.n_frames == 1:
                lastSlice = 1
            else:
                lastSlice = self.pjs.slices.shape[0]

            dialog = QtWidgets.QDialog()
            ui = dialogs.expandseeds.ExpandSeedsDialog()

            ui.setupUi(dialog, firstslice=firstSlice, lastslice=lastSlice,
                       gaussian_sigma=dialogs.expandseeds.ExpandSeedsDialog.gaussianSigma)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        # Otherwise, continue with the supplied parameters.
        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'sigma': sigma}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Propagate forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Propagate backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO propagate!!
            self.launch_thread(self.segmentROIs, {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True}, finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn)


        return continue_flag

    # Smallest possible value for firstSlice is 1.
    def cbPropagateSeeds(self, firstSlice: int = None, lastSlice: int = None, xcorrWindowSize: int = None) -> bool:

        # If not enough parameters, open a dialog.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None or xcorrWindowSize is False or xcorrWindowSize is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.propagateseeds.PropagateSeedsDialog()
            if self.pjs.n_frames == 1:
                lastSlice = 1
            else:
                lastSlice = self.pjs.slices.shape[0]

            ui.setupUi(dialog, firstslice=self.pjs.curslice + 1, lastslice=lastSlice,
                       xcorrwinsz=dialogs.propagateseeds.PropagateSeedsDialog.window_size)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        # Otherwise, continue with the supplied parameters.
        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'xcorr_win_sz': xcorrWindowSize}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Propagate forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Propagate backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO propagate!!
            self.launch_thread(self.propagateSeeds, {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True, 'stop': True}, finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn)

            return True
        else:
            return False

    # Smallest possible value for firstSlice is 1.
    def cbCentroidSeeds(self, firstSlice: int = None, lastSlice: int = None) -> bool:

        # If not enough parameters, open a dialog.
        if (
                firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.timepoints.TimePointsDialog()

            firstSlice = self.pjs.curslice + 1
            if self.pjs.n_frames == 1:
                lastSlice = 1
            else:
                lastSlice = self.pjs.slices.shape[0]

            ui.setupUi(dialog, firstslice=firstSlice, lastslice=lastSlice)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters_tuple = ui.parameters()
            theparameters = {'first': theparameters_tuple[0], 'last': theparameters_tuple[1]}

            dialog.close()

        # Otherwise, continue with the supplied parameters.
        else:
            theparameters = {'first': firstSlice, 'last': lastSlice}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Propagate forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Propagate backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO propagate!!
            self.launch_thread(self.centroidSeeds,
                               {'theslices': theslicenumbers, 'progress': True},
                               finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn)

            return True
        else:
            return False

    def cbExpandSeeds(self, firstSlice: int = None, lastSlice: int = None, sigma: float = None) -> bool:

        # If not enough parameters, open a dialog.
        if (
                firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None or sigma is False or sigma is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.expandseeds.ExpandSeedsDialog()

            firstSlice = self.pjs.curslice + 1

            if self.pjs.n_frames == 1:
                lastSlice = 1
            else:
                lastSlice = self.pjs.slices.shape[0]

            ui.setupUi(dialog, firstslice=firstSlice, lastslice=lastSlice,
                       gaussian_sigma=dialogs.expandseeds.ExpandSeedsDialog.gaussianSigma)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        # Otherwise, continue with the supplied parameters.
        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'sigma': sigma}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Expand forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Expand backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO expand!!
            self.launch_thread(self.expandSeeds,
                               {'parameters': theparameters, 'theslices': theslicenumbers, 'progress': True},
                               finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn)
            return True
        else:
            return False

    def cbExpandNPropagateSeeds(self, firstSlice: int = None, lastSlice: int = None, sigma: float = None,
                                xcorrWindowSize: int = None) -> bool:
        # If not enough parameters, open a dialog.
        if (
                firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None or xcorrWindowSize is False or xcorrWindowSize is None or sigma is False or sigma is None) and self.pjs is not None:
            dialog = QtWidgets.QDialog()
            ui = dialogs.expandnpropagateseeds.ExpandNPropagateSeedsDialog()
            if self.pjs.n_frames == 1:
                lastSlice = 1
            else:
                lastSlice = self.pjs.slices.shape[0]

            ui.setupUi(dialog, firstslice=self.pjs.curslice + 1, lastslice=lastSlice,
                       gaussian_sigma=dialogs.expandnpropagateseeds.ExpandNPropagateSeedsDialog.gaussianSigma,
                       xcorrwinsz=dialogs.expandnpropagateseeds.ExpandNPropagateSeedsDialog.window_size)
            dialog.exec_()
            dialog.show()
            # If the dialog was closed by pressing OK, then run the measurements.
            continue_flag = dialog.result() == QtWidgets.QDialog.Accepted
            theparameters = ui.parameters()

            dialog.close()

        # Otherwise, continue with the supplied parameters.
        else:
            theparameters = {'first': firstSlice, 'last': lastSlice, 'sigma': sigma, 'xcorr_win_sz': xcorrWindowSize}
            continue_flag = True

        # When you have the input parameters:
        if continue_flag:
            # Expand forward.
            if theparameters['first'] <= theparameters['last']:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'])

            # Expand backwards.
            else:
                theslicenumbers = numpy.arange(theparameters['first'] - 1, theparameters['last'] - 2, -1)

            # But DO expand!!
            self.launch_thread(self.expandNPropagateSeeds,
                               {'parameters': theparameters, 'theslices': theslicenumbers,
                                'progress': True, 'stop': True},
                               finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn)
            return True
        else:
            return False

    def propagateSeeds(self, parameters: dict, theslices: numpy.ndarray, progress_signal: ThreadSignals, stop_signal: ThreadSignals) -> bool:

        # Output parameters.
        Xflow: numpy.ndarray = numpy.empty(0)
        Yflow: numpy.ndarray = numpy.empty(0)

        xcorr_win_sz = parameters.get('xcorr_win_sz', RCBSegment.DEFAULT_WINDOW_SZ)

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # Make sure there are fiducials to move.
        if len(self.pjs.fiducials[theslices[0]]) == 0:
            stop_signal.emit(f"Stopping at slice {theslices[i] + 1}: there are no fiducials to move there.")
            return False

        # For every slice ...
        for i in range(num_slices - 1):
            # Calculate the optic flow between consecutive images and interpolate at the fiducials.
            Xflow, Yflow, _, _ = rimutils.flow(self.pjs.slices[theslices[i]],
                                               self.pjs.slices[theslices[i + 1]],
                                               numpy.array(self.pjs.fiducials[theslices[i]]), xcorr_win_sz)

            # Shift the position of the fiducials in this slice by the flow ... In this case, the coordinates are
            # organized as [x, y], as they come from the fiducial list in PyJAMAS.
            destination_point_array = numpy.array(self.pjs.fiducials[theslices[i]])
            destination_point_array[:, 0] = numpy.int64(numpy.round(
                numpy.float64(destination_point_array[:, 0]) + Xflow))  # X coordinate.
            destination_point_array[:, 1] = numpy.int64(numpy.round(
                numpy.float64(destination_point_array[:, 1]) + Yflow))  # Y coordinate.

            # Here we should clip the fiducials at the ends so that seeds do not go beyond image margins.
            # ind2 = find(next_seeds(:, 1) < 0);
            # next_seeds(intersect(ind, ind2), 1) = 0;
            # ind2 = find(next_seeds(:, 1) >= ud.imsize(1));
            # next_seeds(intersect(ind, ind2), 1) = ud.imsize(1) - 1;
            # ind2 = find(next_seeds(:, 2) < 0);
            # next_seeds(intersect(ind, ind2), 2) = 0;
            # ind2 = find(next_seeds(:, 2) >= ud.imsize(2));
            # next_seeds(intersect(ind, ind2), 2) = ud.imsize(2) - 1;

            # ... before copying them onto the next slice.
            self.pjs.fiducials[theslices[i + 1]] = destination_point_array.tolist()

            # Only emit progress signal if doing more than one slice.
            if num_slices > 1:
                progress_signal.emit(int((100*(i+1))/(num_slices-1)))

        return True

    def centroidSeeds(self, theslices: numpy.ndarray, progress_signal: ThreadSignals) -> bool:

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices):
            thepolylines = [RUtils.qpolygonf2polygon(one_polyline) for one_polyline in self.pjs.polylines[theslices[i]]]

            for one_polyline in thepolylines:
                polycentroid = one_polyline.centroid
                self.pjs.addFiducial(int(polycentroid.x), int(polycentroid.y), theslices[i], paint=False)

            # Only emit progress signal if doing more than one slice.
            if num_slices > 1:
                progress_signal.emit(int((100 * (i + 1)) / num_slices))

        return True

    def findSeeds(self, parameters, theslices, progress_signal: ThreadSignals) -> bool:
        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices):
            theimage = self.pjs.slices[theslices[i]].copy()
            theimage = skimage.filters.gaussian(theimage, parameters['sigma'], multichannel=False)
            # Expand the seeds in the image.
            # ADD WHEELS TO DIALOG FOR WINDOW_SIZE, OPENING/CLOSING SIZE, MIN_DT_VALUE
            seed_coordinates, _ = rimutils.find_seeds(theimage,
                                                      parameters.get('window_size', RCBSegment.DEFAULT_WINDOW_SZ),
                                                      parameters.get('binary_dilation_number',
                                                                     RCBSegment.DEFAULT_BINARY_DILATIONS),
                                                      parameters.get('min_distance_transform',
                                                                     RCBSegment.DEFAULT_MINIMUM_DISTANCE_TRANSFORM),
                                                      )

            # Add the coordinates to the list of fiducials.
            for aSeed in seed_coordinates:
                self.pjs.addFiducial(aSeed[1], aSeed[0], theslices[i], paint=False)

            # Only emit progress signal if doing more than one slice.
            if num_slices > 1:
                progress_signal.emit(int((100 * (i + 1)) / num_slices))

        return True

    def segmentROIs(self, parameters, theslices, progress_signal: ThreadSignals) -> bool:
        """

        :param parameters:
        :param theslices:
        :return:
        """

        centre_seeds: bool = parameters.get('centre_seeds', True)

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        one = numpy.uint(1)

        # For every slice ...
        for i in range(num_slices):
            theimage: numpy.ndarray = self.pjs.slices[theslices[i]].copy()

            theimage = skimage.filters.gaussian(theimage, parameters.get('sigma', 0), multichannel=False)

            therois = self.pjs.polylines[theslices[i]].copy()  # without this copy instruction, the loop below will also go through newly added (within the loop) polygons

            theindex = -1

            # For every ROI ...
            for aroi in therois:
                theindex += 1
                # This code borrowed from rcbcrop.cbCrop. Places a seed at the center of the bounding box.
                # Because most classifiers will "detect" objects using rectangles, this works well. here.
                if aroi != []:
                    minx, miny, maxx, maxy = aroi.boundingRect().getCoords()
                    minx, miny, maxx, maxy = numpy.uint((minx, miny, maxx, maxy))
                else:
                    continue

                roi_im: numpy.ndarray = theimage[miny:(maxy+one), minx:(maxx+one)]
                rows, columns = roi_im.shape
                corner_coords = numpy.asarray([[0, 0], [0, columns - 1], [rows - 1, columns - 1], [rows - 1, 0]],
                                              dtype=numpy.int16)  # in row, col

                # Find seeds only within the roi.
                if centre_seeds:
                    seed_coordinates = numpy.asarray([[(miny+maxy)/2 - miny, (minx+maxx)/2 - minx]], dtype=numpy.int16)
                else:
                    seed_coordinates, _ = rimutils.find_seeds(roi_im,
                                                              parameters.get('window_size', RCBSegment.DEFAULT_WINDOW_SZ),
                                                              parameters.get('binary_dilation_number',
                                                                             RCBSegment.DEFAULT_BINARY_DILATIONS),
                                                              parameters.get('min_distance_transform',
                                                                             RCBSegment.DEFAULT_MINIMUM_DISTANCE_TRANSFORM),
                                                              )

                    # if more than one seed, keep only the central one.

                # Add the coordinates to the list of fiducials.
                for aSeed in seed_coordinates:
                    self.pjs.addFiducial(minx+aSeed[1], miny+aSeed[0], theslices[i], paint=False)


                # Find the dimmest corner of the image gradient to be used as background seed.
                roi_grad: numpy.ndarray = ndimage.gaussian_gradient_magnitude(roi_im, parameters['sigma'])
                ind: int = numpy.argmin(roi_grad[corner_coords[:, 0], corner_coords[:, 1]])

                theseeds: numpy.ndarray = numpy.vstack((corner_coords[ind, [1, 0]], seed_coordinates[:, [1, 0]]))

                # Expand the seeds on the gradient of the roi.
                # NOTE: the goal here is to have one background and one object seed. TYPICALLY, the binary masks
                # for each of the two labels will be the opposite of each other. But find_contours, used
                # in rimutils.waterseed to extract contours from binary images, will detect zero crossings, and thus
                # will return the same contour for both. So below, we will discard the first contour (the one
                # corresponding to the background seed).
                contour_list = rimutils.waterseed(roi_grad, theseeds)

                # Add the contours to the list of annotations.
                for aContour in contour_list[1:]:
                    for aPoint in aContour:
                        aPoint[0], aPoint[1] = aPoint[0] + minx, aPoint[1] + miny

                    self.pjs.replacePolyline(theindex, aContour, theslices[i], paint=False)

                # Only emit progress signal if doing more than one slice.
                if num_slices > 1:
                    progress_signal.emit(int((100 * (i + 1)) / num_slices))

        return True

    def expandSeeds(self, parameters, theslices, progress_signal: ThreadSignals) -> bool:
        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices):
            # Make sure there are fiducials to expand.
            if not self.pjs.fiducials[theslices[i]]:
                continue

            theimage = self.pjs.slices[theslices[i]].copy()
            theimage = skimage.filters.gaussian(theimage, parameters['sigma'], multichannel=False)
            # Expand the seeds in the image.
            contour_list = rimutils.waterseed(theimage, numpy.asarray(self.pjs.fiducials[theslices[i]]))
            # Or for gradient-based segmentation:
            # import skimage.filters
            # contour_list = rimutils.waterseed(skimage.filters.sobel(self.pjs.slices[theslices[i]]),
            #                                               numpy.asarray(self.pjs.fiducials[theslices[i]]))

            # Add the contours to the list of annotations.
            for aContour in contour_list:
                self.pjs.addPolyline(aContour, theslices[i], paint=False)

            # Only emit progress signal if doing more than one slice.
            if num_slices > 1:
                progress_signal.emit(int((100 * (i + 1)) / num_slices))

        return True

    def centerSeeds(self, distance, theslices, exclude_peripheral_seeds=False):
        """

        :param distance:
        :param theslices:
        :param exclude_peripheral_seeds: use the convex_hull?
        :return:
        """
        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices):
            thepolylines = [RUtils.qpolygonf2polygon(one_polyline) for one_polyline in self.pjs.polylines[theslices[i]]]

            # Find the concave hull for the fiducials
            if exclude_peripheral_seeds:
                fiducial_hull: numpy.ndarray = RUtils.concave_hull(numpy.asarray(self.pjs.fiducials[theslices[i]]),
                                                                   self.DEFAULT_ALPHA_CONCAVE_HULL)

                if fiducial_hull.size == 0:
                    fiducial_hull = ConvexHull(numpy.asarray(self.pjs.fiducials[theslices[i]]))
            # The problem is that polygons and fiducials are not stored in the same order. Aaaaarghh!
            # Or rather, they are in the same order, but the order is updated when polygons are deleted
            # after touching the edge?
            # An alternative is to find, for each fiducial, an enclosing polygon, and go from there.
            for idx_fiducial, one_fiducial in enumerate(self.pjs.fiducials[theslices[i]]):
                # If peripheral points must be excluded and this is one of them, then skip it.
                if exclude_peripheral_seeds and idx_fiducial in fiducial_hull:
                    continue

                oneShapelyFiducial = Point(one_fiducial)

                for one_polyline in thepolylines:
                    if one_polyline.contains(oneShapelyFiducial):
                        if oneShapelyFiducial.distance(one_polyline.exterior) < distance and \
                                RCBSegment._MIN_CELL_AREA < one_polyline.area < RCBSegment._MAX_CELL_AREA:
                            polycentroid = one_polyline.centroid
                            self.pjs.fiducials[theslices[i]][idx_fiducial][0] = int(polycentroid.x)
                            self.pjs.fiducials[theslices[i]][idx_fiducial][1] = int(polycentroid.y)

                        break

        return

    def expandNPropagateSeeds(self, parameters, theslices, progress_signal: ThreadSignals, stop_signal: ThreadSignals) -> bool:

        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices - 1):
            # Expand in the current time point.
            self.expandSeeds(parameters, theslices[i], progress_signal)

            # Center seeds.
            self.centerSeeds(RCBSegment.CENTER_SEEDS_CLOSER_TO_THE_EDGE, theslices[i])

            # Propagate to the next time point.
            self.propagateSeeds(parameters, theslices[i:i + 2], progress_signal, stop_signal)

            progress_signal.emit(int((100 * (i + 1)) / num_slices))

        # Finally, expand in the last time point and center the seeds.
        self.expandSeeds(parameters, theslices[-1], progress_signal)

        # Center seeds.
        self.centerSeeds(RCBSegment.CENTER_SEEDS_CLOSER_TO_THE_EDGE, theslices[-1])

        progress_signal.emit(int(100))

        return True
