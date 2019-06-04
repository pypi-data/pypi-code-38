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

import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5 import QtCore
from iocbio.sparks.constants import application_name, database_table_experiment, database_table_roi, database_table_spark, database_table_stage, database_table_spark_extended

from ..calc.spark import Parameters as spark_Parameters
from ..calc.spark import Results as spark_Results
from ..handler.experiment import Parameters as stage_Parameters
from ..handler.experiment import Results as stage_Results

from PIL.Image import fromarray as toimage


def image_export(arr, name):
    dtypes = {'u': 'L'}
    if arr is None:
        print('Image is not ready for saving')
    else:
        mode = dtypes[arr.dtype.kind] if arr.dtype.kind in dtypes else 'F'
        image = toimage(arr, mode=dtypes[arr.dtype.kind] if arr.dtype.kind in dtypes else 'F')
        image.save(name)


def save_image(image, name, default_path=None, parent=None):
    if image is None:
        msg = QMessageBox()
        msg.setWindowTitle(application_name)
        msg.setText('Image "%s" is not ready for saving, still caluclating ...' % name)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        return default_path

    default_path = os.path.expanduser('~') if default_path is None else default_path
    newname, filetype = QFileDialog.getSaveFileName(parent,
                                                    caption='Save image',
                                                    directory=os.path.join(default_path, name.replace(' ', '_')),
                                                    filter='*.tiff')
    if newname == '':
        return default_path

    newname = newname+filetype[1:] if not newname.endswith(filetype[1:]) else newname
    image_export(image, newname)
    return os.path.dirname(newname)


def export_experiments(files_to_export, database, out_file, ftype):
    Export2xls(out_file, files_to_export, database)


class Export2xls(object):

    def __init__(self, out_file, filenames, database):
        import xlsxwriter

        self.filenames = filenames
        self.out_file = out_file
        self.db = database

        # Create a workbook and add worksheets
        self.workbook = xlsxwriter.Workbook(self.out_file)
        self.bold_cell_format = self.workbook.add_format({'bold': True})

        self.write_experiment_sheet()
        self.write_spark_sheet(database_table_spark_extended)
        self.write_spark_sheet(database_table_spark)
        self.write_stage_sheet()

        self.workbook.close()

    def write_experiment_sheet(self):
        table = self.db.table(database_table_experiment)
        sheet = self.workbook.add_worksheet(database_table_experiment)

        filenames = "('%s')" % self.filenames[0] if len(self.filenames) == 1 else str(tuple(self.filenames))
        self.experiment_records = list(self.db.query("SELECT * FROM " + table +
                                       " WHERE filename IN " + filenames +
                                       " ORDER BY filename ASC"))

        show_keys = [x for x in self.experiment_records[0].keys() if x != 'experiment_id']

        # Prepare header
        row = 0
        for i, key in enumerate(show_keys):
            sheet.write(row, i, key, self.bold_cell_format)

        # Write data
        for experiment in self.experiment_records:
            row += 1
            for i, key in enumerate(show_keys):
                sheet.write(row, i, experiment[key])

    def write_spark_sheet(self, table_name):
        sheet = self.workbook.add_worksheet(table_name)
        show_keys = self.db.get_table_column_names(table_name)
        if show_keys is None:
            return
        show_keys.sort()

        # Prepare header
        sheet.write(0, 0, 'Database key:', self.bold_cell_format)
        sheet.write(1, 0, 'Parameter:', self.bold_cell_format)
        sheet.write(2, 0, 'Unit:', self.bold_cell_format)

        for i, key in enumerate(['filename', 'spark no'] + show_keys):
            sheet.write(0, i+1, key, self.bold_cell_format)

            if key in spark_Parameters:
                sheet.write(1, i+1, spark_Parameters[key].human_long, self.bold_cell_format)

            if key in spark_Results:
                sheet.write(1, i+1, spark_Results[key].human_long, self.bold_cell_format)
                sheet.write(2, i+1, spark_Results[key].unit, self.bold_cell_format)

        row = 2
        for experiment in self.experiment_records:
            c = list(self.db.query("SELECT " + (', ').join(['s.%s as %s' %(x,x) for x in show_keys]) + " FROM "
                                   + self.db.table(table_name) + " s INNER JOIN %s r ON" % self.db.table(database_table_roi) +
                                   " s.roi_id=r.roi_id WHERE r.experiment_id=:eid ORDER BY r.x0, r.x1 ASC",
                                   eid=experiment['experiment_id']))

            for k, spark in enumerate(c):
                row += 1
                sheet.write(row, 1, experiment['filename'])
                sheet.write(row, 2, k+1)
                for j, key in enumerate(show_keys):
                    sheet.write(row, j+3, spark[key])
            row += 1

    def write_stage_sheet(self):
        table = self.db.table(database_table_stage)
        sheet = self.workbook.add_worksheet(database_table_stage)
        show_keys = self.db.get_table_column_names(database_table_stage)
        if show_keys is None:
            return
        show_keys.sort()

        # Prepare header
        sheet.write(0, 0, 'Database key:', self.bold_cell_format)
        sheet.write(1, 0, 'Parameter:', self.bold_cell_format)
        sheet.write(2, 0, 'Unit:', self.bold_cell_format)

        for i, key in enumerate(['filename'] + show_keys):
            sheet.write(0, i+1, key, self.bold_cell_format)

            if key in stage_Parameters:
                sheet.write(1, i+1, stage_Parameters[key].human, self.bold_cell_format)

            if key in stage_Results:
                sheet.write(1, i+1, stage_Results[key].human, self.bold_cell_format)
                sheet.write(2, i+1, stage_Results[key].unit, self.bold_cell_format)

        row = 2
        for experiment in self.experiment_records:
            c = list(self.db.query("SELECT * FROM " + table +
                                   " WHERE experiment_id=:eid ORDER BY start, " + '"end"' + " ASC", eid=experiment['experiment_id']))
            for stage in c:
                row += 1
                sheet.write(row, 1, experiment['filename'])
                for j, key in enumerate(show_keys):
                    sheet.write(row, j+2, stage[key])
            row += 1
