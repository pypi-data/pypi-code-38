# -*- coding: utf-8 -*-

"""package benutils
author    Benoit Dubois
copyright FEMTO Engineering, 2019
license   GPL v3.0+
brief     Package dedicated to plot real time graph.
"""

from PyQt5.QtCore import pyqtSignal, QSignalMapper, Qt
from PyQt5.QtWidgets import QWidget, QCheckBox, QPushButton, QHBoxLayout, \
     QVBoxLayout, QApplication, QColorDialog, QDialog, \
     QDialogButtonBox, QLineEdit, QLabel, QCheckBox
from PyQt5.QtGui import QColor, QDoubleValidator

from pyqtgraph import PlotWidget, ViewBox, mkPen, PlotItem


# =============================================================================
class MyDoubleValidator(QDoubleValidator):
    """Override QDoubleValidator to provide a default value when value
    is not acceptable.
    """

    def __init__(self, parent=None, default=0.0):
        """Constructor.
        :returns: None
        """
        super().__init__(parent=parent)
        self._default = str(default)
        self._parent = parent

    def fixup(self, input_):
        self._parent.setText(self._default)


# =============================================================================
class CurveParam(object):
    """ScaleParam class, generates a container for a set of curve parameters.
    """

    def __init__(self, label, scale=1.0, offset=0.0):
        """Constructor.
        :param label: label of curve (str)
        :param scale: scale factor to be applied to the curve (float)
        :param offset: offset to be applied to the curve (float)
        :returns: None
        """
        super().__init__()
        self.label = label
        self.scale = scale
        self.offset = offset


# =============================================================================
class CurveParamDialog(QDialog):
    """CurveParamDialog class, generate a dialog box used to get back parameters
    of a curve.
    """

    def __init__(self, param, parent=None):
        """Constructor.
        :param param: curve parameters (CurveParam)
        :param parent: parent of widget (object)
        :returns: None
        """
        super().__init__(parent=parent)
        self.setWindowTitle("Curve parameters")
        # Lays out
        self._label_led = QLineEdit()
        self._label_led.setText(param.label)
        self._scale_led = QLineEdit()
        self._scale_validator = MyDoubleValidator(self._scale_led, 1.0)
        self._scale_led.setValidator(self._scale_validator)
        self._scale_led.setText(str(param.scale))
        self._offset_led = QLineEdit()
        self._offset_validator = MyDoubleValidator(self._offset_led, 0.0)
        self._offset_led.setValidator(self._offset_validator)
        self._offset_led.setText(str(param.offset))
        self._btn_box = QDialogButtonBox(QDialogButtonBox.Ok |
                                         QDialogButtonBox.Cancel)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Label"))
        layout.addWidget(self._label_led)
        layout.addWidget(QLabel("Scaling factor"))
        layout.addWidget(self._scale_led)
        layout.addWidget(QLabel("Offset"))
        layout.addWidget(self._offset_led)
        layout.addWidget(self._btn_box)
        self.setLayout(layout)
        # Basic logic
        self._btn_box.accepted.connect(self.accept)
        self._btn_box.rejected.connect(self.close)

    @property
    def scale(self):
        """Getter of the scale factor value.
        :returns: scale factor value (float)
        """
        return float(self._scale_led.text())

    @property
    def offset(self):
        """Getter of the offset value.
        :returns: offset value (float)
        """
        return float(self._offset_led.text())

    @property
    def label(self):
        """Getter of the label value.
        :returns: label value (str)
        """
        return self._label_led.text()


# =============================================================================
class DictPlotWidget(PlotWidget):
    """DictPlot class, enhances PlotWidget class with a dictionnay like handling
    of the curves.
    Examples:
    - Add a new curve: dict_graph_object.add_curve("key_name", "label")
    - Indexing curve: dict_graph_object.curve("key_name")
    """

    # Emitted when the data in an item is updated. Sends the key identifier of
    # the item.
    sigPlotChanged = pyqtSignal(object)
    # Emitted when the item is clicked. Sends the key identifier of the item.
    sigClicked = pyqtSignal(object)
    # Emitted when a plot point is clicked. Sends the item object and
    # the list of points under the mouse.
    sigPointsClicked = pyqtSignal(object, list)

    def __init__(self, parent=None, background='default', **kargs):
        """Constructor.
        :returns: None
        """
        super().__init__(parent=parent,
                         background=background, **kargs)
        self.enableAutoRange(ViewBox.XYAxes, True)
        self.showButtons()
        self.showGrid(True, True, 0.5)
        self._curves = {}

    def __iter__(self):
        """Iterator over dictionnary of curve.
        :returns: iterator over dictionnary of curve (iterator)
        """
        return iter(self._curves)

    def curve(self, key):
        """Getter of curve object (PlotDataItem).
        :param key: key identifier of the curve (object)
        :returns: a curve object (PlotDataItem)
        """

        print(key)
        print(self._curves)
        
        return self._curves[key]

    def add_curve(self, key, label=""):
        """Adds the plot 'keyname' ie a curve (PlotDataItem) to the widget.
        :param key: key identifier of the curve (object)
        :param label: label of the curve, default is the key (str)
        :returns: None
        """
        if label == "":
            label = str(key)
        self._curves[key] = self.plot()  # name=label)
        # Re-raises signals from added item
        self._curves[key].sigPlotChanged.connect( \
            lambda: self._sig_plot_changed(key))
        self._curves[key].sigClicked.connect( \
            lambda: self._sig_clicked(key))
        self._curves[key].sigPointsClicked.connect( \
            self._sig_points_clicked)

    def remove_curve(self, key):
        """Removes the plot 'keyname' ie a curve to widget.
        :param key: key identifier of curve (object)
        :returns: None
        """
        self._curves[key].sigPlotChanged.disconnect()
        self._curves[key].sigClicked.disconnect()
        self._curves[key].sigPointsClicked.disconnect()
        self.removeItem(self._curves[key])
        self._curves.pop(key) 

    def _sig_plot_changed(self, key):
        """Generates sigPlotChanged signal. Collects all call from differents
        PlotDataItem composing PlotWidget than redirects them to sigPlotChanged.
        :param key: key identifier of curve (object)
        :returns: None
        """
        self.sigPlotChanged.emit(key)

    def _sig_clicked(self, key):
        """Generates sigClicked signal. Collects all call from differents
        PlotDataItem composing PlotWidget than redirects them to sigClicked.
        :param key: key identifier of curve (object)
        :returns: None
        """
        self.sigClicked.emit(key)

    def _sig_points_clicked(self, points):
        """Generates sigPointsClicked signal. Collects all call from
        differents PlotDataItem composing PlotWidget than redirects them
        to sigPointsClicked.
        :param points: points clicked in curve (np.array)
        :returns: None
        """
        sender = self.sender()
        self.sigPointsClicked.emit(sender, points)


# =============================================================================
class ChannelLegend(QWidget):
    """ChannelLegend widget class, used to display label and handle the behavior
    of a curve (color, label, transformations).
    """

    # Emited when the state of the widget ie the state of the MyQCheckBox
    # changes. Sends the new state value (Qt.State).
    state_changed = pyqtSignal(int)
    # Emited when the color button changes. Sends the new color value (QColor).
    color_changed = pyqtSignal(QColor)
    # Emited when the parameters of parameters changes. Sends the new
    # parameter values (CurveParam).
    parameters_changed = pyqtSignal(CurveParam)

    def __init__(self, parameters, color=None, \
                 parent=None):
        """Constructor.
        :param parameters: parameters of the curve (dict)
        :param color: the color of the curve (QColor)
        :param label: the label of the curve (str)
        :param parent: parent of widget (object)
        :returns: None
        """
        super().__init__(parent=parent)
        self._en_ckbox = QCheckBox()
        self._en_ckbox.setText(parameters.label)
        self._color_btn = QPushButton()
        self._color_btn.setMaximumWidth(20)
        self._color_btn.setAutoFillBackground(True)
        self._color_btn.setFlat(True)
        self.set_color(color)
        self.set_parameters(parameters)
        layout = QHBoxLayout()
        layout.addWidget(self._en_ckbox)
        layout.addWidget(self._color_btn)
        self.setLayout(layout)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self._en_ckbox.stateChanged.connect(self.state_changed)
        self._color_btn.released.connect(self._choose_color)
        self.customContextMenuRequested.connect(self._context_menu_requested)

    def set_label(self, label):
        """Set the label property.
        :param label: the label of the curve (str)
        :returns: None
        """
        self._en_ckbox.setText(label)

    def set_color(self, color):
        """Set the color property.
        :param color: the color of the curve (QColor)
        :returns: None
        """
        self._color = color
        if color is None:
            return
        style = "background-color : {}; border: none;".format(color.name())
        self._color_btn.setStyleSheet(style)
        self.color_changed.emit(color)

    def set_parameters(self, parameters):
        """Set the tranformation properties.
        :param parameters: the parameters of the curve. (dict)
        :returns: None
        """
        self.set_label(parameters.label)
        self._parameters = parameters
        self.parameters_changed.emit(parameters)

    @property
    def parameters(self):
        """Get the parameters properties.
        :returns: the parameters of the curve (dict)
        """
        return self._parameters

    @property
    def label(self):
        """Get the label property.
        :returns: the label of the curve (str)
        """
        return self._en_ckbox.text()

    @property
    def color(self):
        """Gets the color property.
        :returns: the color of the curve (QColor)
        """
        return self._color

    def checkState(self):
        """Gets the state of the widget.
        :returns: the state of the check box (Qt.State)
        """
        return self._en_ckbox.checkState()

    def setState(self, state):
        """Sets the state of the widget.
        :param state: the state of the check box (Qt.State)
        :returns: None
        """
        self._en_ckbox.setCheckState(state)

    def _context_menu_requested(self):
        """Call when user has requested a context menu (with respect to mouse
        click). Opens a parameters dialog box and gets the choosen parameter
        values.
        :returns: None
        """
        dialog = CurveParamDialog(self._parameters)
        dialog.setParent(None, Qt.Dialog)
        retval = dialog.exec_()
        if retval == QDialog.Accepted:            
            parameters = CurveParam(dialog.label, dialog.scale, dialog.offset)
            self.set_parameters(parameters)

    def _choose_color(self):
        """Opens a color dialog box and sets the choosen color as new curve
        color.
        :returns: None
        """
        color = QColorDialog().getColor(self.color, self,
                                        "Select channel color")
        if color.isValid() is True:
            self.set_color(color)


# =============================================================================
class DictChannelLegend(QWidget):
    """DictChannelLegend class, handles a list of ChannelLegend object likes a
    dictionnay.
    """

    # Emited when the state of the widget ie the state of a QCheckBox changes.
    # Sends the new state value (Qt.State).
    state_changed = pyqtSignal(object, int)
    # Emited when the color button changes. Sends the new color value (QColor).
    color_changed = pyqtSignal(object, QColor)
    # Emited when the parameters of the curve changes. Sends the new parameter
    # values (CurveParam).
    parameters_changed = pyqtSignal(object, CurveParam)

    def __init__(self, channel_keys, parent=None):
        """Constructor.
        :param channel_keys: list of key for each of channel in widget (list)
        :returns: None
        """
        super().__init__(parent=parent)
        self._legends = \
          {key: ChannelLegend(CurveParam("Channel " + str(key)), \
              QColor().fromHsv(359*idx/len(channel_keys), 255, 255)) \
              for idx, key in enumerate(channel_keys)}
        #
        self._state_mapper = QSignalMapper()
        self._color_mapper = QSignalMapper()
        self._parameter_mapper = QSignalMapper()
        for key, legend in self._legends.items():
            legend.state_changed.connect(self._state_mapper.map)
            legend.color_changed.connect(self._color_mapper.map)
            legend.customContextMenuRequested.connect( \
                self._parameter_mapper.map)
            self._state_mapper.setMapping(legend, key)
            self._color_mapper.setMapping(legend, key)
            self._parameter_mapper.setMapping(legend, key)
        self._state_mapper.mapped.connect(self._channel_state_changed)
        self._color_mapper.mapped.connect(self._channel_color_changed)
        self._parameter_mapper.mapped.connect(self._channel_parameters_changed)
        #
        layout = QVBoxLayout()
        for legend in self._legends.values():
            layout.addWidget(legend)
        self.setLayout(layout)

    def __iter__(self):
        """Iterator.
        :returns: iterator over the dictionnary of channel legend (iterator)
        """
        return iter(self._legends)

    def values(self):
        """Iterator.
        :returns: iterator over the value of the dictionnary of channel legend
        (iterator)
        """
        return iter(self._legends.values())

    def items(self):
        """Iterator.
        :returns: iterator over the items (ie key, value) of the dictionnary of
        channel legend (iterator)
        """
        return iter(self._legends.items())

    @property
    def legends(self):
        """Getter of the dictionnary of legend object (DictChannelLegend).
        :returns: the dictionnary of legend object (DictChannelLegend)
        """
        return self._legends

    def legend(self, key):
        """Getter of legend object (ChannelLegend).
        :param key: key identifier of the channel (object)
        :returns: a legend object (ChannelLegend)
        """
        return self._legends[key]

    def _channel_parameters_changed(self, key):
        """Emits the signal context_menu_requested when
        :param key: key identifier of the channel (object)
        :returns: None
        """
        parameters = self._legends[key].parameters
        self.parameters_changed.emit(key, parameters)

    def _channel_state_changed(self, key):
        """Emits the signal state_changed when the state of a legend channel
        changes.
        :param key: key identifier of the channel (object)
        :returns: None
        """
        state = self._legends[key].checkState()
        self.state_changed.emit(key, state)

    def _channel_color_changed(self, key):
        """Emits the signal color_changed when the color of a legend channel
        changes.
        :param key: key identifier of the channel (object)
        :returns: None
        """
        color = self._legends[key].color
        self.color_changed.emit(key, color)


class EPlotWidget(QWidget):
    """EPlotWidget class, enhanced Plot Widget used to display numeral data.
    """

    def __init__(self, channel_keys, parent=None):
        """Constructor.
        :param channel_keys: list of key for each of channel in widget (list)
        :returns: None
        """
        super().__init__(parent=parent)
        self._dict = DictChannelLegend(channel_keys)
        self._plot = DictPlotWidget(parent=parent)
        self._plot.setBackground('w')
        # Disabled by default because during rendering it looks causing problem.
        # In fact, it ONLY looks (for users) like a bug but it's not.
        # self._plot.setDownsampling(ds=True, auto=True, mode='peak')
        # Lays-out
        main_layout = QHBoxLayout()
        main_layout.addWidget(self._dict)
        main_layout.addWidget(self._plot)
        self.setLayout(main_layout)
        # Maps signal from channel legend widget
        self._dict.state_changed.connect(self._set_curve_visible)
        self._dict.color_changed.connect(self._set_curve_color)

    def __iter__(self):
        """Iterator.
        :returns: iterator over the dictionnary of channel (iterator)
        """
        return iter(self._dict)

    def reset(self):
        """Resets UI.
        :returns: None
        """
        for legend in self._dict.values():
            legend.setState(Qt.Unchecked)
            legend.setDisabled(True)
        self._plot.getPlotItem().clear()

    @property
    def plot(self):
        """Getter of the plot object (DictPlotWidget).
        :returns: the plot object (DictPlotWidget)
        """
        return self._plot

    @property
    def dict(self):
        """Getter of the dictionnary of legend object (DictChannelLegend).
        :returns: the dictionnary of legend object (DictChannelLegend)
        """
        return self._dict

    def curve(self, key):
        """Getter of curve object (PlotDataItem).
        :param key: key identifier of the curve (object)
        :returns: a curve object (PlotDataItem)
        """
        return self._plot.curve(key)

    def legend(self, key):
        """Getter of legend object (ChannelLegend).
        :param key: key identifier of the curve (object)
        :returns: a legend object (ChannelLegend)
        """
        return self._dict.legend(key)

    def add_curve(self, key, label=""):
        """Adds the plot 'keyname' ie a curve (PlotDataItem) to the plot widget.
        :param key: key identifier of the curve (object)
        :param label: label of the curve, default is the key (str)
        :returns: None
        """
        self._plot.add_curve(key, label)
        color = self._dict.legend(key).color
        self._set_curve_color(key, color)

    def remove_curve(self, key):
        """Removes the plot 'keyname' ie a curve to widget.
        :param key: key identifier of curve (object)
        :returns: None
        """
        self._plot.remove_curve(key)

    def set_data(self, key, *data):
        """Sets data to the plot with 'key'.
        :param key: key identifier of the curve (object)
        :param data: data compatible with PlotDataItem.setData() (see doc)
        :returns: None
        """
        self._plot.curve(key).setData(*data)
        self._plot.repaint()

    def hide(self, key, flag=True):
        """Hides (or not) curve 'key'.
        :param key: key identifier of the curve (object)
        :param flag: if True hide curve else not (bool)
        :returns: None
        """
        if flag is True:
            self._plot.curve(key).setPen(None)
        else:
            color = self._dict.legend(key).color
            self._plot.curve(key).setPen(mkPen(color))

    def _set_curve_visible(self, key, flag):
        """This method holds whether the curve is visible.
        :param key: key identifier of the curve (object)
        :param flag: set curve visible if flag is True
        else curve is invisible (bool)
        :returns: None
        """
        self._plot.curve(key).setVisible(flag)

    def _set_curve_color(self, key, color):
        """Sets color property of curve with 'key'.
        :param key: key identifier of the curve (object)
        :param color: the color of the curve for this channel (QColor)
        :returns: None
        """
        self._plot.curve(key).setPen(mkPen(color))


# =============================================================================
def print_args(*args):
    """Prints 'args', method used as slot.
    """
    for arg in args:
        print("print_args:", arg)


# =============================================================================
def check_dict_plot_widget():
    """Displays a DictPlotWidget.
    """
    import sys

    app = QApplication(sys.argv)

    wdgt = DictPlotWidget()
    wdgt.show()

    sys.exit(app.exec_())


# =============================================================================
def check_channel_legend():
    """Displays a ChannelLegend.
    """
    import sys

    app = QApplication(sys.argv)

    cparam = CurveParam(label='my test label')
    
    wdgt = ChannelLegend(cparam)
    wdgt.state_changed.connect(print_args)
    wdgt.color_changed.connect(print_args)
    wdgt.set_label("Channel 3")
    wdgt.set_color(QColor().fromHsv(0, 255, 255))
    wdgt.show()

    sys.exit(app.exec_())


# =============================================================================
def check_dict_channel_legend():
    """Displays a DictChannelLegend.
    """
    import sys

    app = QApplication(sys.argv)

    wdgt = DictChannelLegend(range(101, 123))
    for i in wdgt:
        print("i:", i)

    wdgt.state_changed.connect(print_args)
    wdgt.color_changed.connect(print_args)
    wdgt.show()

    sys.exit(app.exec_())


# =============================================================================
def check_rt_plot():
    """Checks behavior of "real-time" plotting:
    - displays a plot and a curve updating every second,
    - waits 5 second,
    - adds another curve updating every second.
    """
    import sys

    app = QApplication(sys.argv)
    
    graph = EPlotWidget(range(101, 123))
    graph.plot.setTitle("Check plotting")
    graph.plot.sigPlotChanged.connect(print_args)
    graph.add_curve(101, "Channel 1")

    layout = QVBoxLayout()
    layout.addWidget(graph)
    widget = QWidget()
    widget.setLayout(layout)
    widget.show()

    sys.exit(app.exec_())


# =============================================================================
if __name__ == '__main__':
    # Ctrl-c closes the application
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # check_channel_legend()
    # check_dict_plot_widget()
    # check_dict_channel_legend()
    check_rt_plot()
