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
from .. calc.spark import Spark
from .experiment import ExperimentHandler
from iocbio.sparks.constants import database_table_roi

from PyQt5.QtCore import pyqtSignal, QObject, QCoreApplication
from PyQt5.QtWidgets import QMessageBox

import iocbio.sparks.info as info

class ROIHandler(QObject):
    """ class that holds ROIs """

    sigRois = pyqtSignal(dict, list)

    sigActiveRoi = pyqtSignal(str)
    sigActiveSpark = pyqtSignal(Spark, list)

    database_table = database_table_roi

    @staticmethod
    def database_schema(db):
        db.query("CREATE TABLE IF NOT EXISTS " + db.table(ROIHandler.database_table) +
                 "(experiment_id text, roi_id text PRIMARY KEY, " +
                 "x0 integer, y0 integer, x1 integer, y1 integer, FOREIGN KEY (experiment_id) REFERENCES " +
                 db.table(ExperimentHandler.database_table) + "(experiment_id) ON DELETE CASCADE)")

    def __init__(self, experiment_id, database, background, image):
        QObject.__init__(self)

        self.database = database
        self.experiment_id = experiment_id
        self.rois = {}
        self.current_roi = None

        self.image = image

        if self.database is not None:
            for row in self.database.query("SELECT roi_id, x0, y0, x1, y1 FROM " +
                                           self.database.table(ROIHandler.database_table) +
                                           " WHERE experiment_id=:eid", eid=self.experiment_id):
                roi_id = row['roi_id']
                x0 = row['x0']
                y0 = row['y0']
                x1 = row['x1']
                y1 = row['y1']
                coords = (x0, y0, x1, y1)
                self.rois[roi_id] = { 'id': roi_id,
                                      'data coordinates': coords,
                                      'spark': Spark(self.experiment_id, roi_id, self.database,
                                                     self.image,
                                                     coords) }

        if bool(self.rois):
            self.current_roi = self.sorted_roi_list[0]

    def trigger_updates(self):
        self.sigRois.emit(self.rois, self.sorted_roi_list)
        self.sigActiveRoi.emit(self.current_roi)
        if self.current_roi is not None:
            self.sigActiveSpark.emit(self.rois[self.current_roi]['spark'],
                                     list(self.rois[self.current_roi]['data coordinates']))

    def add(self, coords, setactive=True):
        import uuid

        x0, y0, x1, y1 = coords
        roi_id = str(uuid.uuid4())

        if self.database is not None:
            self.database.query("INSERT INTO " + self.database.table(ROIHandler.database_table) +
                                "(experiment_id, roi_id, x0, y0, x1, y1) VALUES (:eid, :rid, :x0, :y0, :x1, :y1)",
                                eid=self.experiment_id, rid=roi_id, x0=x0, y0=y0, x1=x1, y1=y1)

        self.rois[roi_id] = { 'id': roi_id,
                              'data coordinates': coords,
                              'spark': Spark(self.experiment_id, roi_id, self.database,
                                             self.image,
                                             coords) }

        self.sigRois.emit(self.rois, self.sorted_roi_list)
        if setactive:
            self.set_active(roi_id)

    def remove(self, roi_id):
        def removekey(d, key):
            r = dict(d)
            del r[key]
            return r

        clist = self.sorted_roi_list
        index = clist.index(roi_id)

        self.rois[roi_id]['spark'].remove()

        if self.database is not None:
            self.database.query("DELETE FROM " + self.database.table(ROIHandler.database_table) +
                                " WHERE roi_id=:rid",
                                rid=roi_id)

        self.rois = removekey(self.rois, roi_id)
        self.sigRois.emit(self.rois, self.sorted_roi_list)
        if len(clist) > 1:
            if index>0:
                n = clist[index-1]
            else:
                n = clist[1]
        else:
            n = None
        self.set_active(n)

    def update_roi(self, roi_id, coords):
        x0, y0, x1, y1 = coords
        #roi_id = roi.roi_id
        self.rois[roi_id]['data coordinates'] = coords
        self.rois[roi_id]['spark'].set_coords(coords)
        self.rois[roi_id]['spark'].analyze(store_result=True)

        if self.database is not None:
            self.database.query("UPDATE " + self.database.table(ROIHandler.database_table) +
                                " SET x0=:x0, y0=:y0, x1=:x1, y1=:y1 WHERE roi_id=:rid",
                                x0=x0, y0=y0, x1=x1, y1=y1, rid=roi_id)

        if roi_id == self.current_roi:
            self.sigActiveSpark.emit(self.rois[self.current_roi]['spark'],
                                     list(self.rois[self.current_roi]['data coordinates']))


    def set_active(self, roi_id):
        if self.current_roi == roi_id or (roi_id not in self.rois and roi_id is not None):
            return

        self.current_roi = roi_id
        self.sigActiveRoi.emit(roi_id)
        if roi_id is not None:
            self.sigActiveSpark.emit(self.rois[self.current_roi]['spark'],
                                     list(self.rois[self.current_roi]['data coordinates']))
        else:
            self.sigActiveSpark.emit(None, [])

    def cleanup_sparks(self, autodetect_only):
        keys = self.rois.keys()
        counter = 0
        for k in keys:
            QCoreApplication.processEvents()
            if not self.rois[k]['spark'].checkIfAnalysisIsOK(strict=autodetect_only):
                print('Removing spark:', k)
                self.remove(k)
                counter += 1
        return counter

    def cleanup_sparks_gui(self):
        autodetect_only = ( QMessageBox.question(None,
                                                 "Cleanup action",
                                                 "Are the current sparks detected automatically without " +
                                                 "any of manual corrections of regions defining sparks?",
                                                 QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes )
        msg = QMessageBox()
        msg.setWindowTitle("Checking sparks regions")
        msg.setInformativeText("Please wait")
        msg.setDetailedText("It will take some time")
        msg.setStandardButtons(QMessageBox.NoButton)
        msg.setModal(True)
        msg.show()

        counter = self.cleanup_sparks(autodetect_only)

        info.info("Cleanup: removed {} sparks".format(counter))
        msg.deleteLater()

    def update_current_spark(self, updated_parameters):
        if self.current_roi is not None and self.current_roi in self.rois:
            self.rois[self.current_roi]['spark'].analyze(updated_parameters=updated_parameters)

    def update_noncurrent_sparks(self, updated_parameters):
        for k, v in self.rois.items():
            if k != self.current_roi:
                v['spark'].analyze(updated_parameters=updated_parameters)

    @property
    def sorted_roi_list(self):
        if self.database is None:
            return []
        else:
            return [el[0] for el in self.database.query("SELECT roi_id FROM " +
                                                        self.database.table(ROIHandler.database_table) +
                                                        " WHERE experiment_id=:eid ORDER BY x0, x1 ASC", eid=self.experiment_id )]
