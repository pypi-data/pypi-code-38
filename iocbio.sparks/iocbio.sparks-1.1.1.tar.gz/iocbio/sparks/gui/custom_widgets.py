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
#!/usr/bin/env python3

from PyQt5.QtCore import Qt, pyqtSignal, QRect, QTimer, QPoint
from PyQt5.QtWidgets import QWidget, QGroupBox, QSlider, QSpinBox, QHBoxLayout, QVBoxLayout, QLabel, QGridLayout
from PyQt5.QtWidgets import QLineEdit, QCheckBox, QPushButton, QToolButton, QListWidget, QListWidgetItem, QScrollArea
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QTextEdit, QStatusBar
from PyQt5.QtGui import QPalette, QColor, QMenu, QFrame
from ..calc.spark import Spark
from ..handler.image import Image
from ..handler.experiment import ExperimentHandler
from .lut import LUTWidget
import pyqtgraph as pg

from collections import namedtuple

import numpy as np


def float_to_nice_string(f):
    if f is None:
        return 'none'
    if np.isneginf(f):
        return '- inf'
    if np.isposinf(f):
        return '+ inf'
    if np.isnan(f):
        return 'nan'
    if np.abs(f) < 1.e-12:
        return str(f)
    digits = 5
    # { TODO following is for testing period
    try:
        power = int(np.ceil(np.log10(np.abs(f))))
    except:
        print('Something is really wrong', type(f), f)
    # }
    round_rule = digits-power
    if round_rule < 1:
        round_rule = 1
    return str(round(f, round_rule))


class SmallLabel(QLabel):

    def __init__(self, text, word_wrap=True):
        QLabel.__init__(self, '<small>'+text+'</small>')
        self.setWordWrap(word_wrap)


class HLine(QFrame):
    def __init__(self):
        QFrame.__init__(self)
        self.setFrameShape(QFrame.HLine)
        self.setLineWidth(5)
        self.set_color()

    def set_color(self, color=None):
        if color is not None:
            palette = QPalette(self.palette())
            color = QColor(color)
            color.setAlpha(60)
            palette.setColor(palette.Foreground, color)
            self.setPalette(palette)


class SunkenHLine(QFrame):
    def __init__(self):
        QFrame.__init__(self)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class SparksStatsView(QWidget):

    def __init__(self):
        QTableWidget.__init__(self)

        self.spark = None

        # {Creating ui
        self.spark_stats = QTableWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Spark statistics:'), 0)
        layout.addWidget(self.spark_stats, 1)
        self.setLayout(layout)
        m = layout.getContentsMargins()
        layout.setContentsMargins(m[0], 0, m[2], 0)
        # }

    def set_spark(self, spark):
        if self.spark is not None:
            self.spark.sigUpdateStats.disconnect(self.update_stats)

        self.spark = spark
        if self.spark is None:
            self.spark_stats.clear()
            self.spark_stats.setRowCount(0)
            self.spark_stats.horizontalHeader().setVisible(False)
            return

        self.spark.sigUpdateStats.connect(self.update_stats)
        self.update_stats()

    def update_stats(self):
        self.spark_stats.clear()
        data = self.spark.stats

        if data == {}:
            return

        keys = sorted(data.keys())
        resdict = self.spark.results_dict()

        self.spark_stats.clear()
        self.spark_stats.setColumnCount(3)
        self.spark_stats.setRowCount(len(keys))
        self.spark_stats.verticalHeader().setVisible(False)
        self.spark_stats.horizontalHeader().setVisible(True)
        self.spark_stats.setHorizontalHeaderLabels(['parameter', 'value', 'unit'])

        for i, key in enumerate(keys):
            if key in resdict:
                r = resdict[key]
                desc, unit = r.human_long, r.unit
            else:
                desc, unit = key, ""
            self.spark_stats.setItem(i, 0, QTableWidgetItem(desc))
            item = QTableWidgetItem(float_to_nice_string(data[key]))
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.spark_stats.setItem(i, 1, item)
            self.spark_stats.setItem(i, 2, QTableWidgetItem(unit))

        self.spark_stats.resizeColumnsToContents()
        self.spark_stats.resizeRowsToContents()


class SparksListView(QWidget):
    sigActiveSpark = pyqtSignal(str)
    sigSparkRemove = pyqtSignal(str)

    def __init__(self):
        QWidget.__init__(self)

        self.spark_list = None
        self.active_spark = None
        self.read_only = False

        self.list_widget = QListWidget()
        self.list_widget.uniformItemSizes()
        label = QLabel('Sparks list:')
        self.list_widget.setMaximumWidth(label.sizeHint().width())
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)

        # {Event bindings
        self.list_widget.currentRowChanged.connect(self.update_selected)
        self.list_widget.customContextMenuRequested.connect(self.open_context_menu)
        # }

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.list_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def open_context_menu(self, position):
        menu = QMenu()
        menu.addAction('Remove', self.remove_item)
        menu.addAction('Remove all', self.remove_all_items)
        menu.exec_(self.list_widget.viewport().mapToGlobal(position))

    def remove_item(self):
        row = self.list_widget.currentRow()
        if row < 0 or row >= len(self.spark_list):
            return

        self.active_spark = None
        self.sigSparkRemove.emit(self.spark_list[row])

    def remove_all_items(self):
        for row in range(self.list_widget.count())[::-1]:
            self.sigSparkRemove.emit(self.spark_list[row])
        self.active_spark = None

    def set_list(self, rois, sorted_roi_list):
        self.list_widget.clear()
        self.spark_list = sorted_roi_list
        for i, roi_id in enumerate(self.spark_list):
            item = QListWidgetItem('%i' % (i+1,))
            item.roi_id = roi_id
            self.list_widget.addItem(item)

    def update_selected(self, i):
        if i < 0: return

        spid = self.spark_list[i]
        if self.active_spark == spid and self.active_spark is None:
            return
        self.sigActiveSpark.emit(spid)

    def set_active(self, roi_id):
        if roi_id in self.spark_list:
            self.active_spark = roi_id
            self.list_widget.setCurrentRow(self.spark_list.index(roi_id))

    def keyPressEvent(self, event):
        if self.read_only: return
        if event.key() == Qt.Key_Delete and len(self.spark_list) > 0:
            self.remove_item()

    def set_read_only(self, state):
        self.read_only = state
        if self.read_only:
            self.list_widget.customContextMenuRequested.disconnect(self.open_context_menu)
        else:
            self.list_widget.customContextMenuRequested.connect(self.open_context_menu)


class CalculationProgress(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        palette = QPalette(self.palette())
        palette.setColor(palette.WindowText, QColor(255,0,0))
        self.setPalette(palette)
        self.parent = parent

        layout = QVBoxLayout()
        self.message = QLabel('')
        layout.addWidget(self.message)
        self.setLayout(layout)

    def set_message(self, message):
        self.message.setText(message)
        self.adjustSize()
        self.set_location()

    def set_location(self):
        p = self.parent.geometry()
        s = self.frameGeometry()
        newGeometry = QRect(p.right()-s.width(), p.top(), s.width(), s.height())
        self.setGeometry(newGeometry)


class ShowInfo(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        palette = QPalette(self.palette())
        palette.setColor(palette.WindowText, QColor(20,20,20))
        palette.setColor(palette.Window, QColor(250,250,250))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        self.parent = parent
        self.timer = QTimer()
        self.timer.timeout.connect(self.hide)

        layout = QVBoxLayout()
        self.message = QLabel('')
        layout.addWidget(self.message)
        self.setLayout(layout)

    def set_message(self, message, interval=1):
        self.message.setText(message)
        self.adjustSize()
        self.set_location()
        self.timer.setInterval(interval*60000)
        self.timer.setSingleShot(True)
        self.timer.start()

    def set_location(self):
        p = self.parent.geometry()
        s = self.frameGeometry()
        newGeometry = QRect(p.left(), p.bottom()-s.height(), s.width(), s.height())
        self.setGeometry(newGeometry)


class ControlSlider(QWidget):
    sigValueChanged = pyqtSignal(int)

    def __init__(self, label, value, vmin, vmax, manualtextsize):
        '''
        value - initial position of the slider
        vmin - minimum slider position
        vmax - maximum slider position
        manualtextsize - size of the valueSpinBox
        '''
        QWidget.__init__(self)

        self.value = value

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(vmin, vmax)
        self.slider.setValue(value)

        self.valueSpinBox = QSpinBox()
        self.valueSpinBox.setFixedWidth(manualtextsize)
        self.valueSpinBox.setRange(vmin, vmax)
        self.valueSpinBox.setValue(value)
        self.valueSpinBox.setSingleStep(1)

        # event bindings {
        self.slider.valueChanged.connect(self.valueSpinBox.setValue)
        self.valueSpinBox.valueChanged.connect(self.slider.setValue)
        self.slider.valueChanged.connect(self.valueChanged)
        # }

        # create layout {
        layout_slider = QHBoxLayout()
        layout_slider.addWidget(self.slider, Qt.AlignTop | Qt.AlignLeft)
        layout_slider.addWidget(self.valueSpinBox, Qt.AlignTop | Qt.AlignLeft)

        mainlayout = QVBoxLayout()
        mainlayout.addWidget(QLabel(label), Qt.AlignTop)
        mainlayout.addLayout(layout_slider, Qt.AlignTop)
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.addStretch(1)
        self.setLayout(mainlayout)
        # }

    def valueChanged(self):
        self.value = self.slider.value()
        self.sigValueChanged.emit(self.value)

    def set_value(self, value):
        self.slider.setValue(value)


class ImageIntensitySetter(QWidget):
    sigValueChanged = pyqtSignal(int, int) # emits min and max value

    def __init__(self, label, vmin, vmax, levels_range, manualtextsize):
        '''
        label - the name
        value - initial position of the slider
        vmin - minimum slider position
        vmax - maximum slider position
        manualtextsize - size of the valueSpinBox
        '''
        QWidget.__init__(self)

        self.vmin = vmin
        self.vmax = vmax
        r0, r1 = levels_range

        self.min_setter = ControlSlider('Minimum', vmin, r0, r1, manualtextsize)
        self.max_setter = ControlSlider('Maximum', vmax, r0, r1, manualtextsize)

        # event bindings {
        self.min_setter.sigValueChanged.connect(self.min_value_changed)
        self.max_setter.sigValueChanged.connect(self.max_value_changed)
        # }

        layout = QVBoxLayout()
        layout.addWidget(self.min_setter)
        layout.addWidget(self.max_setter)
        layout.addStretch(1)

        groupBox = QGroupBox(label)
        groupBox.setLayout(layout)
        mainlayout = QHBoxLayout()
        mainlayout.addWidget(groupBox)
        mainlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainlayout)

    # def set_disabled(self, disabled=False):
    #     self.setDisabled(disabled)

    def min_value_changed(self, value):
        self.vmin = value
        self.value_changed()

    def max_value_changed(self, value):
        self.vmax = value
        self.value_changed()

    def value_changed(self):
        self.sigValueChanged.emit(self.vmin, self.vmax)

    def update_value(self, vmin, vmax):
        self.vmin = vmin
        self.vmax = vmax
        self.sigValueChanged.emit(self.vmin, self.vmax)

    def set_values(self, vmin, vmax):
        self.vmin = vmin
        self.vmax = vmax
        self.min_setter.set_value(self.vmin)
        self.max_setter.set_value(self.vmax)

    @property
    def get_levels(self):
        return self.vmin, self.vmax


class ImageAdjustments(QWidget):

    def __init__(self, label, vmin, vmax, levels_range, manualtextsize, lut_name):
        QWidget.__init__(self)

        self.lut = LUTWidget('0' if lut_name is None else lut_name)

        self.image_levels = ImageIntensitySetter(label='Set image intesity levels',
                                                 vmin=vmin,
                                                 vmax=vmax,
                                                 levels_range=levels_range,
                                                 manualtextsize=manualtextsize)

        self.spark_levels = ImageIntensitySetter(label='Set spark image intesity levels',
                                                 vmin=vmin,
                                                 vmax=vmax,
                                                 levels_range=levels_range,
                                                 manualtextsize=manualtextsize)

        disable_spark_levels = QCheckBox('Use the same levels for sparks and image')
        disable_spark_levels.setTristate(False)
        disable_spark_levels.setCheckState(Qt.Unchecked)
        disable_spark_levels.stateChanged.connect(self.on_disable_spark_levels)

        layout = QVBoxLayout()
        layout.addWidget(self.lut)
        layout.addWidget(disable_spark_levels)
        layout.addWidget(self.image_levels)
        layout.addWidget(self.spark_levels)
        layout.addStretch(1)
        self.setLayout(layout)

    def on_disable_spark_levels(self, disable):
        if disable:
            self.image_levels.sigValueChanged.connect(self.spark_levels.update_value)
            self.spark_levels.sigValueChanged.emit(*self.image_levels.get_levels)
            self.spark_levels.hide()
        else:
            self.image_levels.sigValueChanged.disconnect(self.spark_levels.update_value)
            self.spark_levels.set_values(*self.image_levels.get_levels)
            self.spark_levels.show()


class CustomQLineEdit(QLineEdit):
    sigValueUpdated = pyqtSignal(str)

    def __init__(self, value, dtype, group):
        QLineEdit.__init__(self)
        self.dtype = dtype
        self.group = group
        self.set_value(value)
        self.returnPressed.connect(self.value_updated)

    def value_updated(self):
        self.sigValueUpdated.emit(self.group)

    def set_value(self, value):
        self.setText(str(value))

    @property
    def get_value(self):
        if self.dtype is float:
            return float(self.text())
        if self.dtype is int:
            return int(self.text())


class CustomQCheckBox(QCheckBox):
    sigValueUpdated = pyqtSignal(str)

    def __init__(self, value, group):
        QCheckBox.__init__(self)
        self.group = group
        self.set_value(value)
        self.stateChanged.connect(self.value_updated)

    def value_updated(self, value):
        self.sigValueUpdated.emit(self.group)

    def set_value(self, value):
        self.setChecked(value)

    @property
    def get_value(self):
        return self.isChecked()


class CollapseButton(QToolButton):
    sigClicked = pyqtSignal(bool, str)

    def __init__(self, title, group):
        QToolButton.__init__(self)
        self.group = group
        self.setStyleSheet('QToolButton {border: none; font-weight: bold;}')
        self.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.setArrowType(Qt.RightArrow)
        self.setText(title)
        self.setCheckable(True)
        self.setChecked(False)

        self.clicked.connect(self.on_button)

    def on_button(self, checked):
        if checked:
            self.setArrowType(Qt.DownArrow)
        else:
            self.setArrowType(Qt.RightArrow)
        self.sigClicked.emit(checked, self.group)


class ParametersSetter(QWidget):
    sigParametersChanged = pyqtSignal(str, dict, dict, dict)

    def __init__(self, spark_parameters, image_parameters, auto_detect_parameters):
        """
        parameters : is a dictronary of parameter key and value as namedtuple
        global_parametes : a list of parameters that will have a global effect
        """
        QWidget.__init__(self)
        self.spark_parameters = spark_parameters
        self.image_parameters = image_parameters
        self.auto_detect_parameters = auto_detect_parameters
        self.ignore_changes = False

        self.input_widgets_spark = {}
        self.input_widgets_image = {}
        self.input_widgets_auto_detect = {}

        self.information_widgets = {'spark': [], 'image': [], 'auto_detect': []}

        self.read_only = False

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout()
        layout = QGridLayout()
        layout.setVerticalSpacing(1)
        layout.setAlignment(Qt.AlignTop)

        def add_to_layout(parameters, input_widgets, group):
            # group defines either it is: spark / image / auto_detect
            for key in parameters.keys():
                param = parameters[key]
                default = param.default

                if param.pytype == int or param.pytype == float:
                    input_widget = CustomQLineEdit(default, dtype=param.pytype, group=group)

                elif param.pytype == bool:
                    input_widget = CustomQCheckBox(param.default, group)

                input_widget.sigValueUpdated.connect(self.signal_received)
                input_widget.setMaximumWidth(50)

                row = layout.rowCount()

                human_short = QLabel(param.human_short)
                human_long = SmallLabel(param.human_long)
                space = SmallLabel('')
                layout.addWidget(human_short, row, 0)
                layout.addWidget(input_widget, row, 1)
                layout.addWidget(human_long, row+1, 0, 1, 2)
                layout.addWidget(space, row+2, 0, 1, 2)

                input_widgets[key] = input_widget
                self.information_widgets[group].append(human_short)
                self.information_widgets[group].append(human_long)
                self.information_widgets[group].append(space)

        image_button = CollapseButton('Image analysis parameters:', 'image')
        layout.addWidget(image_button, layout.rowCount(), 0, 1, 2)
        add_to_layout(self.image_parameters, self.input_widgets_image, 'image')

        auto_button = CollapseButton('Spark detection parameters:', 'auto_detect')
        layout.addWidget(auto_button, layout.rowCount(), 0, 1, 2)
        add_to_layout(self.auto_detect_parameters, self.input_widgets_auto_detect, 'auto_detect')

        spark_button = CollapseButton('Spark analysis parameters:', 'spark')
        layout.addWidget(spark_button, layout.rowCount(), 0, 1, 2)
        add_to_layout(self.spark_parameters, self.input_widgets_spark, 'spark')

        apply_to_all_btn = QPushButton('Apply to all')
        set_defaults_btn = QPushButton('Set defaults')

        # { Buttons event bindings
        apply_to_all_btn.clicked.connect(self.apply_to_all)
        set_defaults_btn.clicked.connect(self.set_defaults)
        spark_button.sigClicked.connect(self.visibility)
        image_button.sigClicked.connect(self.visibility)
        auto_button.sigClicked.connect(self.visibility)
        # }
        self.visibility(False, 'spark')
        self.visibility(False, 'image')
        self.visibility(False, 'auto_detect')

        button_layout = QHBoxLayout()
        button_layout.addWidget(apply_to_all_btn)
        button_layout.addWidget(set_defaults_btn)

        # { Creating scroll area for parameters
        layout_widget = QWidget()
        layout_widget.setLayout(layout)
        scroll_layout = QScrollArea()
        scroll_layout.setWidgetResizable(True)
        scroll_layout.setWidget(layout_widget)
        # }

        main_layout.addWidget(scroll_layout)
        main_layout.addLayout(button_layout)
        # scroll_layout.setMinimumWidth(layout.sizeHint().width()+35)
        self.setLayout(main_layout)

    def visibility(self, checked, group):
        input_widgets = getattr(self, 'input_widgets_%s' % group)

        if not checked:
            for _, w in input_widgets.items():
                w.hide()
            for w in self.information_widgets[group]:
                w.hide()
        else:
            for _, w in input_widgets.items():
                w.show()
            for w in self.information_widgets[group]:
                w.show()

    def apply_to_all(self):
        self.signal_received('all')

    def set_defaults(self):
        v = self.get_values()
        Spark.set_defaults(v)
        Image.set_defaults(v)

    def get_values(self):
        d = {}
        for key, widget in self.input_widgets_spark.items():
            d[key] = widget.get_value
        for key, widget in self.input_widgets_image.items():
            d[key] = widget.get_value
        for key, widget in self.input_widgets_auto_detect.items():
            d[key] = widget.get_value
        return d

    def signal_received(self, group):
        if self.ignore_changes:
            return

        self.sigParametersChanged.emit(group,
                                       {key:widget.get_value for key, widget in self.input_widgets_spark.items()},
                                       {key:widget.get_value for key, widget in self.input_widgets_image.items()},
                                       {key:widget.get_value for key, widget in self.input_widgets_auto_detect.items()})

    def set_values(self, d):
        self.ignore_changes = True
        for k, v in d.items():
            if k in self.spark_parameters:
                self.input_widgets_spark[k].set_value(v)
            elif k in self.image_parameters:
                self.input_widgets_image[k].set_value(v)
            elif k in self.auto_detect_parameters:
                self.input_widgets_auto_detect[k].set_value(v)
            else:
                raise KeyError('No such key found, key: %s' % k)
        self.ignore_changes = False

    def set_read_only(self, state):
        self.read_only = state
        for key in self.information_widgets.keys():
            for _, widget in getattr(self, 'input_widgets_%s' % key).items():
                widget.setEnabled(not self.read_only)

        for widget in self.findChildren(QPushButton):
            widget.setEnabled(not self.read_only)


class CommentEdit(QWidget):
    sigCommentChanged = pyqtSignal(str)

    def __init__(self, comment=None):
        QWidget.__init__(self)

        self.read_only = False
        self.comments_field = QTextEdit()
        if comment is not None:
            self.set_comment(comment)

        submit = QPushButton('Submit')
        submit.clicked.connect(self.submit)

        layout = QVBoxLayout()
        layout.addWidget(self.comments_field)
        layout.addWidget(submit)
        self.setLayout(layout)

    def submit(self):
        self.sigCommentChanged.emit(self.get_comment)

    def set_comment(self, comment):
        self.comments_field.setText(comment)

    @property
    def get_comment(self):
        return self.comments_field.toPlainText()

    def set_read_only(self, state):
        self.read_only = state
        self.comments_field.setReadOnly(self.read_only)
        for widget in self.findChildren(QPushButton):
            widget.setEnabled(not self.read_only)


class StageField(QWidget):
    sigRemoveRequested = pyqtSignal(str)
    sigNameChanged = pyqtSignal(str, str)

    def __init__(self, name=''):
        QWidget.__init__(self)

        self.name = name
        self.can_remove = True
        self.stage_id = None
        self._init_ui()

    def _init_ui(self):
        from ..handler.experiment import Results as layout_dict
        from ..handler.experiment import ResultsOrder as layout_order
        self.layout_dict = layout_dict

        main_layout = QVBoxLayout()
        layout = QGridLayout()
        layout.setVerticalSpacing(1)

        layout.addWidget(QLabel('Range'), 0, 0)
        self.value_range_label = QLabel('')
        layout.addWidget(self.value_range_label, 0, 1)

        for name in layout_order:
            desc = self.layout_dict[name]
            row = layout.rowCount()
            layout.addWidget(QLabel(desc.human), row, 0)
            value_label = QLabel('')
            setattr(self, 'value_%s' % name, value_label)
            layout.addWidget(value_label, row, 1)

        region_layout = QHBoxLayout()
        self.region_title_edit = QLineEdit(self.name)
        self.remove_btn = QPushButton('Remove')
        region_layout.addWidget(QLabel('<b>Region name:</b>'))
        region_layout.addWidget(self.region_title_edit)
        region_layout.addWidget(self.remove_btn)
        self.region_title_long = QLabel('')
        self.set_name(self.name)

        # { Event bindings
        self.region_title_edit.returnPressed.connect(self.update_name)
        self.remove_btn.clicked.connect(self.remove)
        #region_title_edit.textEdited.connect(self.set_name)
        # }

        self.line = HLine()
        main_layout.addLayout(region_layout)
        main_layout.addWidget(self.line)
        main_layout.addWidget(self.region_title_long)

        main_layout.addLayout(layout)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

    def update_stage(self, stage):
        self.stage_id = stage['stage_id']
        self.set_name(stage['name'])
        self.set_range(stage['start'], stage['end'])
        self.set_color('#%s'%self.stage_id[:6])

        for name in self.layout_dict.keys():
            if name in stage:
                getattr(self, 'value_%s' % name).setText(float_to_nice_string(stage[name]))
            else:
                getattr(self, 'value_%s' % name).setText('')
        if stage['spark_analysis']:
            self.can_remove = False
            self.remove_btn.setDisabled(True)
        else:
            self.can_remove = True
            self.remove_btn.setDisabled(False)


    def update_name(self):
        self.sigNameChanged.emit(self.stage_id, self.region_title_edit.text())

    def set_name(self, value):
        self.name = value
        self.region_title_edit.setText(value)
        self.region_title_long.setText('<small>'+'Region named as: '+self.name+'</small>')

    def set_range(self, start, end):
        self.value_range_label.setText(float_to_nice_string(start) + ", " + float_to_nice_string(end))

    def set_color(self, color):
        self.line.set_color(color)

    def remove(self):
        if self.can_remove:
            self.sigRemoveRequested.emit(self.stage_id)


class StagesEdit(QWidget):
    sigAdd = pyqtSignal()
    sigRemove = pyqtSignal(str)
    sigNameChanged = pyqtSignal(str, str)

    def __init__(self):
        QWidget.__init__(self)

        add_stage_btn = QPushButton('Add')

        self.read_only = False
        self.stages_dict = {}
        self.stages_layout = QVBoxLayout()

        # { Creating scroll area for parameters
        layout_widget = QWidget()
        layout_widget.setLayout(self.stages_layout)
        scroll_layout = QScrollArea()
        scroll_layout.setWidgetResizable(True)
        scroll_layout.setWidget(layout_widget)
        # }

        # { Event bindings
        add_stage_btn.clicked.connect(self.add_stage)
        # }

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_layout)
        main_layout.addWidget(add_stage_btn)
        self.setLayout(main_layout)

    def add_stage(self):
        self.sigAdd.emit()

    def update_stages(self, stages_dict, stages_list):
        for key in stages_list:
            if key not in self.stages_dict:
                stage = StageField()
                stage.sigRemoveRequested.connect(self.sigRemove)
                stage.sigNameChanged.connect(self.sigNameChanged)
                self.stages_layout.insertWidget(self.stages_layout.count() - 1, stage)
                self.stages_layout.addStretch()
                self.stages_dict[key] = stage
            self.stages_dict[key].update_stage(stages_dict[key])

        keys = list(self.stages_dict.keys())
        for key in keys:
            if key not in stages_list:
                self.stages_dict[key].deleteLater()
                del self.stages_dict[key]

    def set_read_only(self, state):
        self.read_only = state
        for key, stage in self.stages_dict.items():
            # stage.setEnabled(not self.read_only)
            stage.region_title_edit.setEnabled(not self.read_only)
            stage.remove_btn.setEnabled(not self.read_only)

        for widget in self.findChildren(QPushButton):
            widget.setEnabled(not self.read_only)


class MainWindowStatusBar(QStatusBar):

    def __init__(self):
        QStatusBar.__init__(self)

        self.rw_status = QLabel('')
        self.jobs_status = QLabel('')
        self.message = QLabel('')

        self.addWidget(self.rw_status)
        self.addWidget(self.jobs_status)
        self.addWidget(self.message)

        self.timer = QTimer()
        self.timer.timeout.connect(self.message.hide)

        self.update_rw_status() # for testing

    def update_rw_status(self, status=True):
        uchar = '\u2B24'
        if status:
            self.rw_status.setText("<span style='color:#990f0f;'>%s</span> Read-write mode" % uchar)
        else:
            self.rw_status.setText("<span style='color:#0f9934;'>%s</span> Read-only mode" % uchar)

    def update_message(self, s, interval=1):
        self.message.setText('| '+s)
        self.timer.setInterval(interval*60000)
        self.timer.setSingleShot(True)
        self.timer.start()

    def update_jobs_status(self, njobs):
        if njobs < 1:
            self.jobs_status.hide()
        else:
            self.jobs_status.show()
            self.jobs_status.setText('| Active jobs: %s' % njobs)


class XYPlot(QWidget):

    def __init__(self, data=None, title=None, label=None):
        """
        data: dictionary {name_1: {'x': 1D array, 'y': 1D array},
                          ...
                          name_n: {'x': 1D array, 'y': 1D array}}
        title: title for plot
        """
        QWidget.__init__(self)

        self.pw = pg.PlotWidget()
        #self.legend = self.pw.addLegend()

        if data is not None:
            self.set_data(data)

        if title is not None:
            self.set_title(title)

        if label is not None:
            self.set_axis_label(label)

        # { Creating layout
        layout = QVBoxLayout()
        layout.addWidget(self.pw)
        self.setLayout(layout)
        # }

    def set_data(self, data):
        """
        Sets data to plot
        data: see XYPlot.__init__()
        """
        self.pw.clear()
        # for item in self.legend.items:
        #     self.legend.removeItem(item)

        colors = 'brgcmykw'
        no_colors = len(colors)
        linetypes = [Qt.SolidLine, Qt.DashLine, Qt.DotLine, Qt.DashDotLine, Qt.DashDotDotLine]
        no_linetypes = len(linetypes)

        for i, (name, d) in enumerate(data.items()):
            ci = i % no_colors
            li = i // no_colors % no_linetypes
            curve = pg.PlotCurveItem(d['x'], d['y'], name=name,
                                     pen={'color': colors[ci], 'width': 2, 'sytle': linetypes[li]})
            self.pw.addItem(curve)

    def set_title(self, title):
        """ Sets title to plot """
        self.pw.setTitle(title)

    def set_axis_label(self, label):
        self.pw.setLabel(label['position'], label['name'], units=label['units'])


class EmptyContextMenuViewBox(pg.ViewBox):

    def __init__(self, parent=None, border=None, lockAspect=False, enableMouse=True, invertY=False, enableMenu=True, name=None):
        pg.ViewBox.__init__(self, parent, border, lockAspect, enableMouse, invertY, enableMenu, name)

        self.menu = None
        self.menu = self.get_menu(None)

    def raiseContextMenu(self, ev):
        if not self.menuEnabled(): return
        menu = self.getMenu(ev)
        pos  = ev.screenPos()
        menu.popup(QPoint(pos.x(), pos.y()))

    def get_menu(self, event):
        if self.menu is None:
            self.menu = QMenu()
        return self.menu
