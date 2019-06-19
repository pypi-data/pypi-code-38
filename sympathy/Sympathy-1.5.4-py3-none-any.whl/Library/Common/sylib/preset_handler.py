# Copyright (c) 2013, Combine Control Systems AB
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
import os
import os.path
import glob
import base64
import json
import six
from sympathy.platform import qt_compat
QtCore = qt_compat.QtCore
QtGui = qt_compat.import_module('QtGui')


class PresetsWidget(QtGui.QWidget):
    """A widget for handling preset data (loading, storing)."""

    def __init__(self, parent=None):
        super(PresetsWidget, self).__init__(parent)

        vlayout = QtGui.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        hlayout = QtGui.QHBoxLayout()

        presets_label = QtGui.QLabel("Presets")
        self.presets_combobox = QtGui.QComboBox()
        self.presets_save_button = QtGui.QPushButton("Save")
        self.presets_saveas_button = QtGui.QPushButton("Save As...")
        self.presets_load_button = QtGui.QPushButton("Load")

        hlayout.addWidget(self.presets_load_button)
        hlayout.addWidget(self.presets_save_button)
        hlayout.addWidget(self.presets_saveas_button)

        vlayout.addWidget(presets_label)
        vlayout.addWidget(self.presets_combobox)
        vlayout.addItem(hlayout)

        self.setLayout(vlayout)

        self.presets_load_button.clicked[bool].connect(self._presetLoad)
        self.presets_save_button.clicked[bool].connect(self._presetSave)
        self.presets_saveas_button.clicked[bool].connect(self._presetSaveAs)

    def set_presets(self, item_list):
        self.presets_combobox.addItems(sorted(item_list))

    def append_preset(self, item):
        self.presets_combobox.addItem(item)
        self.presets_combobox.setCurrentIndex(
            self.presets_combobox.count() - 1)

    def get_selected_preset(self):
        return self.presets_combobox.currentText()

    def _presetLoad(self):
        self.emit(QtCore.SIGNAL('presetLoad()'))

    def _presetSave(self):
        self.emit(QtCore.SIGNAL('presetSave()'))

    def _presetSaveAs(self):
        self.emit(QtCore.SIGNAL('presetSaveAs()'))


class PresetHandlerWidget(QtGui.QWidget):
    def __init__(self, parameters, definition, parent=None):
        super(PresetHandlerWidget, self).__init__(parent)

        self._parameters = parameters
        self._nodeid = definition['nodeid']
        self._loaded_data = None

        self._preset_dir = self._create_preset_dir()

        vlayout = QtGui.QVBoxLayout()

        self._preset_view = PresetsWidget()

        # Init preset view
        self._name_file_map = self._list_presets_on_disk(self._preset_view)

        vlayout.addWidget(self._preset_view)

        self.setLayout(vlayout)

        QtCore.QObject.connect(self._preset_view,
                               QtCore.SIGNAL("presetLoad()"),
                               self.preset_load)
        QtCore.QObject.connect(self._preset_view,
                               QtCore.SIGNAL("presetSave()"),
                               self.preset_save)
        QtCore.QObject.connect(self._preset_view,
                               QtCore.SIGNAL("presetSaveAs()"),
                               self.preset_saveas)

    def _create_preset_dir(self):
        preset_dir = os.path.join(six.moves.getcwd(), 'presets', self._nodeid)
        if not os.path.isdir(preset_dir):
            os.makedirs(preset_dir)
        return preset_dir

    def _list_presets_on_disk(self, preset_view):
        preset_files = glob.glob(os.path.join(self._preset_dir, '*'))
        name_file_map = {}

        for preset_filename in preset_files:
            with open(preset_filename, 'r') as f:
                data = f.read()
                data_format = json.loads(data)
                preset_view.append_preset(data_format['name'])
                name_file_map[data_format['name']] = preset_filename

        return name_file_map

    def loaded_data(self):
        return self._loaded_data

    def preset_load_name(self, preset_name):
        fq_filename = self._name_file_map[preset_name]

        self._parameters['active_preset']['value'] = preset_name

        with open(fq_filename, 'r') as f:
            data = f.read()
            data_format = json.loads(data)
            self._loaded_data = data_format['data']

        # Update combobox the correct name
        model = self._preset_view.presets_combobox.model()
        item_count = model.rowCount(model.parent(model.index(0, 0)))
        preset_names = [str(model.data(model.index(i, 0)).toString())
                        for i in six.moves.range(0, item_count)]

        if preset_name in preset_names:
            self._preset_view.presets_combobox.setCurrentIndex(
                preset_names.index(preset_name))

        self.emit(QtCore.SIGNAL("presetLoad()"))

    def preset_load(self):
        preset_name = str(self._preset_view.get_selected_preset())
        self.preset_load_name(preset_name)

    def preset_save(self):
        preset_name = str(self._preset_view.get_selected_preset())
        fq_filename = self._name_file_map[preset_name]

        self._parameters['active_preset']['value'] = preset_name

        data_format = {}
        data_format['name'] = preset_name
        data_format['nodeid'] = self._nodeid
        data_format['data'] = self._parameters

        with open(fq_filename, 'w') as f:
            f.write(json.dumps(data_format, sort_keys=True, indent=4))

    def preset_saveas(self):
        preset_name, ok = QtGui.QInputDialog.getText(self,
                                                     "Save As...",
                                                     "Preset name:")
        preset_name = str(preset_name)
        if ok:
            preset_filename_base64 = base64.urlsafe_b64encode(preset_name)
            fq_filename = os.path.join(self._preset_dir,
                                       preset_filename_base64 + '.json')

            self._parameters['active_preset']['value'] = preset_name

            data_format = {}
            data_format['name'] = preset_name
            data_format['nodeid'] = self._nodeid
            data_format['data'] = self._parameters

            with open(fq_filename, 'w') as f:
                f.write(json.dumps(data_format, sort_keys=True, indent=4))

            if preset_name not in self._name_file_map:
                self._preset_view.append_preset(preset_name)
            self._name_file_map[preset_name] = fq_filename
