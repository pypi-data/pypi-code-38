# Copyright (c) 2016, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import os.path

from sympathy.api import exporters
from sympathy.api import node as synode
from sympathy.api import qt as qt_compat

QtGui = qt_compat.import_module('QtGui')


def installed_packages():
    import pip
    try:
        return pip.get_installed_distributions()
    except AttributeError:
        import pkg_resources
        return pkg_resources.working_set


PAPERSIZES = [
    ('Custom', (None, None)),
    ('A4', (210, 297)),
    ('A5', (148, 210)),
    ('A6', (105, 148)),
    ('Letter', (215.9, 279.4)),
    ('Legal', (215.9, 355.6)),
    ('Ledger', (279.4, 431.8)),
    ('B4', (250, 353)),
    ('B5', (176, 250)),
    ('B6', (125, 176)),
]


def create_papersize_labels():
    labels = []
    for l, (w, h) in PAPERSIZES:
        if w is not None or h is not None:
            size = '({}mm x {}mm)'.format(w, h)
        else:
            size = ''
        labels.append('{} {}'.format(l, size))
    return labels


class TabbedSizeChoiceWidget(QtGui.QWidget):
    filename_changed = qt_compat.Signal()

    def __init__(self, parameter_root, *args, **kwargs):
        super(TabbedSizeChoiceWidget, self).__init__(*args, **kwargs)
        self._parameter_root = parameter_root
        self._init_gui()

    def _init_gui(self):
        parameters = self._parameter_root

        vlayout = QtGui.QVBoxLayout()
        vlayout.setContentsMargins(0, 10, 0, 0)

        self._strategy_widget = parameters['selected_strategy'].gui()
        self._strategy_widget.setVisible(False)
        self._strategy_combobox = self._strategy_widget.editor().combobox()

        self._size_tabwidget = QtGui.QTabWidget()
        vlayout.addWidget(self._strategy_widget)
        vlayout.addWidget(self._size_tabwidget)

        # Size by setting pixels
        pixels_tab = QtGui.QWidget()
        pixels_flayout = QtGui.QFormLayout()
        self._width_widget = parameters['width'].gui()
        self._height_widget = parameters['height'].gui()
        for widget in [self._width_widget, self._height_widget]:
            pixels_flayout.addRow(widget.label_widget(), widget.editor())
        pixels_tab.setLayout(pixels_flayout)

        # Size by setting size in mm and dpi
        pagesize_tab = QtGui.QWidget()
        pagesize_flayout = QtGui.QFormLayout()
        self._size_width_widget = parameters['size_width'].gui()
        self._size_height_widget = parameters['size_height'].gui()
        self._paper_size_widget = parameters['paper_size'].gui()
        self._paper_size_combo = self._paper_size_widget.editor().combobox()
        self._p_orient_widget = parameters['paper_orientation'].gui()
        self._paper_orient_combo = self._p_orient_widget.editor().combobox()
        for widget in [self._size_width_widget, self._size_height_widget,
                       self._paper_size_widget, self._p_orient_widget]:
            pagesize_flayout.addRow(widget.label_widget(), widget.editor())
        pagesize_tab.setLayout(pagesize_flayout)

        self._size_tabwidget.addTab(pixels_tab, 'Set Pixels')
        self._size_tabwidget.addTab(pagesize_tab, 'Set Page Size')

        self._dpi_widget = parameters['dpi'].gui()
        vlayout.addWidget(self._dpi_widget)
        extension_gui = parameters['extension'].gui()
        vlayout.addWidget(extension_gui)
        extension_gui.editor().combobox().currentIndexChanged[int].connect(
            self._filename_changed)
        self.setLayout(vlayout)

        self._size_tabwidget.setCurrentIndex(
            self._strategy_combobox.currentIndex())

        self._strategy_combobox.currentIndexChanged[int].connect(
            self._strategy_combobox_changed)
        self._size_tabwidget.currentChanged[int].connect(self._tab_changed)
        self._paper_size_combo.currentIndexChanged[int].connect(
            self._paper_size_changed)
        self._paper_orient_combo.currentIndexChanged.connect(
            self._orientation_changed)

    def _strategy_combobox_changed(self, index):
        self._size_tabwidget.setCurrentIndex(index)

    def _tab_changed(self, index):
        self._strategy_combobox.setCurrentIndex(index)

    def _orientation_changed(self):
        index = self._paper_size_combo.currentIndex()
        self._paper_size_changed(index)

    def _paper_size_changed(self, index):
        label, (size_width, size_height) = PAPERSIZES[index]
        if size_width is not None and size_height is not None:
            orientation = self._parameter_root['paper_orientation'].selected
            if orientation == 'landscape':
                size_width, size_height = size_height, size_width
            self._size_width_widget.editor().set_value(size_width)
            self._size_height_widget.editor().set_value(size_height)

    def _filename_changed(self):
        self.filename_changed.emit()


class DataExportFigure(exporters.FigureDataExporterBase):
    """Exporter for Figure files."""
    EXPORTER_NAME = "Image"
    FILENAME_EXTENSION = None

    def __init__(self, parameters):
        super(DataExportFigure, self).__init__(parameters)
        flat_installed_packages = [package.project_name for package in
                                   installed_packages()]
        if 'xelatex' in flat_installed_packages:
            plist = ['eps', 'pdf', 'pgf', 'png', 'ps', 'svg', 'svgz']
        else:
            plist = ['eps', 'pdf', 'png', 'ps', 'svg', 'svgz']

        if 'extension' not in self._parameters:
            self._parameters.set_list(
                'extension',
                label='Filename extension:',
                description=('The extension to be used for exporting '
                             'the figures.'),
                value=[1],
                plist=plist,
                editor=synode.Util.combo_editor())

        if 'selected_strategy' not in self._parameters:
            self._parameters.set_list(
                'selected_strategy',
                label='Image size strategy',
                description=('Choose who to set the size of the saved '
                             'image(s).'),
                plist=['Set Pixels', 'Set Page Size'],
                editor=synode.Util.combo_editor())

        if 'width' not in self._parameters:
            self._parameters.set_integer(
                'width',
                label='Image width (px):',
                description='The image width in pixels.',
                value=800,
                editor=synode.Util.bounded_spinbox_editor(
                    100, 1000000000, 1))
        if 'height' not in self._parameters:
            self._parameters.set_integer(
                'height',
                label='Image height (px):',
                description='The image height in pixels.',
                value=600,
                editor=synode.Util.bounded_spinbox_editor(
                    100, 1000000000, 1))

        if 'size_width' not in self._parameters:
            self._parameters.set_float(
                'size_width',
                label='Image width (mm):',
                description='The image width in millimeter.',
                value=297,
                editor=synode.Util.bounded_decimal_spinbox_editor(
                    0., 1000000000, 1, 3))
        if 'size_height' not in self._parameters:
            self._parameters.set_float(
                'size_height',
                label='Image height (mm):',
                description='The image height in millimeter.',
                value=210,
                editor=synode.Util.bounded_decimal_spinbox_editor(
                    0., 1000000000, 1, 3))

        if 'paper_size' not in self._parameters:
            self._parameters.set_list(
                'paper_size',
                label='Paper size:',
                description='The paper size in millimeter.',
                value=[0],
                plist=create_papersize_labels(),
                editor=synode.Util.combo_editor())

        if 'paper_orientation' not in self._parameters:
            self._parameters.set_list(
                'paper_orientation',
                label='Orientation:',
                description='The paper orientation (portrait or landscape).',
                plist=['portrait', 'landscape'],
                editor=synode.Util.combo_editor())

        if 'dpi' not in self._parameters:
            self._parameters.set_integer(
                'dpi',
                label='Dots-per-inch',
                description='The dots-per-inch of the figure.',
                value=120,
                editor=synode.Util.bounded_spinbox_editor(
                    1, 100000, 1))

    def create_filenames(self, input_list, filename, *args):
        ext = self._parameters['extension'].selected
        return super(DataExportFigure, self).create_filenames(
            input_list, filename, *args,
            ext=ext)

    def parameter_view(self, input_list):
        return TabbedSizeChoiceWidget(self._parameters)

    def export_data(self, figure, fq_outfilename, progress=None):
        """Export Figure to Image."""
        strategy = self._parameters['selected_strategy'].selected
        dpi = self._parameters['dpi'].value
        if strategy == 'Set Pixels':
            width = self._parameters['width'].value
            height = self._parameters['height'].value
        else:
            size_width = self._parameters['size_width'].value
            size_height = self._parameters['size_height'].value
            # convert size in mm to inch and multiply with dpi to get image
            # size in pixel
            width = int(size_width * 0.039370 * dpi)
            height = int(size_height * 0.039370 * dpi)
        kwargs = {'dpi': dpi,
                  'size': (width, height)}

        if not os.path.exists(os.path.dirname(fq_outfilename)):
            os.makedirs(os.path.dirname(fq_outfilename))
        figure.save_figure(fq_outfilename, **kwargs)
