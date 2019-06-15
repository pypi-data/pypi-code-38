from glue.config import importer
from glue.utils.qt.helpers import load_ui

from ...core.experiment import MappingExperiment

from ...filters.denoise import DenoiseFilter, UniformFilter, GaussianFilter
from ...io.loader import PickleLoader, DefaultLoader
from ...composite import CompositeChannels
from ...composite.segmentation import SlicSegmenter
from ...glue.map_coordinates import MapCoordinates
from ...point_analysis.points import points_from_segmentation

from ...io.raw_io import esprit_ascii_map_format, esprit_ascii_bse_format

from .. import gluedata_from_points, gluedata_from_stack_and_composite, gluedata_from_stack

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
import qtpy.QtWidgets as qtw
import qtpy.QtGui as qtg
import qtpy.QtCore as qtc

import os.path


class PreviewBSE(FigureCanvas):
    """Preview the BSE map."""
    def __init__(self, parent=None):
        fig = Figure()
        grid = GridSpec(3,1)
        self.ax = fig.add_subplot(grid[:2,0])
        self.ax_hist = fig.add_subplot(grid[2,0])
        self.ax.axis("off")
        self.ax_hist.set_xlim([0,1])
        self.ax_hist.axis("off")

        super().__init__(fig)
        self.setParent(parent)

    def draw_bse(self, img):
        self.ax.cla()
        self.ax.imshow(img, cmap=plt.cm.gray)

        self.ax_hist.cla()
        self.ax_hist.hist(img.ravel(), bins=100, range=(0,1))
        self.ax_hist.set_xlim([0,1])

        self.figure.tight_layout()

        self.draw()
        self.flush_events()

    def reset_bse(self):
        self.ax.cla()
        self.ax.axis("off")
        self.ax_hist.cla()
        self.ax_hist.axis("off")
        self.draw()
        self.flush_events()


class LoadEDSdata(qtw.QDialog):
    """A dialog to load a glue dataset"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.info = {}
        self._ui = load_ui('loader.ui', self,
            directory=os.path.dirname(__file__))

        self.fill_format()

        self.disable_all_params()

        self._ui.browse_button.clicked.connect(self.browse_for_pattern)
        self._ui.pattern_box.editingFinished.connect(self.load_preview)

        self.set_preview_canvas()
        self.results = []

    def fill_format(self):
        ui = self._ui

        ui.format_eds_delim.setText(esprit_ascii_map_format.delimiter)
        ui.format_eds_max.setText(str(esprit_ascii_map_format.max_value))
        ui.format_eds_min.setText(str(esprit_ascii_map_format.min_value))

        ui.format_bse_delim.setText(esprit_ascii_bse_format.delimiter)
        ui.format_bse_max.setText(str(esprit_ascii_bse_format.max_value))
        ui.format_bse_min.setText(str(esprit_ascii_bse_format.min_value))


    def get_bse_format(self):
        ui = self._ui

        txtformat = esprit_ascii_bse_format.copy()
        txtformat.delimiter = ui.format_bse_delim.text()
        txtformat.min_value = float(ui.format_bse_min.text())
        txtformat.max_value = float(ui.format_bse_max.text())

        return txtformat

    def get_eds_format(self):
        ui = self._ui

        txtformat = esprit_ascii_map_format.copy()
        txtformat.delimiter = ui.format_eds_delim.text()
        txtformat.min_value = float(ui.format_eds_min.text())
        txtformat.max_value = float(ui.format_eds_max.text())

        return txtformat

    def browse_for_pattern(self):
        """Browse the filesystem to find a BSE map and transform as pattern."""
        full_bse_path, _ = qtw.QFileDialog.getOpenFileName(None, "Open map", ".","txt files (*.txt);;All Files (*)")

        try:
            head, tail = full_bse_path.rsplit("BSE", maxsplit=1)
        except ValueError as e:
            print(e)
            return

        pattern = head+"{component}"+tail

        short_text = os.path.basename(head)

        self._ui.short_label_edit.setText(short_text)
        self._ui.pattern_box.setText(pattern)
        self._ui.pattern_box.editingFinished.emit()


    def set_preview_canvas(self):
        preview_tab = self._ui.preview_tab

        layout = qtw.QVBoxLayout()

        self.bse_preview = PreviewBSE()
        layout.addWidget(self.bse_preview)

        preview_tab.setLayout(layout)

    def load_preview(self):
        """Load a preview."""
        pattern = self._ui.pattern_box.text()
        #label = self._ui.short_label_edit.text()
        print("Selected pattern : {0}".format(pattern))
        try:
            self.preview_exp = MappingExperiment(pattern, map_format=self.get_eds_format(), bse_format=self.get_bse_format())
        except RuntimeError as e:
            print(e)
            self.preview_exp = None
            self.disable_all_params()
            self.bse_preview.reset_bse()
        else:
            self.enable_all_params()
            self.set_combo_box()
            self.draw_preview()


    def draw_preview(self):
        """Draw the preview BSE."""
        loader = DefaultLoader(self.preview_exp, filters=None)
        bse = loader.load_edsmap("BSE")
        self.bse_preview.draw_bse(bse.map)



    def set_combo_box(self):
        """Set the combo boxes in parameters."""
        ui = self._ui
        for combo in [ui.green_combo, ui.red_combo, ui.blue_combo]:
            combo.clear()
            combo.addItem("None")
            combo.addItems(self.preview_exp.list_components)

        if "Al" in self.preview_exp.list_components:
            ui.green_combo.setCurrentText("Al")
        if "Si" in self.preview_exp.list_components:
            ui.red_combo.setCurrentText("Si")
        if "Ca" in self.preview_exp.list_components:
            ui.blue_combo.setCurrentText("Ca")

    def enable_all_params(self):
        """Enable the params once the preview is loaded."""
        self._change_all_params(True)

    def disable_all_params(self):
        """Disable all the params if the pattern is not correct"""
        self._change_all_params(False)

    def _change_all_params(self, enabled):
        ui = self._ui

        widgets = [
                ui.no_filter_check,
                ui.tv_filter_check,
                ui.mean_filter_check,
                ui.gaussian_filter_check,

                ui.weight_filter_box,
                ui.radius_filter_box,
                ui.sigma_filter_box,

                ui.segmentation_check,

                ui.green_combo,
                ui.red_combo,
                ui.blue_combo,

                ui.green_factor_box,
                ui.red_factor_box,
                ui.blue_factor_box,

                ui.bsemix_check,
                ui.alpha_box,

                ui.numberpts_box,

                ui.filterbse_check,
                ui.minbse_box,
                ]

        for widget in widgets:
            widget.setEnabled(enabled)

    def get_experiment(self):
        """Return an experiment."""
        pattern = self._ui.pattern_box.text()
        label = self._ui.short_label_edit.text()
        description = self._ui.description_box.text()

        exp = MappingExperiment(pattern, label, description, map_format=self.get_eds_format(), bse_format=self.get_bse_format())
        return exp

    def get_filters(self):
        """Return the filter to load the maps."""
        if self._ui.no_filter_check.isChecked():
            return None
        elif self._ui.tv_filter_check.isChecked():
            weight = float(self._ui.weight_filter_box.text())
            return [DenoiseFilter(weight),]
        elif self._ui.mean_filter_check.isChecked():
            radius = self._ui.radius_filter_box.value()
            return [UniformFilter(radius),]
        elif self._ui.gaussian_filter_check.isChecked():
            sigma = self._ui.sigma_filter_box.value()
            return [GaussianFilter(sigma),]

    def get_scale(self):
        """Return the coordinate system"""
        pixel_size = self._ui.dx_scale_box.value() # in nanometer
        if pixel_size > 0:
            scale = 1/(1e-3*pixel_size) # in pixel/um
        else:
            scale = 1.0
        return MapCoordinates(scale=scale)

    def get_channels(self):
        """Return the channels for the composite."""
        ui = self._ui

        components = []

        for combo in [ui.green_combo, ui.red_combo, ui.blue_combo]:
            comp = combo.currentText()
            if comp == "None":
                comp = None
            components.append(comp)

        factors = []
        for fbox in [ui.green_factor_box, ui.red_factor_box, ui.blue_factor_box]:
            factors.append(fbox.value())

        return CompositeChannels(components, factors)

    def set_data(self):
        ui = self._ui

        exp = self.get_experiment()
        filters = self.get_filters()
        loader = PickleLoader(exp, filters=filters)


        stack = loader.load_stack()
        coords = self.get_scale()

        if ui.segmentation_check.isChecked():
            channels = self.get_channels()
            composite = loader.load_composite(channels)


            bse_map =  loader.load_edsmap("BSE")

            if ui.bsemix_check.isChecked():
                composite.mix_with_bse(bse_map, ui.alpha_box.value())
            if ui.filterbse_check.isChecked():
                composite.map[bse_map.map<0.2,:] = 0


            stack_data = gluedata_from_stack_and_composite(exp.label+"maps", stack, composite, coords)

            # segmentation
            compactness = float(ui.compactness_box.text())
            numberpts = float(ui.numberpts_box.text())
            labels = SlicSegmenter(compactness, numberpts).apply(composite)
            pts = points_from_segmentation(stack, labels, mask_img=composite.map, include_yx=True)
            pts_data = gluedata_from_points(exp.label+"points", pts)
            self.results.append(stack_data)
            self.results.append(pts_data)
        else:
            stack_data = gluedata_from_stack(exp.label+"maps", stack)
            self.results.append(stack_data)

    def accept(self):
        qtw.QApplication.setOverrideCursor(qtg.QCursor(qtc.Qt.WaitCursor))
        try:
            self.set_data()
        except:
            qtw.QApplication.restoreOverrideCursor()
            return self.reject()
        qtw.QApplication.restoreOverrideCursor()
        return super().accept()

@importer("Import EDS/BSE maps")
def load_maps():
    """Load maps in glue"""
    dialog = LoadEDSdata()

    dialog_result = dialog.exec_()
    if dialog_result != qtw.QDialog.Accepted:
        return []

    return dialog.results