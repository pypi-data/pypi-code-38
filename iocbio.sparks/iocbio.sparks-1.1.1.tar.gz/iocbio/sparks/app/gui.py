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
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QSettings, QCoreApplication, QStandardPaths
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtGui import QIcon, QPixmap
import hashlib, traceback, gc

from iocbio.sparks.constants import application_name
from iocbio.sparks.handler.experiment import ExperimentHandler

import iocbio.sparks.worker as worker
import iocbio.sparks.info as info
import iocbio.sparks.io.db as dbwrapper

################################################################################
### Main app function
################################################################################

def app(args):
    from tifffile.tifffile import TiffFile
    from iocbio.sparks.gui.mainwindow import MainGUI
    from iocbio.sparks.gui.experiment_browser import OpenExperiment, ConnectDatabaseGUI
    from iocbio.sparks.gui.import_image import ImportImage
    from iocbio.sparks.handler.experiment import ExperimentHandler
    from iocbio.sparks.handler.roi import ROIHandler
    from iocbio.sparks.calc.spark import Spark
    from iocbio.sparks.handler.image import Image
    import os, sys

    QCoreApplication.setOrganizationName("iocbio")
    QCoreApplication.setApplicationName("sparks")

    info.infoHub = info.Info()
    worker.workPool = worker.Pool()

    # start app
    app = QApplication([])
    settings = QSettings()

    repeat = True
    show_connect_dialog = False
    reopen_readwrite = None
    devel_mode = (int(settings.value("development/exceptions_crash", 0)) > 0)

    splash_pixmap = QPixmap( os.path.join( os.path.dirname(os.path.realpath(__file__)), 'splash.png') )
    window_icon = QIcon( os.path.join( os.path.dirname(os.path.realpath(__file__)), 'icon.png') )

    # set window icon
    app.setWindowIcon(window_icon)

    while repeat:

        if not show_connect_dialog:
            try:
                database = dbwrapper.DatabaseInterface()
            except Exception as e:
                errtxt = 'Error occurred:\n\n' + str(e) + "\n\n" + str(e)
                print('\n' + errtxt + '\n\n')
                print(traceback.format_exc())
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle(application_name + ": Error")
                msg.setInformativeText(errtxt)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
                show_connect_dialog = True

        if show_connect_dialog or not database.is_ok:
            show_connect_dialog = False
            connect = ConnectDatabaseGUI()
            connect.show()
            exit_code = app.exec_()
            connect.deleteLater()
            if connect.save_settings:
                continue
            else:
                sys.exit(exit_code)

        try:
            # init database
            ExperimentHandler.database_schema(database, create_view=False) # requires sparks_data table to be present
            ROIHandler.database_schema(database)
            Image.database_schema(database)
            Spark.database_schema(database)
            ExperimentHandler.database_schema(database, create_view=True) # requires sparks_data table to be present

            readonly_mode = ((int(settings.value(OpenExperiment.settingReadOnly, 0)) > 0) and reopen_readwrite is None)
            readonly_apply = True

            if reopen_readwrite is not None:
                file_name = reopen_readwrite
            else:
                file_name = args.file_name
            # If file_name is not given then database experiment browser is lauched
            if file_name is None:
                readonly_apply = False
                browser = OpenExperiment(database)
                browser.show()
                exit_code = app.exec_()
                browser.deleteLater()
                file_name = browser.filename
                show_connect_dialog = browser.connect_to_new_db
                if show_connect_dialog:
                    continue

                if file_name is None:
                    sys.exit(exit_code)

            transposed = 0
            file_name = os.path.abspath(file_name)

            with TiffFile(file_name) as tif:
                if tif.is_lsm is True:
                    data = tif.asarray()[:,0,0,0,:]
                    dx = tif.lsm_metadata['VoxelSizeX'] # in meters #* 1e6 # in microns
                    dt = tif.lsm_metadata['TimeIntervall'] # in seconds * 1000 # in milli seconds
                    dimX = tif.lsm_metadata['DimensionX']
                    dimTime = tif.lsm_metadata['DimensionTime']
                    experiment_id = hashlib.sha256(data.tostring()).hexdigest()

                # elif tif.is_ome is True:
                #     raise NotImplementedError('OME TIF support is not yet implemented')
                #     for it in tif.ome_metadata['Image'].items():
                #         print(it)
                #     data = tif.asarray()
                else:
                    data = tif.asarray()
                    experiment_id = hashlib.sha256(data.tostring()).hexdigest()
                    importer = ImportImage(database, experiment_id, data)
                    if importer.new_record:
                        importer.show()
                        exit_code = app.exec_()

                    if importer.start_analysis is False:
                        sys.exit(exit_code)
                    data, dx, dt, dimX, dimTime, transposed = importer.metadata

            print('File name:', file_name)
            print('\tData PixelSizeX:', dx, 'meters')
            print('\tData TimeInterval:', dt, 'seconds')
            print('\tPixels in X:', dimX)
            print('\tPixels in Time:', dimTime)
            print('\tExperiment ID:', experiment_id, '\n')

            # readin comments if given by file
            if args.commentfile is not None:
                 with open(args.commentfile, 'r') as f:
                     args.comment = f.read()

            # start splashscreen
            app.processEvents()
            splash = QSplashScreen(splash_pixmap)
            splash.show()
            splash.showMessage("%s: Loading dataset" % application_name, Qt.AlignBottom | Qt.AlignCenter, Qt.white)
            app.processEvents()

            # set to readonly if its in the settings, we have data in the database already, and user was opening using cmd line arguments
            if readonly_apply:
                if ExperimentHandler.has_record(database, experiment_id):
                    database.read_only = readonly_mode
                else:
                    database.read_only = False

            if not database.read_only or ExperimentHandler.has_record(database, experiment_id):
                gui_obj = MainGUI(experiment_id, file_name,
                                  args.comment,
                                  database, data.T, dx, dt, transposed)
                gui_obj.show()
                splash.finish(gui_obj)
                exit_code = app.exec_()
                info.infoHub.disconnect()
                worker.workPool.disconnect()

                repeat = gui_obj.phoenix
                if gui_obj.readwrite_reopen:
                    reopen_readwrite = file_name
                    repeat = True
                else:
                    reopen_readwrite = None

                del splash
                del gui_obj
                splash = None

                gc.collect()

            else:
                repeat = True

                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle(application_name + ": Read only mode")
                msg.setInformativeText("You cannot open the dataset in read-only mode when it is not available in the database.\n\n" +
                                       "Please either set read-write mode or open the dataset that is in the database already")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

        # catch exceptions and show them on terminal and GUI
        except Exception as e:
            errtxt = 'Error occurred:\n\n' + str(e) + "\n\n" + str(type(e))
            print('\n' + errtxt + '\n\n')
            print(traceback.format_exc())

            if devel_mode:
                sys.exit(-1)

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle(application_name + ": Error")
            msg.setInformativeText(errtxt)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

        database.close()
        worker.workPool.drop_all()
        args.file_name, args.commen, args.commentfile = None, None, None

    sys.exit(exit_code)


################################################################################
### Main entry point
################################################################################
def main():
    import argparse, sys

    parser = argparse.ArgumentParser(description='IocBio calcium spark analyser tool')
    parser.add_argument('file_name', nargs='?', type=str, help='Input file')
    parser.add_argument('--comment', type=str, default='', help='Commentary regarding experiment')
    parser.add_argument('--commentfile', type=str, help='Text file with the commentary regarding experiment')
    args = parser.parse_args()

    app(args)

# if run as a script
if __name__ == '__main__':
    main()
