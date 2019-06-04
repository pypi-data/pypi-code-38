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
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QWidget

import gc
import os
import sys
import numpy as np

from iocbio.sparks.calc.spark import Spark
from iocbio.sparks.calc.synthetic import SyntheticData
from iocbio.sparks.handler.experiment import ExperimentHandler
from iocbio.sparks.handler.roi import ROIHandler
from iocbio.sparks.handler.image import Image
from iocbio.sparks.io.export import image_export

import iocbio.sparks.worker as worker
import iocbio.sparks.info as info
import iocbio.sparks.io.db as dbwrapper


class GroundTruth():
    database_table = 'ground_truth_experiment'

    @staticmethod
    def database_schema(db):
        db.query("CREATE TABLE IF NOT EXISTS " + db.table(GroundTruth.database_table) +
                 "(experiment_id text not null PRIMARY KEY, " +
                 "f0 DOUBLE PRECISION, gain DOUBLE PRECISION)")

    def __init__(self, database, experiment_id, f0, gain):

        self.database = database
        self.experiment_id = experiment_id
        self.f0 = f0
        self.gain = gain

        if self.database is not None:
            record_found = False
            for row in self.database.query("SELECT f0 FROM " +
                                           self.database.table(GroundTruth.database_table) +
                                           " WHERE experiment_id=:eid", eid=self.experiment_id):
                record_found = True

        if not record_found:
            self.database.query("INSERT INTO " + self.database.table(GroundTruth.database_table) +
                                "(experiment_id, f0, gain) " +
                                "VALUES(:eid, :f0, :gain)",
                                eid=self.experiment_id, f0=self.f0, gain=self.gain)


class Main(QWidget):

    def __init__(self, experiment_id, filename, comment, database, data, dx, dt, save_path=None):
        QWidget.__init__(self)

        self.dx = dx
        self.dt = dt
        self.save_path = save_path

        self.image = Image(data.T, dt, dx, experiment_id, database)
        raw_image_shape = self.image.raw.shape
        xdata = self.image.raw.mean(axis=1).astype(np.float64)
        transposed = 0

        self.experiment = ExperimentHandler(experiment_id, filename, comment,
                                            database,
                                            self.dt*(raw_image_shape[0]),
                                            self.dx*(raw_image_shape[1]),
                                            raw_image_shape[0], raw_image_shape[1],
                                            transposed,
                                            xdata, self.dt*np.arange(0, raw_image_shape[0]))

        QCoreApplication.processEvents()
        self.rois = ROIHandler(experiment_id=experiment_id,
                               database=database,
                               background=self.experiment.background,
                               image=self.image)

        self.image.sigImageNormalized.connect(self.detect)
        worker.workPool.sigJobNumberChanged.connect(self.onJobsNumberChanged)
        self.image.sigRoiAdd.connect(self.rois.add)

        info.infoHub.sigInfo.connect(self.print_info)
        info.infoHub.sigWarning.connect(self.print_info)
        info.infoHub.sigError.connect(self.print_info)

        QCoreApplication.processEvents()
        self.image.normalize(0, (self.image.raw.shape[0]-1)*dt)

    def detect(self, b):
        if b and self.image.get_slice('Filtered') is not None:
            print('Start detecting sparks')
            self.image.detect_sparks()
            if self.save_path is not None:
                key = 'Corrected Mean MedBlu'
                image_export(self.image.get_slice(key), os.path.join(self.save_path, '%s.tiff' % key))


    def onJobsNumberChanged(self, njobs):
        if njobs == 0:
            count = self.rois.cleanup_sparks(True)
            print('Removed sparks:', count)
            self.close()

    def print_info(self, header, short_message=None, long_message=None):
        s = header
        if short_message is not None:
            s += ' ' + short_message
        if long_message is not None:
            s += ' ' + long_message
        print(s)


def app(args, f0):

    dx = args.dx
    dt = args.dt
    lenx = args.lenx
    lent = args.lent
    freq = args.freq
    f_f0 = args.f_f0
    gain = args.gain

    QCoreApplication.setOrganizationName("iocbio")
    QCoreApplication.setApplicationName("sparks")

    info.infoHub = info.Info()
    worker.workPool = worker.Pool()

    database = dbwrapper.DatabaseInterface()

    try:
        # init database
        ExperimentHandler.database_schema(database, create_view=False) # requires sparks_data table to be present
        ROIHandler.database_schema(database)
        Spark.database_schema(database)
        Image.database_schema(database)
        ExperimentHandler.database_schema(database, create_view=True) # requires sparks_data table to be present
        GroundTruth.database_schema(database)
        SyntheticData.database_schema(database)
    except:
        print('Initilizing tables failed')
        database.close()
        exit()

    sd = SyntheticData(lenx, lent, dx, dt, f0, f_f0, gain=gain)
    sd.generate_data(spark_freq=freq)
    if args.save is not None:
        sd.save_image(os.path.join(args.save, 'synthetic_data_f0_%i.tiff' % (f0)))
    sd.update_database(database)

    data = sd.data
    gain = sd.gain
    experiment_id = sd.experiment_id
    filename = ''
    comment = args.comment
    print('Synthetic data:')
    print('\texperiment_id:', experiment_id)
    print('\tF0:', f0)
    print('\tcalculated gain:', gain)
    print('\tno sparks generated:', sd.nsparks)
    print('\timage min/max: %i/%i' % (data.min(), data.max()))

    GroundTruth(database, experiment_id, f0, gain)
    app = QApplication([])
    main_obj = Main(experiment_id, filename, comment, database, data, dx=dx*1.e-6, dt=dt*1.e-3, save_path=args.save)
    exit_code = app.exec_()

    database.close()
    worker.workPool.drop_all()
    gc.collect()

    return experiment_id


################################################################################
### Main entry point
################################################################################
def main():
    import argparse

    l = np.arange(0.05, 0.85, 0.05).tolist() + [1, 1.25, 1.5, 2]

    parser = argparse.ArgumentParser(description='''
IocBio calcium spark synthetic data analyser tool.

Use iocbio-spark to set database where synthetic data analysis results will be saved
and to set default analysis parameters.
''',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--dx', type=float, default=0.14, help='Pixel size in space in microns')
    parser.add_argument('--dt', type=float, default=1.53, help='Pixel size in time in milliseconds')
    parser.add_argument('--lenx', type=int, default=512, help='Experiment sizes in space in pixels')
    parser.add_argument('--lent', type=int, default=37000, help='Experiment sizes time in pixels')
    parser.add_argument('--freq', type=float, default=1.5, help='Sparks frequency in sparks per 100 microns per 1 second')
    parser.add_argument('--f0',  nargs='+', type=float, default=[1, 2, 3, 4, 6, 9, 12, 16], help='List of f0 values')
    parser.add_argument('--f_f0', nargs='+', type=float, default=l,#[0.1, 0.25, 0.5, 0.75, 1, 1.25],
                        help='List of spark relative amplitudes respect to f0. Example: --f_f0 0.05 0.15 0.2 0.3')
    parser.add_argument('--gain', type=float, help='Parameter for scaling synthetic data')
    parser.add_argument('-l', '--loops', type=int, default=1, help='Number of repetitions')
    parser.add_argument('-s', '--save', type=str, help='Path where to save synthetic data images')
    parser.add_argument('--comment', type=str, default='Synthetic data', help='Commentary regarding experiment')

    args = parser.parse_args()
    # print(args)

    for i in range(args.loops):
        for f0 in args.f0:
            app(args, f0)
        print(i+1, 'loops done.')


# if run as a script
if __name__ == '__main__':
    main()
