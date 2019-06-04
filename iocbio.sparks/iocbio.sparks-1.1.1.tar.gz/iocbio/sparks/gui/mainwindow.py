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
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QSettings, QByteArray, QCoreApplication
from PyQt5.QtWidgets import QWidget, QMainWindow, QHBoxLayout, QVBoxLayout, QSplitter, QTabWidget, QPushButton
from PyQt5.QtWidgets import QMessageBox, QCheckBox, QScrollArea, QSystemTrayIcon, QStyle, QApplication
from PyQt5.QtGui import QPalette, QIcon
import pyqtgraph as pg
import numpy as np
import os

from iocbio.sparks.constants import application_name
from ..handler.experiment import ExperimentHandler
from ..handler.roi import ROIHandler
from ..handler.image import Image, NormalizationParameters, SparkDetectorParameters
from .spark_plot import SparkPlot
from .experiment_plot import AverageIntensityPlot
from .overview_plot import OverViewPlot
from .histogram_plot import Histogram
from .custom_widgets import ImageAdjustments, ParametersSetter, SunkenHLine, SmallLabel, XYPlot
from .custom_widgets import SparksListView, SparksStatsView, CommentEdit, StagesEdit, MainWindowStatusBar
from ..calc.spark import Spark
from .experiment_browser import ExportExperiment
from ..io.export import export_experiments

import iocbio.sparks.worker as worker
import iocbio.sparks.info as info


class MainGUI(QMainWindow):
    sigShiftOverViewPlot = pyqtSignal(Qt.Key)

    settingLowerSplitter = "Main GUI/lower splitter"
    settingMainSplitter = "Main GUI/main splitter"
    settingGeometry = "Main GUI/geometry"
    settingShowLabels = "Main GUI/show labels"
    settingLookuptableName = "Main GUI/lookup table name"

    def __init__(self, experiment_id, filename, comment, database, data, dx, dt, transposed):
        QMainWindow.__init__(self)

        self.phoenix = False
        self.readwrite_reopen = False

        self.dx = dx
        self.dt = dt
        self.image = Image(data.T, dt, dx, experiment_id, database)
        raw_image_shape = self.image.raw.shape

        # { Setting graphics general properites
        pg.setConfigOption('antialias', True)
        pg.setConfigOption('background', self.palette().color(QPalette.Window))
        pg.setConfigOption('foreground', '000000')
        # }

        # init data
        xdata = self.image.raw.mean(axis=1).astype(np.float64)

        self.experiment = ExperimentHandler(experiment_id, filename, comment,
                                            database,
                                            self.dt*(raw_image_shape[0]),
                                            self.dx*(raw_image_shape[1]),
                                            raw_image_shape[0], raw_image_shape[1],
                                            transposed,
                                            xdata, self.dt*np.arange(0, raw_image_shape[0]))

        QCoreApplication.processEvents()
        self.image.normalize(*self.experiment.analysis_range)

        QCoreApplication.processEvents()
        self.rois = ROIHandler(experiment_id=experiment_id,
                               database=database,
                               background=self.experiment.background,
                               image=self.image)

        QCoreApplication.processEvents()

        self.spark_plot = SparkPlot(self.dx, self.dt)
        self.average_intensity_plot = AverageIntensityPlot(xdata,
                                                           self.dt*np.arange(0, raw_image_shape[0]),
                                                           self.experiment.analysis_range)
        self.histogram_whole_data = Histogram(title='Histogram: full experiment')
        self.histogram_analysis_range = Histogram(title='Histogram: analyzed range')
        self.background_correction_plot = XYPlot(title='Normalized background SD',
                                                 label={'position':'bottom', 'name': 'space', 'units': 'microns'})
        self.overview_plot = OverViewPlot(self.image)
        overview_plot_show_labels = QCheckBox('Show labels')
        overview_plot_show_labels.setTristate(False)

        self.setWindowTitle('%s: %s' % (application_name, filename))

        self.status_bar = MainWindowStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.update_rw_status(not database.read_only)

        main_layout = QVBoxLayout()

        self.sparks_list_view = SparksListView()
        self.spark_stats_view = SparksStatsView()

        self.export_experiment_browser = ExportExperiment(database)

        detect_btn = QPushButton('Detect')
        self.cleanup_btn = QPushButton('Cleanup')
        recalc_btn = QPushButton('Recalc')
        export_btn = QPushButton('Export')
        copy_exp_id_btn = QPushButton('ID')
        reopen_readwrite_btn = QPushButton('Read/Write')
        openfile_btn = QPushButton('Open')

        detect_btn.setEnabled(self.image.image_normalized())
        self.cleanup_btn.setEnabled(False)

        # load settings
        settings = QSettings()

        # { Controls
        controls_tabs = QTabWidget()
        vmin = int(self.image.raw.min())
        vmax = int(np.percentile(self.image.raw, 99))

        image_adjustments = ImageAdjustments(label='Set image intesity levels',
                                             vmin=vmin,
                                             vmax=vmax,
                                             levels_range=(min(0, self.image.raw.min()), self.image.raw.max()),
                                             manualtextsize=70,
                                             lut_name=settings.value(MainGUI.settingLookuptableName))

        self.overview_plot.set_levels(*image_adjustments.image_levels.get_levels)
        self.overview_plot.update_analysis_region(self.experiment.analysis_range)
        self.overview_plot.set_lut(image_adjustments.lut.get_current_colormap)
        self.spark_plot.set_image_levels(*image_adjustments.spark_levels.get_levels)
        self.spark_plot.set_lut(image_adjustments.lut.get_current_colormap)
        self.parameters_setter = ParametersSetter(Spark.Parameters, NormalizationParameters, SparkDetectorParameters)
        self.update_parameters_setter(self.image)

        image_adjustment_scroll_layout = QScrollArea()
        image_adjustment_scroll_layout.setWidgetResizable(True)
        image_adjustment_scroll_layout.setWidget(image_adjustments)

        comments = CommentEdit(self.experiment.comment)

        stages = StagesEdit()
        controls_tabs.addTab(self.parameters_setter, 'Parameters')
        controls_tabs.addTab(stages, 'Experiment stages')
        controls_tabs.addTab(image_adjustment_scroll_layout, 'Adjust images')
        controls_tabs.addTab(comments, 'Comments')
        # }

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon( QIcon(os.path.join( os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'app', 'tray_icon.png')) )

        # { Event bindings
        self.image.sigUpdated.connect(self.overview_plot.update_current_image)
        self.image.sigRoiAdd.connect(self.rois.add)
        self.image.sigImageNormalized.connect(detect_btn.setEnabled)
        self.image.sigImageNormalized.connect(self.update_background_correction_plot)

        self.overview_plot.sigRoiAdd.connect(self.rois.add)
        self.overview_plot.sigRoiChanged.connect(self.rois.update_roi)
        self.overview_plot.sigRoiRemove.connect(self.rois.remove)
        self.overview_plot.sigActiveRoi.connect(self.rois.set_active)
        overview_plot_show_labels.stateChanged.connect(self.overview_plot.set_roi_labels_visible)

        self.sparks_list_view.sigSparkRemove.connect(self.rois.remove)
        self.sparks_list_view.sigActiveSpark.connect(self.rois.set_active)

        self.rois.sigRois.connect(self.overview_plot.set_rois)
        self.rois.sigRois.connect(self.sparks_list_view.set_list)
        self.rois.sigActiveRoi.connect(self.overview_plot.set_active_roi)
        self.rois.sigActiveRoi.connect(self.sparks_list_view.set_active)
        self.rois.sigActiveSpark.connect(self.spark_plot.set_spark)
        self.rois.sigActiveSpark.connect(self.spark_stats_view.set_spark)
        self.rois.sigActiveSpark.connect(self.update_parameters_setter)

        image_adjustments.image_levels.sigValueChanged.connect(self.overview_plot.set_levels)
        image_adjustments.spark_levels.sigValueChanged.connect(self.spark_plot.set_image_levels)
        image_adjustments.lut.sigUpdate.connect(self.overview_plot.set_lut)
        image_adjustments.lut.sigUpdate.connect(self.spark_plot.set_lut)

        self.parameters_setter.sigParametersChanged.connect(self.update_parameters)

        self.average_intensity_plot.sigAnalysisRegionChange.connect(self.overview_plot.update_analysis_region)
        self.average_intensity_plot.sigAnalysisRegionChangeFinished.connect(self.experiment.set_analysis_range)
        self.average_intensity_plot.sigAnalysisRegionChangeFinished.connect(lambda rng: self.image.normalize(*rng))
        self.average_intensity_plot.sigAnalysisRegionChangeFinished.connect(lambda rng: self.histogram_analysis_range.set_data(self.image.get_raw_time_slice(*rng)))
        self.average_intensity_plot.sigStageRangeChanged.connect(self.experiment.update_stage_range)

        self.experiment.sigStages.connect(stages.update_stages)
        self.experiment.sigStages.connect(self.average_intensity_plot.update_stages)
        self.experiment.sigStages.connect(self.overview_plot.update_stages)
        comments.sigCommentChanged.connect(lambda x: self.experiment.set(comment=x))

        worker.workPool.sigJobNumberChanged.connect(self.onJobsNumberChanged)

        self.overview_plot.sigZoomXChanged.connect(self.average_intensity_plot.update_zoom_range)
        self.sigShiftOverViewPlot.connect(self.overview_plot.shift_plot_item_time)

        stages.sigNameChanged.connect(self.experiment.update_stage_name)
        stages.sigAdd.connect(self.experiment.add_stage)
        stages.sigRemove.connect(self.experiment.remove_stage)

        info.infoHub.sigInfo.connect(self.show_new_info)
        info.infoHub.sigWarning.connect(self.show_new_warning)
        info.infoHub.sigError.connect(self.raise_error_dialog)

        detect_btn.clicked.connect(self.image.detect_sparks)
        self.cleanup_btn.clicked.connect(self.rois.cleanup_sparks_gui)
        recalc_btn.clicked.connect(self.recalc_all_sparks)
        copy_exp_id_btn.clicked.connect(self.copy_exp_id)
        export_btn.clicked.connect(self.show_export_experiments_browser)
        reopen_readwrite_btn.clicked.connect(self.open_readwrite)
        openfile_btn.clicked.connect(self.open_new_file)

        self.export_experiment_browser.sigExportRequest.connect(export_experiments)
        # }

        self.rois.trigger_updates()
        self.experiment.trigger_updates()

        # {If read only
        self.read_only = database.read_only
        if database.read_only:
            self.average_intensity_plot.set_read_only(True)
            self.overview_plot.set_read_only(True)
            self.sparks_list_view.set_read_only(True)
            self.parameters_setter.set_read_only(True)
            stages.set_read_only(True)
            comments.set_read_only(True)
            recalc_btn.setEnabled(False)
            self.image.sigImageNormalized.disconnect(detect_btn.setEnabled)
            detect_btn.setEnabled(False)

        # }

        upper_layout = QHBoxLayout()
        upper_layout.addWidget(self.average_intensity_plot, 4)
        upper_layout.addWidget(self.histogram_analysis_range, 1)
        upper_layout.addWidget(self.histogram_whole_data, 1)
        upper_layout.addWidget(self.background_correction_plot, 1)
        upper_widget = QWidget()
        upper_widget.setLayout(upper_layout)

        action_buttons_layout = QVBoxLayout()
        action_buttons_layout.addWidget(overview_plot_show_labels)
        action_buttons_layout.addWidget(detect_btn)
        action_buttons_layout.addWidget(SmallLabel('Auto-detect sparks in current experiment'))
        action_buttons_layout.addWidget(self.cleanup_btn)
        action_buttons_layout.addWidget(SmallLabel('Remove sparks with the inconsistent positioning'))
        action_buttons_layout.addWidget(recalc_btn)
        action_buttons_layout.addWidget(SmallLabel('Recalculate all sparks in current experiment'))
        action_buttons_layout.addWidget(copy_exp_id_btn)
        action_buttons_layout.addWidget(SmallLabel('Copy experiment id to clipboard'))
        action_buttons_layout.addWidget(export_btn)
        action_buttons_layout.addWidget(SmallLabel('Export experiments to *.xlsx'))
        if database.read_only:
            action_buttons_layout.addWidget(reopen_readwrite_btn)
            action_buttons_layout.addWidget(SmallLabel('Re-open this experiment in read-write mode'))
        action_buttons_layout.addWidget(openfile_btn)
        action_buttons_layout.addWidget(SmallLabel('Open a new experiment'))
        action_buttons_layout.addStretch(1)

        lower_left_widget = QWidget()
        lower_left_layout = QHBoxLayout()
        lower_left_layout.addLayout(action_buttons_layout)
        lower_left_layout.addWidget(self.sparks_list_view)
        lower_left_layout.addWidget(self.spark_plot, 1)
        m = lower_left_layout.getContentsMargins()
        lower_left_layout.setContentsMargins(m[0], 0, m[2], 0)
        lower_left_widget.setLayout(lower_left_layout)

        self.lower_splitter = QSplitter(Qt.Horizontal)
        self.lower_splitter.addWidget(lower_left_widget)
        self.lower_splitter.addWidget(self.spark_stats_view)
        self.lower_splitter.addWidget(controls_tabs)

        self.main_splitter = QSplitter(Qt.Vertical)
        self.main_splitter.addWidget(upper_widget)
        self.main_splitter.addWidget(self.overview_plot)
        self.main_splitter.addWidget(self.lower_splitter)
        main_layout.addWidget(self.main_splitter)

        # create content area widget for padding
        main_content_widget = QWidget()
        main_content_widget.setLayout(main_layout)
        # set the central widget
        self.setCentralWidget(main_content_widget)

        self.onJobsNumberChanged(worker.workPool.jobs())

        # appling window geometry settings
        self.lower_splitter.restoreState(settings.value(MainGUI.settingLowerSplitter, QByteArray()))
        self.main_splitter.restoreState(settings.value(MainGUI.settingMainSplitter, QByteArray()))
        self.restoreGeometry(settings.value(MainGUI.settingGeometry, QByteArray()))

        try:
            v = bool(int(settings.value(MainGUI.settingShowLabels)))
        except:
            v = True

        if v:
            overview_plot_show_labels.setCheckState(Qt.Checked)
        else:
            overview_plot_show_labels.setCheckState(Qt.Unchecked)
        self.overview_plot.set_roi_labels_visible(v)

        self.histogram_whole_data.set_data(self.image.raw)
        x0, x1 = self.experiment.analysis_range
        self.histogram_analysis_range.set_data(self.image.raw[int(round(x0/self.dt)): int(round(x1/self.dt))])

    def copy_exp_id(self):
        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(self.experiment.experiment_id, mode=cb.Clipboard)

    def open_new_file(self):
        self.phoenix = True
        self.close()

    def open_readwrite(self):
        self.readwrite_reopen = True
        self.close()

    def raise_error_dialog(self, header, short_message, long_message):
        msg = QMessageBox()
        msg.setWindowTitle(header)
        msg.setInformativeText(short_message)
        msg.setDetailedText(long_message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_new_info(self, message):
        self.status_bar.update_message(message)

    def show_new_warning(self, message):
        self.status_bar.update_message(message, interval=2)

    def onJobsNumberChanged(self, njobs):
        if njobs == 0:
            self.cleanup_btn.setEnabled(True)
            self.tray_icon.hide()
        else:
            self.cleanup_btn.setEnabled(False)
            message = 'Active jobs: %s' % njobs
            self.tray_icon.setToolTip(message)
            self.tray_icon.show()

        self.status_bar.update_jobs_status(njobs)

    def show_export_experiments_browser(self):
        self.export_experiment_browser.update_expeiment_table()
        self.export_experiment_browser.show()

    def recalc_all_sparks(self):
        self.rois.update_current_spark({})
        self.rois.update_noncurrent_sparks({})

    def update_parameters(self, mode, spark_params, image_params, auto_detect_params):
        if mode == 'image' or mode == 'auto_detect' or  mode == 'all':
            image_params.update(auto_detect_params)
            self.image.normalize(*self.experiment.analysis_range, **image_params)
            self.rois.update_current_spark(spark_params)
            self.rois.update_noncurrent_sparks(spark_params)

        elif mode == 'spark':
            self.rois.update_current_spark(spark_params)

        else:
            raise KeyError('No such mode found, mode:' % mode)

    def update_background_correction_plot(self, b):
        if b is False:
            return

        x = self.dx*1e6*np.arange(self.image.raw.shape[1])
        corr_mean = self.image.get_slice('Corrected Background Mean')
        corr_meansd = self.image.get_slice('Corrected Background MeanSD')

        if corr_mean is not None and corr_meansd is not None:
            d = {
                'Corr Mean': {'x': x, 'y': corr_mean/np.median(corr_mean)},
                'Corr MeanSD': {'x': x, 'y': corr_meansd/np.median(corr_meansd)},
            }
            self.background_correction_plot.set_data(d)

    def update_parameters_setter(self, obj):
        d = {}
        if obj is not None:
            if isinstance(obj, Spark):
                for k in Spark.Parameters.keys():
                    d[k] = getattr(obj, k)

            if isinstance(obj, Image):
                for k in NormalizationParameters.keys():
                    d[k] = obj.normalization_parameters[k]
                for k in SparkDetectorParameters.keys():
                    d[k] = obj.normalization_parameters[k]

            self.parameters_setter.set_values(d)

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_PageUp, Qt.Key_PageDown,
                           Qt.Key_Right, Qt.Key_Left,
                           Qt.Key_Plus, Qt.Key_Minus,
                           Qt.Key_Home, Qt.Key_End,
                           Qt.Key_0]:
            self.sigShiftOverViewPlot.emit(event.key())

    def resizeEvent(self, event):
        event.accept()

    def closeEvent(self, event):
        quit = True

        if worker.workPool.jobs() > 0 and not self.read_only:
            msg = QMessageBox()
            msg.setWindowTitle('Calculations still running')
            msg.setInformativeText('Do you want to quit?')
            msg.setText('Calculations are still running!')
            msg.setIcon(QMessageBox.Warning)
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            ret = msg.exec_()
            if ret == QMessageBox.Cancel:
                quit = False

        if quit:
            settings = QSettings()
            settings.setValue(MainGUI.settingLowerSplitter, self.lower_splitter.saveState())
            settings.setValue(MainGUI.settingMainSplitter, self.main_splitter.saveState())
            settings.setValue(MainGUI.settingGeometry, self.saveGeometry())
            settings.setValue(MainGUI.settingShowLabels, int(self.overview_plot.show_roi_labels))
            settings.setValue(MainGUI.settingLookuptableName, self.findChild(ImageAdjustments).lut.get_current_lut_name)
            event.accept()
        else:
            event.ignore()
