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
from PyQt5 import QtWidgets

from pyjamas import dialogs
from pyjamas.pjsthreads import ThreadSignals
from pyjamas.rcallbacks.rcallback import RCallback
from pyjamas.rutils import RUtils


class RCBTrackFiducials(RCallback):
    def cbTrackFiducials(self, firstSlice: int = None, lastSlice: int = None) -> bool:

        # If not enough parameters, open a dialog.
        if (firstSlice is False or firstSlice is None or lastSlice is False or lastSlice is None) \
                and self.pjs is not None:
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

            # But DO propagate (in a thread)!!
            """athread = Thread(self.track_fiducials)
            athread.kwargs['theslices'] = theslicenumbers
            athread.kwargs['progress_signal'] = athread.signals.progress
            athread.kwargs['stop_signal'] = athread.signals.stop

            athread.signals.finished.connect(self.finished_fn)
            athread.signals.progress.connect(self.progress_fn)
            athread.signals.stop.connect(self.stop_fn)

            self.pjs.threadpool.start(athread)"""

            self.launch_thread(self.track_fiducials, {'theslices': theslicenumbers, 'progress': True, 'stop': True}, finished_fn=self.finished_fn, stop_fn=self.stop_fn, progress_fn=self.progress_fn)

            return True
        else:
            return False

    def track_fiducials(self, theslices: numpy.ndarray, progress_signal: ThreadSignals, stop_signal: ThreadSignals) -> bool:
        """
        Requires a constant number of fiducials.

        :param theslices: indeces of the slices in which fiducials will be tracked. They do not need to be consecutive.
        :return:
        """
        # Make sure that the slices are in a 1D numpy array.
        theslices = numpy.atleast_1d(theslices)
        num_slices = theslices.size

        # For every slice ...
        for i in range(num_slices-1):
            if len(self.pjs.fiducials[theslices[i]]) == 0:
                stop_signal.emit(f"Stopping at slice {theslices[i]+1}: there are no fiducials to track there!")
                return True

            if len(self.pjs.fiducials[theslices[i+1]]) == 0:
                stop_signal.emit(f"Stopping at slice {theslices[i+1]+1}: there are no fiducials to track there!")
                return True

            if len(self.pjs.fiducials[theslices[i]]) != len(self.pjs.fiducials[theslices[i+1]]):
                stop_signal.emit(f"Error: slices {theslices[i]+1} and {theslices[i + 1] + 1} have a different number of fiducials.")
                return False

            fiducials_orig = numpy.array(self.pjs.fiducials[theslices[i]])
            fiducials_dest = numpy.array(self.pjs.fiducials[theslices[i + 1]])

            # Find distance between all pairs of fiducials.
            distance_matrix: numpy.ndarray = RUtils.point2point_distances(fiducials_orig, fiducials_dest)
            sorted_indices: numpy.ndarray = distance_matrix.argsort()

            # For each fiducials_orig[ii] select the closest fiducials_dest[jj].
            closest_fiducial_index: numpy.ndarray = sorted_indices[:, 0]

            # Deal with cases in which more than one fiducial maps to another.
            # bincount is WAY faster than unique.
            #theindex, counts = numpy.unique(closest_fiducial_index, return_counts=True)
            #conflictive_indeces = theindex[counts > 1]
            counts: int = numpy.bincount(closest_fiducial_index)

            if any(counts > 1):
                conflictive_indeces = numpy.arange(counts.shape[0])[counts > 1]
                original_fiducials = numpy.arange(closest_fiducial_index.shape[0])[closest_fiducial_index == conflictive_indeces[0]]
                stop_signal.emit(f"Error in slice {theslices[i + 1]+1}, fiducial {conflictive_indeces[0]+1}: fiducials {original_fiducials+1} from slice {theslices[i]+1} map here.")
                return False

            else:
                self.pjs.fiducials[theslices[i+1]] = fiducials_dest[closest_fiducial_index].tolist()

            progress_signal.emit(int((100*(i+1))/(num_slices-1)))

        return True
