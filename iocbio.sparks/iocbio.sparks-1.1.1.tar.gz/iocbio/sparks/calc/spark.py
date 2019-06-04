# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#  Copyright (C) 2018
#   Laboratory of Systems Biology, Department of Cybernetics,
#   School of Science, Tallinn University of Technology
#  Authors: Martin Laasmaa and Marko Vendelin
#  This file is part of project: IOCBIO Sparks
#
import numpy as np
import math
from skimage.feature import peak_local_max
from skimage.morphology import watershed, binary_dilation
from scipy import ndimage
from scipy.interpolate import interp1d, PchipInterpolator
from scipy.optimize import leastsq, brentq
from collections import namedtuple, OrderedDict

import PyQt5.QtCore as QC
from PyQt5.QtCore import pyqtSlot, pyqtSignal

from .auto_detect import get_sparks
from ..handler.image import Image

import iocbio.sparks.worker as worker
import iocbio.sparks.info as info
from iocbio.sparks.constants import database_table_roi, database_table_spark, database_table_spark_extended


### parameters used for sparks analysis

PDesc = namedtuple("PDesc", ["human_short", "human_long", "default", "sqltype", "pytype", "sqlinsert"])

Parameters = OrderedDict([
    ["enforce_monotonic_time", PDesc("Monotonic time transient", "Enforce monotonic increase and decay for time transient", False, "INTEGER", bool, int)],
    ["enforce_monotonic_space", PDesc("Monotonic spatial transient", "Enforce monotonic increase and decay for spatial transient", False, "INTEGER", bool, int)],
    ["slice_by_time", PDesc("Lines averaged for spatial transient", "Number of lines used for averaging spatial transient taken at before and after half-decay", 3, "INTEGER", int, int)],
    ["time_spline_nodes_before", PDesc("Time nodes before peak", "Spline nodes used to fit time transient before the peak", 7, "INTEGER", int, int)],
    ["time_spline_nodes_after", PDesc("Time nodes after peak", "Spline nodes used to fit time transient after the peak", 10, "INTEGER", int, int)],
    ["slice_by_location", PDesc("Lines averaged for time transient", "Number of lines used for averaging time transient taken before and after spark peak", 3, "INTEGER", int, int)],
    ["space_spline_nodes_before", PDesc("Space nodes before peak", "Spline nodes used to fit time transient before the peak", 7, "INTEGER", int, int)],
    ["space_spline_nodes_after", PDesc("Space nodes after peak", "Spline nodes used to fit time transient after the peak", 7, "INTEGER", int, int)],
])

RDesc = namedtuple("RDesc", ["human_long", "unit", "view"])
Results = {
    "location_space": RDesc("Location: space", "microm", None),
    "location_time": RDesc("Location: time", "ms", None),
    "amplitude": RDesc("Amplitude", "AU", None),
    "amplitude_f0": RDesc("Amplitude/image F0", "", "amplitude/image.f0"),
    "amplitude_blurred": RDesc("Amplitude blurred", "AU", None),
    "amplitude_blurred_f0": RDesc("Amplitude blurred/image F0", "", "amplitude_blurred/image.f0"),
    "f0": RDesc("F0", "AU", None),
    "time_spline_amplitude": RDesc("Time: spline amplitude", "AU", None),
    "time_spline_amplitude_f0": RDesc("Time: spline amplitude/image F0", "", "time_spline_amplitude/image.f0"),
    "time_half_raise": RDesc("Time: half raise", "ms", None),
    "time_half_decay": RDesc("Time: half decay", "ms", None),
    "time_half_width": RDesc("Time: half width", "ms", "time_half_raise+time_half_decay"),
    "space_spline_amplitude": RDesc("Space: spline amplitude", "AU", None),
    "space_spline_amplitude_f0": RDesc("Space: spline amplitude/image F0", "", "space_spline_amplitude/image.f0"),
    "space_half_raise": RDesc("Space: half raise", "microm", None),
    "space_half_decay": RDesc("Space: half decay", "microm", None),
    "space_half_width": RDesc("Space: half width", "microm", "space_half_raise+space_half_decay"),
    "spark_size": RDesc("Spark size", "microm x ms", None)
}


class BumpSpline:
    def __init__(self, x, y, xmax, nodes_before=7, nodes_after=10, enforce_monotonic=False):
        """
        """
        self.x = x
        self.y = y
        self.xmax = xmax
        self.nodes_before = nodes_before
        self.nodes_after = nodes_after
        self.enforce_monotonic = enforce_monotonic
        self.spline_ready = False

        self.calcspline()

    def calcspline(self):
        try:
            dx0 = (self.xmax-self.x[0]) / self.nodes_before
            dx1 = (self.x[-1]-self.xmax) / self.nodes_after

            self.xx = np.append(np.linspace(self.x[0]-dx0/10, self.xmax, self.nodes_before),
                                np.linspace(self.xmax, self.x[-1]+dx1/10, self.nodes_after)[1:])
            yy = np.ones(self.xx.shape)
            r = leastsq(self.spline_error, yy)
            self.make_spline(r[0])
            self.spline_ready = True
        except:
            info.warning("Spline fitting failed. Exception occured during spline fitting")

    def make_spline(self, yy):
        if self.enforce_monotonic:
            val = yy[0]
            zz = [val]
            for i in range(1,self.nodes_before):
                val += yy[i]**2
                zz.append(val)
            for i in range(self.nodes_before, len(yy)):
                val -= yy[i]**2
                zz.append(val)
            self.spline = PchipInterpolator(self.xx, zz)
        else:
            #self.spline = interp1d(self.xx, yy, kind="cubic")
            self.spline = PchipInterpolator(self.xx, yy)

    def spline_error(self, pars):
        self.make_spline(pars)
        return self.curr_error()

    def curr_error(self):
        return self.y - self.spline(self.x)
        #return self.y[1:self.xmax] - self.spline(self.x[1:self.xmax])

    def __call__(self, x):
        return self.spline(x)

    def min(self):
        if not self.spline_ready: return None
        return min(self.spline(self.x[0]), self.spline(self.x[-1]))

    def max(self):
        if not self.spline_ready: return None
        return self.spline(self.xmax)

    def _intersect_error(self, x):
        return self.spline(x) - self.intersect_value

    def intersect(self, value):
        """
        Assuming that value is between minima and maxima, finds two argument values
        closest to the maxima at which spline is equal to value
        """
        if not self.spline_ready:
            return None, None

        self.intersect_value = value
        data = self.spline(self.x) - self.intersect_value

        i_raise, i_fall = None, None

        # raise
        i = self.xmax-1
        while i >= 0:
            if data[i+1] > 0 and data[i] <= 0:
                i_raise = self.x[i] + (self.x[i+1]-self.x[i]) / (data[i+1] - data[i]) * (-data[i])
                break
            i -= 1

        # fall
        i = self.xmax
        imax = len(data) - 1
        while i < imax:
            if data[i+1] < 0 and data[i] >= 0:
                i_fall = self.x[i] + (self.x[i+1]-self.x[i]) / (data[i] - data[i+1]) * (data[i])
                break
            i += 1

        return i_raise, i_fall

        # self.intersect_value = value
        # try:
        #     a ,b = brentq(self._intersect_error, self.x[0], self.xmax), brentq(self._intersect_error, self.xmax, self.x[-1])
        # except:
        #     print("Exception occured during zero finding")
        #     return None, None
        # return a, b

class SparkAnalyzerSignals(QC.QObject):
    sigStats = pyqtSignal(int, str, float)
    sigImage = pyqtSignal(int, str, np.ndarray)
    sigGraph = pyqtSignal(int, str, str, np.ndarray, np.ndarray)
    # sigJobDone = pyqtSignal()

class SparkAnalyzer(worker.Job):
    """Spark analysis object used internally by Spark object. Don't use it outside this class"""

    def __init__(self, id,
                 corrected_mean, corrected_mean_medblu,
                 corrected_meansd_medblu, bg, std_meansd_medblu, mF0, f0, dx, dt,
                 accept_as_possible_peak, accept_as_possible_area, min_area,
                 detector_median_time_px, detector_median_space_px,):
        """
        corrected - binary data [time][space], zero mean
        f0 - binary data [time][space]
        dx - pixel size in micrometers
        dt - line scan time in ms
        bg - fluorescence in the background without any cells
        min_distance - minimal separation of the peaks
        """

        worker.Job.__init__(self)

        self.id = id
        self.F0 = np.mean(f0)
        self.mF0 = mF0
        self.bg = bg
        self.corrected_mean = corrected_mean - bg - mF0
        self.corrected_mean_medblu = corrected_mean_medblu - bg - mF0
        self.corrected_meansd_medblu = corrected_meansd_medblu - bg - mF0
        self.std_meansd_medblu = std_meansd_medblu
        self.dx = dx
        self.dt = dt
        self.accept_as_possible_peak = accept_as_possible_peak
        self.accept_as_possible_area = accept_as_possible_area
        self.min_area = min_area
        self.detector_median_time_px = detector_median_time_px
        self.detector_median_space_px = detector_median_space_px

        self.signals = SparkAnalyzerSignals()

        # parameters
        # self.sigma_time = 3.0 / dt
        # self.sigma_space = 0.25 / dx
        # self.correction_percentile = 25.0
        #
        # self.mask_dilation_for_bg = 5
        #
        self.location_border = 3 # TODO set settable?

        # internal variables
        self.correction = None

        for k in Parameters.keys():
            setattr(self, k, Parameters[k].default)

    def run_job(self):
        waterlabel = get_sparks(self.corrected_meansd_medblu, std=self.std_meansd_medblu,
                                accept_as_possible_peak=self.accept_as_possible_peak,
                                accept_as_possible_area=self.accept_as_possible_area,
                                min_area=self.min_area,
                                detector_median_time_px=self.detector_median_time_px,
                                detector_median_space_px=self.detector_median_space_px,
                                largest_only=True)

        #self.location = np.unravel_index(self.corrected_medblu.argmax(), self.corrected_medblu.shape)

        if waterlabel.max() < 0.5: # no labels left
            info.warning("No spark detected")
            self.signals.sigStats.emit(self.id,  "Spark not found, no labels", 0)
            return

        # only one label is expected
        self.location = ndimage.maximum_position(self.corrected_meansd_medblu, waterlabel)

        # keep only spark-related mask
        label_value = waterlabel[self.location]
        waterlabel[ waterlabel!=label_value ] = 0
        waterlabel[ waterlabel==label_value ] = 1

        # send out images
        self.signals.sigImage.emit(self.id, "corrected", self.corrected_mean + self.bg + self.F0)
        self.signals.sigImage.emit(self.id, "medblu", self.corrected_mean_medblu + self.bg + self.F0)
        self.signals.sigImage.emit(self.id, "spark watermark", waterlabel)

        # check if location makes sense
        if self.location[0]<self.location_border or self.location[0]>=self.corrected_mean.shape[0]-self.location_border \
            or self.location[1]<self.location_border or self.location[1]>=self.corrected_mean.shape[1]-self.location_border:
            info.info("Cannot find location of the spark")
            self.signals.sigStats.emit(self.id,  "Spark not found, location not found", 0)
            return

        # send out first results
        self.signals.sigStats.emit(self.id, "location_space", self.location[0]*self.dx)
        self.signals.sigStats.emit(self.id, "location_time", self.location[1]*self.dt)
        self.signals.sigStats.emit(self.id, "amplitude", self.corrected_mean[self.location[0], self.location[1]])
        self.signals.sigStats.emit(self.id, "amplitude_f0", self.corrected_mean[self.location[0], self.location[1]] / self.mF0)
        self.signals.sigStats.emit(self.id, "amplitude_blurred",
                                   self.corrected_mean_medblu[self.location[0], self.location[1]])
        self.signals.sigStats.emit(self.id, "amplitude_blurred_f0",
                                   self.corrected_mean_medblu[self.location[0], self.location[1]] / self.mF0)
        self.signals.sigStats.emit(self.id, "f0", self.F0)

        # along time
        self.trace_time = self.corrected_mean[self.location[0]-self.slice_by_location:self.location[0]+self.slice_by_location+1,:].sum(axis=0)
        self.trace_time /= (2*self.slice_by_location + 1)

        # fit time
        self.spline_time = BumpSpline(np.linspace(0, self.trace_time.shape[0]-1, self.trace_time.shape[0]),
                                      self.trace_time, self.location[1],
                                      nodes_before=self.time_spline_nodes_before,
                                      nodes_after=self.time_spline_nodes_after,
                                      enforce_monotonic=self.enforce_monotonic_time)
        if not self.spline_time.spline_ready:
            self.signals.sigStats.emit(self.id,  "Failed to calculate time spline", 0)
            return

        xt = np.linspace(0, self.trace_time.shape[0]-1, self.trace_time.shape[0])
        self.signals.sigGraph.emit(self.id, "time", "original", xt*self.dt, self.trace_time)
        self.signals.sigGraph.emit(self.id, "time", "spline", xt*self.dt, self.spline_time(xt))

        self.time_halfvalue = self.spline_time.max()/2
        self.time_halfraise, self.time_halfdrop = self.spline_time.intersect(self.time_halfvalue)
        if self.time_halfraise is None or self.time_halfdrop is None:
            self.signals.sigStats.emit(self.id,  "Failed to find time constants", 0)
            return

        self.signals.sigStats.emit(self.id, "time_spline_amplitude", self.spline_time.max())
        self.signals.sigStats.emit(self.id, "time_spline_amplitude_f0", self.spline_time.max() / self.mF0)
        self.signals.sigStats.emit(self.id, "time_half_raise", self.dt*(self.location[1]-self.time_halfraise))
        self.signals.sigStats.emit(self.id, "time_half_decay", self.dt*(self.time_halfdrop - self.location[1]))
        self.signals.sigStats.emit(self.id, "time_half_width", self.dt*(self.time_halfdrop - self.time_halfraise))

        # along space
        # ti = int(self.time_halfdrop)
        # self.trace_space = self.corrected_mean[:,ti-self.slice_by_time:ti+self.slice_by_time+1].sum(axis=1)
        # self.trace_space /= (2*self.slice_by_time + 1)
        self.trace_space = self.corrected_mean[:,self.location[1]-self.slice_by_time:self.location[1]+self.slice_by_time+1].sum(axis=1)
        self.trace_space /= (2*self.slice_by_time + 1)

        self.spline_space = BumpSpline(np.linspace(0, self.trace_space.shape[0]-1, self.trace_space.shape[0]),
                                       self.trace_space, self.location[0],
                                       nodes_before=self.space_spline_nodes_before,
                                       nodes_after=self.space_spline_nodes_after,
                                       enforce_monotonic=self.enforce_monotonic_space)
        if not self.spline_space.spline_ready:
            self.signals.sigStats.emit(self.id,  "Failed to calculate spatial spline", 0)
            return

        xs = np.linspace(0, self.trace_space.shape[0]-1, self.trace_space.shape[0])
        self.signals.sigGraph.emit(self.id, "space", "original", xs*self.dx, self.trace_space)
        self.signals.sigGraph.emit(self.id, "space", "spline", xs*self.dx, self.spline_space(xs))

        self.space_halfvalue = self.spline_space.max()/2
        self.space_halfraise, self.space_halfdrop = self.spline_space.intersect(self.space_halfvalue)
        if self.space_halfraise is None or self.space_halfdrop is None:
            self.signals.sigStats.emit(self.id,  "Failed to find space constants", 0)
            return

        self.signals.sigStats.emit(self.id, "space_spline_amplitude", self.spline_space.max())
        self.signals.sigStats.emit(self.id, "space_spline_amplitude_f0", self.spline_space.max() / self.mF0)
        self.signals.sigStats.emit(self.id, "space_half_raise", self.dx*(self.location[0]-self.space_halfraise))
        self.signals.sigStats.emit(self.id, "space_half_decay", self.dx*(self.space_halfdrop - self.location[0]))
        self.signals.sigStats.emit(self.id, "space_half_width", self.dx*(self.space_halfdrop - self.space_halfraise))

        self.spark_size = np.sum(waterlabel)
        self.signals.sigStats.emit(self.id, "spark_size", self.spark_size*self.dt*self.dx)


class Spark(QC.QObject):
    """Spark detection class"""

    database_table = database_table_spark
    database_view = database_table_spark_extended
    settings_group = "spark"

    Parameters = Parameters

    sigUpdateImage = pyqtSignal()
    sigUpdateStats = pyqtSignal()
    sigUpdateGraph = pyqtSignal()
    sigNewAnalysis = pyqtSignal()

    @staticmethod
    def default_parameters():
        keys = list(Parameters.keys())
        keys.sort()
        return keys

    @staticmethod
    def database_schema(db, create_view=True):
        from iocbio.sparks.constants import database_table_image

        psql = ""
        keys = list(Parameters.keys())
        keys.sort()
        for k in keys:
            psql += k + " " + Parameters[k].sqltype +","

        keys = list(Results.keys())
        keys.sort()
        for k in keys:
            if Results[k].view is None:
                psql += k + " DOUBLE PRECISION,"

        db.query("CREATE TABLE IF NOT EXISTS " + db.table(Spark.database_table) +
                 "(roi_id text PRIMARY KEY, " + psql +
                 "FOREIGN KEY (roi_id) REFERENCES " + db.table(database_table_roi) + "(roi_id) ON DELETE CASCADE)")

        # view
        if create_view and not db.has_view(Spark.database_view):
            psql = "sd.roi_id,"
            for k in keys:
                if Results[k].view is not None:
                    psql += "sd." + Results[k].view + " AS " + k + ","
                else:
                    psql += "sd." + k + " AS " + k + ","
            psql = psql[:-1]
            db.query("CREATE VIEW " + db.table(Spark.database_view) + " AS SELECT " +
                     psql + " FROM " + db.table(Spark.database_table) + " sd "
                     "JOIN " + db.table(database_table_roi) + " roi ON roi.roi_id=sd.roi_id " +
                     "JOIN " + db.table(database_table_image) + " image ON roi.experiment_id=image.experiment_id")

    @staticmethod
    def database_schema_update_2_3(db):
        # make new table
        Spark.database_schema(db, create_view = False)

        kk = "roi_id,"
        for k in Parameters:
            kk += k + ","

        for k in Results:
            if Results[k].view is None:
                kk += k + ","

        kk = kk[:-1]
        db.query("INSERT INTO " + db.table(Spark.database_table) +
                 "(" + kk + ") SELECT " + kk + " FROM " +
                 db.table("spark") # name of the table in schema version 2"
                 )

        db.query("DROP TABLE " + db.table("spark"))

        # create view as well
        Spark.database_schema(db)

    @staticmethod
    def database_schema_update_3_4(db):
        db.query("DROP VIEW " + db.table("spark"))
        # create view as well
        Spark.database_schema(db)

    @staticmethod
    def set_defaults(defaults):
        settings = QC.QSettings()
        for k, v in defaults.items():
            if k in Parameters:
                if isinstance(v, bool):
                    v = int(v)
                settings.setValue(Spark.settings_group + "/" + k, v)

    @staticmethod
    def results_dict():
        return Results

    def __init__(self, experiment_id, roi_id, database, image, coords):

        QC.QObject.__init__(self)

        self.experiment_id = experiment_id
        self.roi_id = roi_id
        self.database = database

        self.set_coords(coords)
        self.image = image
        self.dx = image.dx * 1.e6 # meters to microns
        self.dt = image.dt * 1.e3 # seconds to milli-seconds

        self.store_results = True

        self.analysis_id = 0
        settings = QC.QSettings()
        keys = Spark.default_parameters()
        for k in keys:
            if isinstance(Parameters[k].default, bool):
                v = bool(int(( settings.value(Spark.settings_group + "/" + k,
                                              defaultValue = Parameters[k].default) )))
            else:
                v = Parameters[k].pytype( settings.value(Spark.settings_group + "/" + k,
                                                         defaultValue = Parameters[k].default) )
            setattr(self, k, v)

        # load parameters from the database if available
        if self.database is not None:
            psql = ""
            keys = list(Parameters.keys())
            for k in keys:
                psql += k + ","
            psql = psql[:-1]
            # only one row is expected
            for row in self.database.query("SELECT " + psql + " FROM " +
                                           self.database.table(Spark.database_table) +
                                           " WHERE roi_id=:rid", rid=self.roi_id):
                for i in range(len(keys)):
                    setattr(self, keys[i], row[i])

        self.analyze()

        self.image.sigUpdated.connect(self.onImageUpdate)

    def _updateImage(self, id, name, value):
        if self.analysis_id != id: return
        self.images[name] = value
        self.sigUpdateImage.emit()

    def _updateStats(self, id, name, value):
        if self.analysis_id != id: return
        self.stats[name] = value
        self.sigUpdateStats.emit()
        if self.store_results and self.database is not None and name in Results and Results[name].view is None:
            self.database.query("UPDATE " + self.database.table(Spark.database_table) +
                                " SET " + name + "=:val WHERE roi_id=:rid",
                                val=value, rid=self.roi_id)

    def _updateGraph(self, id, type, name, vx, vy):
        if self.analysis_id != id: return
        self.graphs[type][name] = { "x": vx, "y": vy }
        self.sigUpdateGraph.emit()

    def set_coords(self, coords):
        x0, y0, x1, y1 = coords
        self.coords = [x0,x1], [y0,y1]

    def onImageUpdate(self, name):
        if name in [Image.ALL, 'property: mF0', 'property: meansd std_medblu',
                    'Corrected MeanSD MedBlu', 'F0']:
            self.analyze(store_result=self.store_results)

    def analyze(self, store_result=None, updated_parameters=None):
        self.stats = {}
        self.images = { "original": self.image.get_slice('Raw', self.coords).T }
        self.graphs = { "time": {}, "space": {} }
        self.sigNewAnalysis.emit()

        if updated_parameters is not None:
            self.store_results = True
        if store_result is not None:
            self.store_results = store_result

        if updated_parameters is not None:
            for k in updated_parameters.keys():
                setattr(self, k, updated_parameters[k])

        if self.store_results and self.database is not None:
            self.database.query("DELETE FROM " + self.database.table(Spark.database_table) +
                                " WHERE roi_id=:rid",
                                rid=self.roi_id)

            pvals = { 'rid': self.roi_id }
            pnames = "roi_id,"
            args = "(:rid,"
            for k in Parameters.keys():
                pnames += k + ","
                args += ":" + k + ","
                pvals[k] = Parameters[k].sqlinsert(getattr(self, k))
            pnames = pnames[:-1]
            args = args[:-1] + ")"
            self.database.query("INSERT INTO " + self.database.table(Spark.database_table) +
                                "(" + pnames + ") VALUES " + args,
                                **pvals)

        corrected_mean = self.image.get_slice('Corrected Mean', self.coords)
        corrected_mean_medblu = self.image.get_slice('Corrected Mean MedBlu', self.coords)
        corrected_meansd_medblu = self.image.get_slice('Corrected MeanSD MedBlu', self.coords)
        f0 = self.image.get_slice('F0', self.coords)
        std_meansd_medblu = self.image.get_property('meansd std_medblu')
        mF0 = self.image.get_property('mF0')

        accept_as_possible_peak = self.image.get_property('accept_as_possible_peak')
        accept_as_possible_area = self.image.get_property('accept_as_possible_area')
        bg = self.image.get_property('bg')
        min_area = self.image.get_property('min_area')
        detector_median_time_px = self.image.get_property('detector_median_time_px')
        detector_median_space_px = self.image.get_property('detector_median_space_px')

        if corrected_meansd_medblu is None or corrected_mean is None or corrected_mean_medblu is None or f0 is None or std_meansd_medblu is None or mF0 is None:
            info.info("Spark: Have to wait for processed data")
            return

        # start analysis if we have all ready
        self.analysis_id += 1
        analyzer = SparkAnalyzer(self.analysis_id,
                                 corrected_mean=corrected_mean.T,
                                 corrected_mean_medblu=corrected_mean_medblu.T,
                                 corrected_meansd_medblu=corrected_meansd_medblu.T,
                                 bg=bg, std_meansd_medblu=std_meansd_medblu,
                                 mF0=mF0, f0=f0.T, dx=self.dx, dt=self.dt,
                                 accept_as_possible_peak=accept_as_possible_peak,
                                 accept_as_possible_area=accept_as_possible_area,
                                 min_area=min_area,
                                 detector_median_time_px = detector_median_time_px,
                                 detector_median_space_px = detector_median_space_px)
        analyzer.signals.sigImage.connect(self._updateImage)
        analyzer.signals.sigStats.connect(self._updateStats)
        analyzer.signals.sigGraph.connect(self._updateGraph)

        for k in Parameters.keys():
            setattr(analyzer, k, getattr(self, k))

        analyzer.start()

    def checkIfAnalysisIsOK(self, strict):
        """Check whether the found spark is in expected region and whether all stats were determined"""
        if "spark watermark" not in self.images or "space_half_width" not in self.stats:
            return False # some data is missing

        # check watermark next to the boundary of ROI
        # not that symmetry could be broken by user-provided ROI
        wx = self.images["spark watermark"].sum(axis=0)
        wy = self.images["spark watermark"].sum(axis=1)
        if wx[0]!=0 or wx[-1]!=0 or wy[0]!=0 or wy[-1]!=0:
            return False

        if strict:
            # check for symmetry if in strict mode
            for w in [wx, wy]:
                left, i = 0, 0
                while not w[i]:
                    left += 1
                    i += 1
                right, i = 0, 0
                while not w[-i]:
                    right += 1
                    i += 1
                if abs(left-right) > 1:
                    return False

        return True


    def remove(self):
        if self.store_results and self.database is not None:
            self.database.query("DELETE FROM " + self.database.table(Spark.database_table) +
                                " WHERE roi_id=:rid",
                                rid=self.roi_id)
