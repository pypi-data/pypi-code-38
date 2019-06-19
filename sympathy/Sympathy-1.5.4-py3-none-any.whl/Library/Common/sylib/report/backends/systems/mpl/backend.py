# Copyright (c) 2015, Combine Control Systems AB
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
import functools
import os.path

from sympathy.api import qt as qt_compat
from sympathy.api.exceptions import sywarn
QtCore = qt_compat.QtCore # noqa
QtGui = qt_compat.QtGui # noqa
qt_compat.backend.use_matplotlib_qt() # noqa

try:
    from matplotlib.backends import qt_compat
except ImportError:
    from matplotlib.backends import qt4_compat  # noqa

from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas)
from matplotlib.figure import Figure

from sylib.report import models
from sylib.report import plugins
from sylib.report import patterns
from sylib.report import data_manager
from sylib.report import ruler


COLOR_SCALES = {
    'cubehelix': 'cubehelix',
    'rainbow': 'jet',
    'blues': 'Blues',
    'yellow-green-blue': 'YlGnBu',
    'summer': 'summer',
    'pink': 'pink',
    'brown and blue': 'BrBG',
    'red and blue': 'RdBu'}


def wrap_and_bind(binding_context, widget, source_property, target_getter,
                  target_setter):
    """
    Convenience wrap and bind which also connects destructor of canvas to
    unregister binding.
    :param binding_context: Binding context.
    :param widget: Canvas widget.
    :param source_property: Source property.
    :param target_getter: Target property getter.
    :param target_setter: Target property setter.
    """
    wrapper = binding_context.wrap_and_bind(source_property, target_getter,
                                            target_setter)
    widget.destroyed.connect(functools.partial(__unregister, binding_context,
                                               wrapper))


def __unregister(binding_context, wrapper):
    QtGui.QApplication.processEvents()
    binding_context.unregister_target(wrapper)


def init_widget(self):
    self._parent = None
    self._rulers = (None, None)
    self._scrollbars = (None, None)
    self.setMouseTracking(True)


def mouse_event(self, event):
    if all(self._rulers):
        pos = event.pos()
        if self._parent:
            pos = self.mapTo(self._parent, pos)
        self._rulers[0].set_cursor_pos(pos)
        self._rulers[1].set_cursor_pos(pos)
    event.accept()


def wheel_event(self, event):
    def scroll(scrollbar, delta):
        if delta > 0:
            scrollbar.triggerAction(QtGui.QAbstractSlider.SliderSingleStepSub)
            scrollbar.triggerAction(QtGui.QAbstractSlider.SliderSingleStepSub)
        else:
            scrollbar.triggerAction(QtGui.QAbstractSlider.SliderSingleStepAdd)
            scrollbar.triggerAction(QtGui.QAbstractSlider.SliderSingleStepAdd)
    if all(self._scrollbars):
        if event.orientation() == QtCore.Qt.Horizontal:
            scroll(self._scrollbars[0], event.delta(), )
        else:
            scroll(self._scrollbars[1], event.delta())
    event.accept()


class PageWidget(QtGui.QWidget):
    def __init__(self, widget=None):
        super(PageWidget, self).__init__(widget)
        init_widget(self)

    def mouseMoveEvent(self, event):
        mouse_event(self, event)

    def wheelEvent(self, event):
        wheel_event(self, event)

    def set_parent(self, parent):
        self._parent = parent

    def set_rulers(self, horizontal, vertical):
        self._rulers = (horizontal, vertical)

    def set_scrollbars(self, horizontal, vertical):
        self._scrollbars = (horizontal, vertical)


class TextWidget(QtGui.QLabel):
    def __init__(self):
        super(TextWidget, self).__init__()
        init_widget(self)

    def mouseMoveEvent(self, event):
        mouse_event(self, event)

    def wheelEvent(self, event):
        wheel_event(self, event)

    def set_parent(self, parent):
        self._parent = parent

    def set_rulers(self, horizontal, vertical):
        self._rulers = (horizontal, vertical)

    def set_scrollbars(self, horizontal, vertical):
        self._scrollbars = (horizontal, vertical)


class ItemFactory(object):
    def __init__(self, binding_context):
        self.binding_context = binding_context

        self.item_mapping = {
            models.Pages: self._create_pages,
            models.Page: self._create_page,
            models.Layout: self._create_layout,
            models.TextBox: self._create_textbox,
            models.Image: self._create_image,
            models.Graph: self._create_graph,
            models.GraphDimensions: self._create_graph_dimensions,
            models.GraphDimension: None,
            models.GraphAxis: None,
            models.GraphLayers: self._create_graph_layers,
            models.GraphLayer: None,
            models.GraphLayerData: None,
            models.GraphLayerDataDimension: None
        }

    def build(self, item_model):
        """
        Handle the given item model in its appropriate factory.
        :param item_model: Item model from model_wrapper.
        :return: Factory result.
        """
        # Make build process a bit more responsive by processing the event
        # queue.
        QtGui.QApplication.processEvents()
        return self.item_mapping[type(item_model)](item_model)

    def _create_pages(self, pages_model):
        """
        Create container for pages.
        :param pages_model: Model describing pages from model_wrapper.
        :return: Widget representing pages.
        """
        assert isinstance(pages_model, models.Pages)
        tab_widget = QtGui.QTabWidget()
        tab_widget.setTabPosition(QtGui.QTabWidget.South)
        for page_model in pages_model.children:
            page_widget = self.build(page_model)

            scroll_layout = QtGui.QGridLayout()
            scroll_widget = QtGui.QScrollArea()
            scroll_widget.setWidgetResizable(True)

            horizontal_ruler = ruler.Ruler(ruler.Ruler.HORIZONTAL)
            vertical_ruler = ruler.Ruler(ruler.Ruler.VERTICAL)

            page_widgets = page_widget.findChildren(QtGui.QWidget)
            page_widgets.append(page_widget)
            for widget in page_widgets:
                widget.set_parent(page_widget)
                widget.set_rulers(horizontal_ruler, vertical_ruler)
                widget.set_scrollbars(
                    scroll_widget.horizontalScrollBar(),
                    scroll_widget.verticalScrollBar())

            scroll_layout.addWidget(horizontal_ruler, 0, 0, 1, 10)
            scroll_layout.addItem(QtGui.QSpacerItem(0, 0), 0, 10)
            scroll_layout.addWidget(page_widget, 1, 0, 15, 9)
            scroll_layout.addWidget(vertical_ruler, 1, 10, 15, 1)
            scroll_layout.setColumnStretch(1, 1)
            scroll_layout.setRowStretch(1, 1)
            scroll_layout.setHorizontalSpacing(0)
            scroll_layout.setVerticalSpacing(0)

            scroll_area = QtGui.QWidget()
            scroll_area.setLayout(scroll_layout)
            scroll_widget.setWidget(scroll_area)

            index = tab_widget.addTab(scroll_widget, page_model.label)
            properties = page_model.properties_as_dict()
            wrap_and_bind(
                self.binding_context,
                tab_widget,
                properties['title'],
                functools.partial(tab_widget.tabText, index),
                functools.partial(tab_widget.setTabText, index))
        return tab_widget

    def _create_page(self, page_model):
        """
        Create a single page.
        :param page_model: Model describing page from model_wrapper.
        :return: Widget representing page.
        """
        assert len(page_model.children) <= 1
        assert isinstance(page_model, models.Page)

        # Only one child per page is allowed.
        if len(page_model.children) == 1:
            page_content_model = page_model.children[0]
            page_content = self.build(page_content_model)
            if isinstance(page_content, QtGui.QLayout):
                widget = PageWidget()
                widget.setLayout(page_content)
                return widget
            return page_content
        return PageWidget()

    def _create_layout(self, layout_model):
        """
        Create layout.
        :param layout_model: Model describing layout from model_wrapper.
        :return: Layout element.
        """
        assert isinstance(layout_model, models.Layout)
        kind = layout_model.data['kind']
        if kind == 'horizontal':
            layout = QtGui.QHBoxLayout()
        elif kind == 'vertical':
            layout = QtGui.QVBoxLayout()
        else:
            raise ValueError('Unhandled layout kind {}'.format(kind))

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        for child in layout_model.children:
            item = self.build(child)
            if isinstance(item, QtGui.QLayout):
                layout.addLayout(item)
            else:
                layout.addWidget(item)

        return layout

    def _create_textbox(self, textbox_model):
        """
        Create textbox.
        :param textbox_model: Model for TextBox.
        :return: TextBox element.
        """
        assert isinstance(textbox_model, models.TextBox)
        properties = textbox_model.properties_as_dict()
        widget = TextWidget()

        def update_label(widget_, value):
            widget_.setText(value)
            widget_.update()

        def align_setter(widget_, model_, _):
            prop = model_.properties_as_dict()
            halign = prop['halign'].get()
            valign = prop['valign'].get()
            hval = {'left': QtCore.Qt.AlignLeft,
                    'center': QtCore.Qt.AlignHCenter,
                    'right': QtCore.Qt.AlignRight}
            vval = {'top': QtCore.Qt.AlignTop,
                    'center': QtCore.Qt.AlignVCenter,
                    'bottom': QtCore.Qt.AlignBottom}
            try:
                flags = hval[halign] | vval[valign]
                widget_.setAlignment(flags)
                widget_.update()
            except KeyError:
                pass

        def width_setter(widget_, model_, _):
            FIXED = QtGui.QSizePolicy.Fixed  # noqa
            MINIMUM = QtGui.QSizePolicy.Minimum  # noqa

            prop = model_.properties_as_dict()
            width = prop['width'].get()
            height = prop['height'].get()
            try:
                widget_.setMinimumSize(width, height)
            except TypeError:
                widget_.setMinimumSize(0, 0)
            widget_.setSizePolicy(FIXED if width else MINIMUM,
                                  FIXED if height else MINIMUM)
            widget_.setWordWrap(True)
            widget_.update()

        wrap_and_bind(self.binding_context, widget, properties['text'],
                      widget.text, functools.partial(update_label, widget))
        wrap_and_bind(self.binding_context, widget, properties['halign'],
                      properties['halign'].get,
                      functools.partial(align_setter, widget, textbox_model))
        wrap_and_bind(self.binding_context, widget, properties['valign'],
                      properties['valign'].get,
                      functools.partial(align_setter, widget, textbox_model))
        wrap_and_bind(self.binding_context, widget, properties['width'],
                      widget.text,
                      functools.partial(width_setter, widget, textbox_model))
        wrap_and_bind(self.binding_context, widget, properties['height'],
                      widget.text,
                      functools.partial(width_setter, widget, textbox_model))

        return widget

    @staticmethod
    def _create_image(image_model):
        """
        Create image.
        :param image_model: Model for Image.
        :return: Image element.
        """
        assert isinstance(image_model, models.Image)
        properties = image_model.properties_as_dict()
        path = properties['image'].get()
        if os.path.exists(path):
            widget = ImageWidget(path)
        else:
            widget = PageWidget()
        return widget

    def _bind_axes(self, dimension_list, axes, canvas, graph_node):
        """
        Binding function for axes.
        :param dimension_list: List of dimension objects.
        :param axes: Axes object to bind to.
        :param canvas: Canvas which is used for drawing.
        :param graph_node: Graph node of property tree.
        """
        def update_label(parameters, value):
            canvas_ = parameters['canvas']
            dim = parameters['dimension']
            if value == '':
                layers = parameters['graph_model'].layers()
                if len(layers):
                    layer = layers[0]
                    _, ds_properties = layer.extract_data_and_properties()
                    value = ds_properties[dim].get()
            if dim == 0:
                axes.set_xlabel(value)
            else:
                axes.set_ylabel(value)
            canvas_.draw_idle()

        def update_scale_type(canvas_, dim, value):
            if dim == 0:
                axes.set_xscale(value)
            else:
                axes.set_yscale(value)
            canvas_.draw_idle()

        def update_extent(parameters, min_prop, max_prop, value):
            min_ = min_prop.get()
            max_ = max_prop.get()
            parameters['extent'] = lambda: value
            update_view_interval(parameters, (min_, max_))

        def update_axis_min(parameters, value):
            _, max_ = parameters['axis'].get_view_interval()
            update_view_interval(parameters, (value, max_))

        def update_axis_max(parameters, value):
            min_, _ = parameters['axis'].get_view_interval()
            update_view_interval(parameters, (min_, value))

        def update_view_interval(parameters, value):
            """
            Update view interval given domain or layer data if the scale
            has extent set.
            :param parameters: {
                                 canvas      : the canvas object,
                                 dimension   : integer with dimension #,
                                 axis        : the axis object,
                                 graph_model : graph model for the graph
                                 extent      : fit to data getter
                               }
            """
            min_range = float(value[0])
            max_range = float(value[1])
            layers = parameters['graph_model'].layers()
            if parameters['extent']() and layers:
                min_range = float('inf')
                max_range = -float('inf')
                for layer in layers:
                    extent = layer.extent_of_layer_data(
                        parameters['dimension'])
                    min_range = min(extent[0], min_range)
                    max_range = max(extent[1], max_range)

            parameters['axis'].set_view_interval(
                min_range, max_range, ignore=True)
            parameters['canvas'].draw_idle()

        dummy_getter = lambda: None  # noqa

        for dim, axis in enumerate((axes.get_xaxis(), axes.get_yaxis())):
            # Bind axis ranges
            wrap_and_bind(self.binding_context,
                          canvas,
                          source_property=dimension_list[dim]['min'],
                          target_getter=dummy_getter,
                          target_setter=functools.partial(
                              update_axis_min,
                              {'canvas': canvas,
                               'dimension': dim,
                               'axis': axis,
                               'graph_model': graph_node,
                               'extent': dimension_list[dim]['extent'].get}))
            wrap_and_bind(self.binding_context,
                          canvas,
                          source_property=dimension_list[dim]['max'],
                          target_getter=dummy_getter,
                          target_setter=functools.partial(
                              update_axis_max,
                              {'canvas': canvas,
                               'dimension': dim,
                               'axis': axis,
                               'graph_model': graph_node,
                               'extent': dimension_list[dim]['extent'].get}))

            # Bind title.
            try:
                wrap_and_bind(self.binding_context,
                              canvas,
                              source_property=dimension_list[dim]['title'],
                              target_getter=dummy_getter,
                              target_setter=functools.partial(
                                  update_label,
                                  {'canvas': canvas,
                                   'dimension': dim,
                                   'graph_model': graph_node}))
            except IndexError:
                pass

            # Bind axes properties (scale and extent)
            wrap_and_bind(self.binding_context,
                          canvas,
                          source_property=dimension_list[dim]['scale_type'],
                          target_getter=dummy_getter,
                          target_setter=functools.partial(
                              update_scale_type, canvas, dim))
            wrap_and_bind(self.binding_context,
                          canvas,
                          source_property=dimension_list[dim]['extent'],
                          target_getter=dummy_getter,
                          target_setter=functools.partial(
                              update_extent,
                              {'canvas': canvas,
                               'dimension': dim,
                               'axis': axis,
                               'graph_model': graph_node,
                               'extent': None},
                              dimension_list[dim]['min'],
                              dimension_list[dim]['max']))

    def _create_graph(self, graph_model):
        """
        Create graph with all its contents.
        :param graph_model: Model describing layout from model_wrapper.
        :return: Graph element.
        """
        assert isinstance(graph_model, models.Graph)

        widget = PageWidget()
        widget_layout = QtGui.QVBoxLayout()
        widget.setLayout(widget_layout)
        widget.setContentsMargins(0, 0, 0, 0)

        fig = Figure()
        if graph_model.properties_as_dict()['projection'].get() == 'polar':
            axes = fig.add_subplot(111, projection='polar')
        else:
            axes = fig.add_subplot(111)
        axes.set_autoscalex_on(False)
        axes.set_autoscaley_on(False)
        fig.set_facecolor((0.0, 0.0, 0.0, 0.0))
        fig.set_tight_layout(True)
        canvas = CanvasWidget(fig)

        def set_title(axes_, canvas_, value):
            axes_.set_title(value)
            canvas_.draw_idle()

        def set_grid(axes_, canvas_, value):
            axes_.grid(value)
            canvas_.draw_idle()

        def set_height(fig_, canvas_, height_pixels):
            # Since matplotlib 1.5 it seems like we need to resize both the
            # figure and the canvas manually:
            width_inches, _ = fig_.get_size_inches()
            height_inches = height_pixels / float(fig_.dpi)
            fig_.set_size_inches(width_inches, height_inches)
            canvas_.setFixedHeight(height_pixels)

        def set_width(fig_, canvas_, width_pixels):
            # Since matplotlib 1.5 it seems like we need to resize both the
            # figure and the canvas manually:
            _, height_inches = fig_.get_size_inches()
            width_inches = width_pixels / float(fig_.dpi)
            fig_.set_size_inches(width_inches, height_inches)
            canvas_.setFixedWidth(width_pixels)

        accessor_map = {
            'width': (widget.width,
                      functools.partial(set_width, fig, canvas)),
            'height': (widget.height,
                       functools.partial(set_height, fig, canvas)),
            'title': (axes.get_title,
                      functools.partial(set_title, axes, canvas)),
            'grid': (lambda: axes._gridOn,
                     functools.partial(set_grid, axes, canvas))
        }

        dimension_list = None
        for p in graph_model.properties:
            if p.property in accessor_map:
                wrap_and_bind(self.binding_context, canvas, p,
                              *accessor_map[p.property])

        for child in graph_model.children:
            if isinstance(child, models.GraphDimensions):
                dimension_list = self._create_graph_dimensions(child)
            # or layers.
            elif isinstance(child, models.GraphLayers):
                self._create_graph_layers(child, axes, canvas)

        # We let each layer take responsibility for managing and adding their
        # own artists, hence removing code below. This is necessary since some
        # plots change the number of artists depending on some property.
        # One example is a 1D-histogram where the number of rectangles change
        # when the number of bins change. It also simplifies being able to
        # reuse existing MPL-plots which are adding the elements automatically.
        try:
            self._bind_axes(dimension_list, axes, canvas, graph_model)
        except KeyError:
            sywarn(
                'Input data has changed. Review settings that '
                'use column data etc.')
            pass

        widget_layout.addWidget(canvas)

        return widget

    @staticmethod
    def _create_graph_dimensions(graph_dimensions_model):
        """
        Create list of dimensions in the given graph.
        :param graph_dimensions_model: model.GraphDimensions object.
        :return: List of dimensions.
        """
        assert isinstance(graph_dimensions_model, models.GraphDimensions)

        dimension_list = []
        for dimension_model in graph_dimensions_model.children:
            dimension_dict = {}
            for dimension_axis in dimension_model.children:
                dimension_dict = dimension_axis.properties_as_dict()
            dimension_list.append(dimension_dict)

        return dimension_list

    def _create_graph_layers(self, graph_layers_model, axes, canvas):
        """
        Create layers in graph.
        :param graph_layers_model: models.GraphLayers object.
        :param axes: MPL-axes object.
        :param canvas: MPL-canvas object appearing as a QWidget.
        :return: List of layers.
        """
        assert isinstance(graph_layers_model, models.GraphLayers)

        layer_list = []
        for z_order, layer_model in enumerate(graph_layers_model.children):
            layer_type = layer_model.data['type']
            try:
                layer_creator = plugins.layer_modules[
                    layer_type].renderer_mpl.create_layer
            except KeyError:
                raise ValueError('Unknown layer type {}'.format(layer_type))
            try:
                layer_object = layer_creator(self.binding_context,
                                             {'layer_model': layer_model,
                                              'axes': axes,
                                              'canvas': canvas,
                                              'z_order': z_order})
                layer_list.append(layer_object)
            except ValueError:
                sywarn('Input data missing. Please run preceeding nodes.')

        return layer_list


def bind_artist(binding_context, parameters):
    """
    Convenience function for binding a model.Property to a generic Artist
    object.
    :param binding_context: Binding context.
    :param parameters: Dictionary containing:
                       'property': model.Property object.
                       'getter': Getter function for target.
                       'setter': Setter function for target.
                       'canvas': Canvas used for rendering.
                       'kind': "numeric" or "color".
    """
    def update_property(canvas_, setter_, value):
        setter_(value)
        # We cannot catch exceptions from this call.
        canvas_.draw_idle()

    def update_numeric_property(canvas_, setter_, value):
        if patterns.re_numeric.match('{}'.format(value)) is None:
            return
        update_property(canvas_, setter_, value)

    def update_color_property(canvas_, setter_, value):
        if patterns.re_color.match(value) is None:
            return
        update_property(canvas_, setter_, value)

    f = {'numeric': update_numeric_property,
         'color': update_color_property,
         'string': update_property}

    wrap_and_bind(binding_context,
                  parameters['canvas'],
                  source_property=parameters['property'],
                  target_getter=parameters['getter'],
                  target_setter=functools.partial(f[parameters['kind']],
                                                  parameters['canvas'],
                                                  parameters['setter']))


def bind_artist_list(binding_context, parameters):
    """
    Convenience function for binding a model.Property to a list of Artist
    objects.
    :param binding_context: Binding context.
    :param parameters: Dictionary containing:
                       'property': model.Property object.
                       'artists': Function returning list of artists.
                       'getter_func': Function returning a getter for object.
                       'setter_func': Function returning a setter for object.
                       'canvas': Canvas used for rendering.
                       'kind': "numeric" or "color".
    """
    def update_properties(parameters_, value):
        for artist in parameters_['artists']():
            setter_ = parameters_['setter_func'](artist)
            setter_(value)
        parameters_['canvas'].draw_idle()

    def update_numeric_properties(parameters_, value):
        if patterns.re_numeric.match('{}'.format(value)) is None:
            return
        update_properties(parameters_, value)

    def update_color_properties(parameters_, value):
        if patterns.re_color.match(value) is None:
            return
        update_properties(parameters_, value)

    f = {'numeric': update_numeric_properties,
         'color': update_color_properties,
         'string': update_properties}

    # Where should we fetch data from target object if it is a list?
    # Here we are getting data from the property instead.
    wrap_and_bind(binding_context,
                  parameters['canvas'],
                  source_property=parameters['property'],
                  target_getter=parameters['property'].get,
                  target_setter=functools.partial(f[parameters['kind']],
                                                  parameters))


def calculate_scaled_value(model, property_node):
    """
    If a property has a scale it should be used to transform data.
    :param model: A data model node.
    :param property_node: Value or binding expression.
    :return: Processed value.
    """
    if not property_node.has_binding:
        return property_node.get()

    scale_binding = property_node.scale_binding
    data_id, scale_id = scale_binding.data_id, scale_binding.scale_id
    data = data_manager.data_source.data(data_id)
    scale_model = model.root_node().find_node(models.RootScale, scale_id)
    if data is None or scale_model is None:
        return None
    scale = scale_model.create_scale(data)
    y = scale(data)
    return y


class ImageWidget(PageWidget):
    def __init__(self, image, parent=None):
        super(ImageWidget, self).__init__(parent)
        self.image = QtGui.QImage(image)
        self.setMinimumSize(self.image.size())
        self.setMaximumSize(self.image.size())

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.drawImage(0, 0, self.image)


class CanvasWidget(PageWidget, FigureCanvas):
    def __init__(self, figure):
        super(CanvasWidget, self).__init__(figure)
