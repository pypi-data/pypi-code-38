'''Main bokodapviewer application class definition'''

import os
from collections import OrderedDict
import xml.etree.ElementTree as et

import numpy

from sodapclient import Handler

from bokcolmaps import CMSlicer

from bokeh.models.widgets.tables import DataTable, TableColumn, IntEditor
from bokeh.models.widgets.markups import Paragraph, Div
from bokeh.models.widgets.panels import Panel, Tabs
from bokeh.models.widgets.buttons import Button
from bokeh.models.widgets.inputs import TextInput, Select
from bokeh.models.widgets import CheckboxGroup
from bokeh.models.layouts import WidgetBox, Row, Column
from bokeh.models.sources import ColumnDataSource
from bokeh.plotting import Figure
from bokeh.io import curdoc

from numpy import float32

from bokcolmaps.interp_data import interp_data


class App():

    '''
    A simple OpenDAP data viewer using Bokeh.
    Run with the bokeh server at the command line: bokeh serve --show App.py

    Display data with the following steps:
    1. Enter an OpenDAP URL and press the 'Open URL' button. The DDS will be
    loaded and displayed.
    2. Select a variable (i.e. select a row in the DDS table) and press the
    'Get variable details' button. The DAS and available dimensions will be
    displayed.
    3. Edit the data dimensions (if required) and press the 'Get plot options'
    button.
    4. Select the required plot option in the drop down and enter an
    interpolation interval if required (see below).
    5. Press the 'Get data' button. The data will be loaded and displayed under
    the Data Visualisation tab.

    NB: In order to avoid errors, all steps must be followed in order, i.e.:
    - After opening a new URL, repeat all of steps 2-5 in order.
    - After the selected variable is changed, repeat all of steps 3-5 in order.
    - After selecting new dimensions, press the 'Get plot options' button
      and repeat step 4 then step 5.

    For 2D images both axes must be on a uniform grid so interpolation will be
    done if one of them is not. If a value is entered into the
    Interpolation Interval box it will be used; otherwise the minimum interval
    in the relevant axis grid will be used (this may be slow). For a 2D plot
    with a slider (i.e. 3D volume slices), the slider axis can be non-uniform;
    only the axes for the image itself must be uniform. A non-uniformity
    tolerance percentage can be set: this allows for slight non-uniformity
    in an axis grid (e.g. precision errors) without invoking interpolation.

    When viewing the data the z axis limits can be fixed and all three axes
    can be reversed using the controls below the plot. The 'Update Display'
    button must be pressed to update the plot with the new settings.

    Attributes such as scale factors, offsets, missing and fill values are
    automatically applied. The corresponding names are stored in the config
    file. More than one can be stored, e.g. simply add a config line
    <ScaleFactorName>new_scale_factor</ScaleFactorName> to add the scale factor
    name new_scale_factor. More than one may be needed if different DAS have
    different names for the same thing.

    Other config file settings include the table and plot sizes and whether or
    not a plot cursor readout is required. The app can cope with proxy servers:
    create a simple text file with the proxy details (see the sodapclient
    package for the structure) and include the file path in the config file.
    '''

    def __init__(self):

        self.config_file = 'Config.xml'

        # Plot sizes

        self.main_plot_size = [None, None]
        self.line_plot_size = [None, None]

        # Dictionary of attribute names for scale factors etc.
        self.attr_names = {'ScaleFactorName': [], 'OffsetName': [],
                           'FillValueName': [], 'MissingValueName': []}

        # Read the configuration file to get data sources etc
        self.get_config()

        # Set up the gui
        self.setup_gui()

    def get_config(self):

        '''Read in the xml configuration file'''

        root = et.parse(self.config_file).getroot()

        for child in root:

            if child.tag == 'ProxyFileName':
                proxy_file_name = child.text
            if proxy_file_name == 'None':
                proxy_file_name = None

            if child.tag == 'ColourMapPath':
                self.col_map_path = child.text

            if child.tag == 'TableSize':
                self.table_size = [int(child.attrib['height']),
                                   int(child.attrib['width'])]
            if child.tag == 'MainPlotSize':
                self.main_plot_size = [int(child.attrib['height']),
                                       int(child.attrib['width'])]
            if child.tag == 'LinePlotSize':
                self.line_plot_size = [int(child.attrib['height']),
                                       int(child.attrib['width'])]

            if (child.tag in self.attr_names.keys()) and \
               (child.text not in self.attr_names[child.tag]):
                self.attr_names[child.tag].append(child.text)

            hoverdispmap = dict({'Off': False, 'On': True})

            if child.tag == 'CursorReadout2D':
                self.hoverdisp2d = hoverdispmap[child.text]

            if child.tag == 'CursorReadout3D':
                self.hoverdisp3d = hoverdispmap[child.text]

    def setup_gui(self):

        '''Set up the GUI elements'''

        self.url = TextInput(title='OpenDAP URL:')
        self.open_btn = Button(label='Open URL', button_type='primary')
        self.open_btn.on_click(self.open_url)

        # Set up the data and plot selection tables (initially blank)

        # DDS table

        odt = OrderedDict()
        odt['Variable Name'] = []
        odt['Type'] = []
        odt['Dimensions'] = []
        odt['Dimension Names'] = []
        self.ds_dds = ColumnDataSource(odt)

        cols = []
        for item in iter(odt):
            cols.append(TableColumn(title=item, field=item))
        dds_table = DataTable(source=self.ds_dds, columns=cols, selectable=True,
                              sortable=False, height=self.table_size[0],
                              width=self.table_size[1], index_position=None)

        # DAS table

        odt = OrderedDict()
        odt['Attribute Name'] = []
        odt['Type'] = []
        odt['Value'] = []
        self.ds_das = ColumnDataSource(odt)

        cols = []
        for item in iter(odt):
            cols.append(TableColumn(title=item, field=item))
        das_table = DataTable(source=self.ds_das, columns=cols,
                              selectable=False, sortable=False,
                              height=self.table_size[0],
                              width=self.table_size[1], index_position=None)

        # Selection table

        odt = OrderedDict()
        odt['Dimension'] = []
        odt['First Index'] = []
        odt['Interval'] = []
        odt['Last Index'] = []
        self.ds_select = ColumnDataSource(odt)

        cols = []
        for item in iter(odt):
            if item == 'Dimension':
                cols.append(TableColumn(title=item, field=item))
            else:
                cols.append(TableColumn(title=item, field=item,
                                        editor=IntEditor(step=1)))
        select_table = DataTable(source=self.ds_select, columns=cols,
                                 selectable=True, sortable=True, editable=True,
                                 height=self.table_size[0],
                                 width=self.table_size[1], index_position=None)

        # Selection and Visualisation panels

        self.get_var_btn = Button(label='Get variable details', disabled=True)
        self.get_var_btn.on_click(self.get_var)

        self.p_sel = Paragraph(text='No variable selected.')

        self.get_pltops_btn = Button(label='Get plot options', disabled=True)
        self.get_pltops_btn.on_click(self.get_plot_opts)

        self.plot_ops = Select(options=[])

        self.get_data_btn = Button(label='Get data', button_type='primary',
                                   disabled=True)
        self.get_data_btn.on_click(self.get_data)

        self.endian_chkbox = CheckboxGroup(labels=['Big Endian'], active=[0])

        self.interp_int_box = TextInput(title='Interpolation interval:')
        self.interp_tol_box = TextInput(title='Non-uniform tolerance (%):',
                                        value='1')

        self.revx_chkbox = CheckboxGroup(labels=['Reverse x axis'], active=[])
        self.revy_chkbox = CheckboxGroup(labels=['Reverse y axis'], active=[])
        self.revz_chkbox = CheckboxGroup(labels=['Reverse z axis'], active=[0])

        self.zmin = TextInput(title='z minimum:')
        self.zmax = TextInput(title='z maximum:')

        self.stat_box = Div(text='<font color="green">Initialised OK</font>',
                            width=800)

        self.update_btn = Button(label='Update Display')
        self.update_btn.on_click(self.display_data)

        ws1 = Row(children=[Column(Div(text='<font color="blue">Dataset Descriptor Structure'),
                                   dds_table), Div(), Column(self.get_var_btn, self.p_sel)])
        ws2 = Row(children=[Column(Div(text='<font color="blue">Dataset Attribute Structure'),
                                   das_table), Div(),
                            Column(Div(text='<font color="blue">Dimensions'), select_table)])
        ws3 = Row(children=[self.get_pltops_btn, self.get_data_btn,
                            self.endian_chkbox])
        ws4 = Row(children=[Column(self.plot_ops, Row(self.interp_int_box,
                                                      self.interp_tol_box))])
        wp1 = Row(children=[self.zmin, self.zmax])
        wp2 = Row(children=[self.revx_chkbox, self.revy_chkbox,
                            self.revz_chkbox])
        wp3 = Row(children=[self.update_btn])

        select_panel = Panel(title='Data Selection',
                             child=Column(ws1, ws2, ws3, ws4))

        plot_panel = Panel(title='Data Visualisation',
                           child=Column(WidgetBox(Div()),
                                        Div(text='',
                                            width=self.main_plot_size[1],
                                            height=100),
                                        wp1, wp2, wp3))

        self.tabs = Tabs(tabs=[select_panel, plot_panel])

        self.gui = Column(children=[WidgetBox(self.url, width=1450),
                                    WidgetBox(self.open_btn),
                                    WidgetBox(self.stat_box),
                                    WidgetBox(Div(text='<hr>', width=1320)),
                                    self.tabs])

    def open_url(self):

        '''Open the URL'''

        self.stat_box.text = '<font color="blue">Opening URL...</font>'

        try:
            self.odh = Handler(self.url.value)
        except:
            self.stat_box.text = \
                '<font color="red">Error: could not open URL</font>'
            return

        if self.odh.dds is None:
            self.stat_box.text = \
                '<font color="red">Error: no DDS found at URL</font>'
            return

        var_names, var_types, var_dims, dim_names = [], [], [], []
        for item, attr in sorted(self.odh.dds.items()):
            var_names.append(item)
            var_types.append(attr[0])
            var_dims.append(attr[1])
            dim_names.append(attr[2])

        odt = OrderedDict()
        odt['Variable Name'] = var_names
        odt['Type'] = var_types
        odt['Dimensions'] = var_dims
        odt['Dimension Names'] = dim_names
        self.ds_dds.data = odt

        self.get_var_btn.disabled = False
        # Disable these to avoid mismatch between DDS and stored data
        self.get_pltops_btn.disabled = True
        self.get_data_btn.disabled = True

        self.stat_box.text = '<font color="green">URL opened OK.</font>'

        self.tabs.active = 0

    def get_var(self):

        '''Read variable attributes and dimensions'''

        sel = self.ds_dds.selected.indices

        if len(sel) > 0:

            # Attributes

            self.var_name = self.ds_dds.data['Variable Name'][sel[0]]
            das = self.odh.das[self.var_name]
            attr_name, attr_type, attr_val = [], [], []
            for attr in das:
                atrs = attr.split()
                attr_name.append(atrs[1])
                attr_type.append(atrs[0])
                attr_val.append(atrs[2])

            odt = OrderedDict()
            odt['Attribute Name'] = attr_name
            odt['Type'] = attr_type
            odt['Value'] = attr_val
            self.ds_das.data = odt

            # Selection

            dvals = self.odh.dds[self.var_name][1]
            dmax = []
            for dim in range(len(dvals)):
                dmax.append(dvals[dim] - 1)
            dim_name = self.odh.dds[self.var_name][2]

            odt = OrderedDict()
            odt['Dimension'] = dim_name
            odt['First Index'] = [0] * len(dvals)
            odt['Interval'] = [1] * len(dvals)
            odt['Last Index'] = dmax
            self.ds_select.data = odt

            self.p_sel.text = 'Variable: ' + self.var_name

            self.get_pltops_btn.disabled = False
            self.get_data_btn.disabled = True  # Disable to avoid mismatch

            self.stat_box.text = '<font color="green">Variable selected.</font>'

    def get_plot_opts(self):

        '''
        Get all the available plot options corresponding to the
        selected data dimensions.
        '''

        num_dims = len(self.ds_select.data['Dimension'])
        if num_dims == 1:
            nav, opts, opt_dims = self.get_opts_1d()
        else:
            nav, av_dims = self.get_av_dims()
            if nav == 0:
                opts = [('None (single value)')]
            elif nav == 1:
                attr = av_dims.index(True)
                opts = [(self.var_name + ' against ' +
                        self.ds_select.data['Dimension'][attr] +
                        ' (line plot)')]
                opt_dims = [attr]
            elif nav == 2:
                opts, opt_dims = self.get_opts_2d(num_dims, nav, av_dims)
            elif nav == 3:
                opts, opt_dims = self.get_opts_3d(num_dims, nav, av_dims)
            else:
                opts = [('None (maximum 3 dimensions - please reduce others to singletons)')]
                opt_dims = []

        self.plot_ops.options = opts
        self.plot_ops.value = opts[0]
        self.opt_dims = opt_dims

        if nav > 0:
            self.get_data_btn.disabled = False

        self.stat_box.text = '<font color="green">Plot options found.</font>'

    def get_opts_1d(self):

        '''Get 1d plot options'''

        sel = self.ds_dds.selected['1d']['indices'][0]

        opts = []
        opt_dims = []

        if self.ds_dds.data['Dimensions'][sel][0] > 1:
            opts.append(self.var_name + ' against index (line plot)')
            opt_dims.append([0])
            nav = 1
        else:
            opts.append('None (single value)')
            nav = 0

        return nav, opts, opt_dims

    def get_opts_2d(self, num_dims, nav, av_dims):

        opts = []
        opt_dims = []

        for attr in range(num_dims):
            if av_dims[attr]:
                for dim in range(num_dims):
                    if av_dims[dim] and (dim != attr):
                        opts.append(self.var_name + ' against ' +
                                    self.ds_select.data['Dimension'][attr] + ' and ' +
                                    self.ds_select.data['Dimension'][dim] + ' (colour map)')
                        opt_dims.append([dim, attr])

        return opts, opt_dims

    def get_opts_3d(self, num_dims, nav, av_dims):

        opts = []
        opt_dims = []

        for attr in range(num_dims):
            if av_dims[attr]:
                for dim in range(num_dims):
                    if av_dims[dim] and (dim != attr):
                        for dim2 in range(num_dims):
                            if av_dims[dim2] and (dim2 != dim) and (dim2 != attr):
                                opts.append(self.var_name + ' against ' +
                                            self.ds_select.data['Dimension'][dim] + ' and ' +
                                            self.ds_select.data['Dimension'][dim2] + ' with ' +
                                            self.ds_select.data['Dimension'][attr] + ' as variable ' +
                                            '(colour map with slider)')
                                opt_dims.append([attr, dim2, dim])

        return opts, opt_dims

    def get_av_dims(self):

        ''' Get available (non-singleton) dimensions'''

        num_dims = len(self.ds_select.data['Dimension'])

        av_dims = [False] * num_dims
        nav = 0
        for dim in range(num_dims):
            rmin = self.ds_select.data['First Index'][dim]
            rint = self.ds_select.data['Interval'][dim]
            rmax = self.ds_select.data['Last Index'][dim] + 1
            if rmax > rmin:
                tli = list(range(rmin, rmax, rint))
                if len(tli) > 1:
                    av_dims[dim] = True
                    nav += 1

        return nav, av_dims

    def get_data(self):

        '''Get the variable data'''

        self.stat_box.text = '<font color="blue">Getting data...</font>'

        self.data = {}  # Clear the data dictionary
        self.dim_names = []  # Clear the dimension names list

        if len(self.endian_chkbox.active) > 0:
            byte_ord_str = '>'
        else:
            byte_ord_str = '<'

        ndims = len(self.odh.dds[self.var_name][2])

        if ndims == 1:  # Dimension variable

            dim_vals = numpy.ndarray(shape=(1, 3), dtype=numpy.dtype('int'))
            dim_vals[0, 0] = self.ds_select.data['First Index'][0]
            dim_vals[0, 1] = self.ds_select.data['Interval'][0]
            dim_vals[0, 2] = self.ds_select.data['Last Index'][0]
            self.odh.get_variable(self.var_name, dim_vals, byte_ord_str)
            self.data[self.var_name] = numpy.ndarray(shape=self.odh.variables[self.var_name].shape,
                                                     dtype=numpy.dtype('float32'))
            self.data[self.var_name][:] = self.odh.variables[self.var_name][:]
            self.apply_attributes(self.var_name)  # Apply any attributes
            self.dim_names.append(self.var_name)

        else:  # Data variable

            dim_vals = numpy.ndarray(shape=(ndims, 3),
                                     dtype=numpy.dtype('int'))

            for dim in range(ndims):
                dim_vals[dim, 0] = self.ds_select.data['First Index'][dim]
                dim_vals[dim, 1] = self.ds_select.data['Interval'][dim]
                dim_vals[dim, 2] = self.ds_select.data['Last Index'][dim]

            # Get the variable

            self.odh.get_variable(self.var_name, dim_vals, byte_ord_str)
            self.data[self.var_name] = numpy.ndarray(shape=self.odh.variables[self.var_name].shape,
                                                     dtype=float32)
            self.data[self.var_name][:] = self.odh.variables[self.var_name][:]
            self.apply_attributes(self.var_name)  # Apply any attributes

            # Get the map variables over the ranges required

            dim_data = numpy.ndarray(shape=(1, 3), dtype=numpy.dtype('int'))
            for dim in range(ndims):
                dim_data[:] = dim_vals[dim]
                dim_name = self.odh.dds[self.var_name][2][dim]
                self.odh.get_variable(dim_name, dim_data, byte_ord_str)
                self.data[dim_name] = numpy.ndarray(shape=self.odh.variables[dim_name].shape,
                                                    dtype=float32)
                self.data[dim_name][:] = self.odh.variables[dim_name][:]
                self.apply_attributes(dim_name)  # Apply any attributes
                self.dim_names.append(dim_name)

        ind = self.plot_ops.options.index(self.plot_ops.value)
        self.plot_dims = self.opt_dims[ind]

        if type(self.plot_dims) is int:
            self.plot_dims = [self.plot_dims]

        self.stat_box.text = '<font color="green">Data downloaded.</font>'

        self.display_data()

    def apply_attributes(self, var_name):

        '''Apply the attributes'''

        attr_list = self.odh.das[var_name]

        scale_factor = numpy.nan
        offset = numpy.nan
        fill_value = numpy.nan
        missing_value = numpy.nan
        for attr in attr_list:
            attr_name = attr.split()[1]
            attr_val = attr.split()[2]
            if attr_name in self.attr_names['ScaleFactorName']:
                scale_factor = float(attr_val)
            if attr_name in self.attr_names['OffsetName']:
                offset = float(attr_val)
            if attr_name in self.attr_names['FillValueName']:
                fill_value = float(attr_val)
            if attr_name in self.attr_names['MissingValueName']:
                missing_value = float(attr_val)

        data = self.data[var_name]
        if not numpy.isnan(fill_value):
            data[data == fill_value] = numpy.nan
        if not numpy.isnan(missing_value):
            data[data == missing_value] = numpy.nan
        if not numpy.isnan(scale_factor):
            data *= scale_factor
        if not numpy.isnan(offset):
            data += offset

    def display_data(self):

        '''Display the data'''

        self.stat_box.text = '<font color="blue">Displaying data...</font>'

        if len(self.plot_dims) == 2:
            xname = self.ds_select.data['Dimension'][self.plot_dims[1]]
            yname = self.ds_select.data['Dimension'][self.plot_dims[0]]
        elif len(self.plot_dims) == 3:
            xname = self.ds_select.data['Dimension'][self.plot_dims[2]]
            yname = self.ds_select.data['Dimension'][self.plot_dims[1]]
            zname = self.ds_select.data['Dimension'][self.plot_dims[0]]

        revx = revy = revz = False
        if len(self.revx_chkbox.active) > 0:
            revx = True
        if len(self.revy_chkbox.active) > 0:
            revy = True
        if len(self.revz_chkbox.active) > 0:
            revz = True

        if len(self.plot_dims) > 1:
            x_t, y_t, data_t = self.get_trans_data(xname, yname, revx, revy)

        rmin_v, rmax_v = self.get_cmap_lims()

        cfile = self.col_map_path + '/jet.txt'
        if not os.path.exists(cfile):
            cfile = None
            print('App warning: colourmap file could not be found: reverting to default palette.')

        try:  # Get non-uniformity tolerance if specified
            nu_tol = float(self.interp_tol_box.value)
        except ValueError:
            nu_tol = 0

        if len(self.plot_dims) == 1:

            disp = self.display_line_plot(revx, revy)

        else:

            x_t, y_t, data_t = interp_data(x_t, y_t, data_t,
                                           nu_tol=nu_tol,
                                           stat_box=self.stat_box,
                                           interp_int_box=self.interp_int_box)

            if data_t is not None:

                if len(self.plot_dims) == 3:
                    z_t = self.data[zname]
                else:
                    z_t = numpy.array([0])
                    zname = None

                disp = CMSlicer(x_t, y_t, z_t, data_t, xlab=xname,
                                ylab=yname, zlab=zname, dmlab=self.var_name,
                                cfile=cfile, cmheight=self.main_plot_size[0],
                                cmwidth=self.main_plot_size[1],
                                lpheight=self.line_plot_size[0],
                                lpwidth=self.line_plot_size[1],
                                revz=revz, rmin=rmin_v, rmax=rmax_v,
                                hoverdisp=self.hoverdisp3d)

        if (len(self.plot_dims) == 1) or (data_t is not None):
            self.tabs.tabs[1].child.children[0] = disp
            self.tabs.active = 1
            self.stat_box.text = '<font color="green">Finished.</font>'

    def get_trans_data(self, xname, yname, revx, revy):

        '''Get the transposed data and axes'''

        all_dims = self.data[self.var_name].shape
        t_dims = [0] * len(all_dims)
        pd_count = 0
        for dim in range(len(t_dims)):
            if all_dims[dim] == 1:
                t_dims[dim] = dim
            else:
                t_dims[dim] = self.plot_dims[pd_count]
                pd_count += 1

        data_t = self.data[self.var_name].copy().transpose(t_dims)
        data_t = numpy.squeeze(data_t)

        x_t = self.data[xname].copy()
        y_t = self.data[yname].copy()
        if revx:
            x_t = numpy.flipud(x_t)
        if revy:
            y_t = numpy.flipud(y_t)

        if len(self.plot_dims) == 2:
            if revx:
                data_t = numpy.fliplr(data_t)
            if revy:
                data_t = numpy.flipud(data_t)
        else:
            for dim in range(data_t.shape[0]):
                if revx:
                    data_t[dim] = numpy.fliplr(data_t[dim])
                if revy:
                    data_t[dim] = numpy.flipud(data_t[dim])

        return x_t, y_t, data_t

    def display_line_plot(self, revx, revy):

        '''Display a line plot'''

        disp = Figure(x_axis_label='Index', y_axis_label=self.var_name,
                      plot_height=self.line_plot_size[0],
                      plot_width=self.line_plot_size[0],
                      tools=["reset,pan,resize,wheel_zoom,box_zoom,save"])

        ydata = self.data[self.var_name]
        ydata = numpy.squeeze(ydata)

        disp.line(x=numpy.linspace(0, ydata.size - 1, ydata.size),
                  y=ydata, line_color='blue', line_width=2, line_alpha=1)

        disp.toolbar_location = 'above'

        disp.title.text_font = disp.xaxis.axis_label_text_font = \
            disp.yaxis.axis_label_text_font = 'garamond'
        disp.xaxis.axis_label_text_font_size = \
            disp.yaxis.axis_label_text_font_size = '10pt'
        disp.title.text_font_style = \
            disp.xaxis.axis_label_text_font_style = \
            disp.yaxis.axis_label_text_font_style = 'bold'
        disp.title.text_font_size = '8pt'
        disp.x_range.start = 0
        disp.x_range.end = ydata.size - 1
        disp.y_range.start = ydata[0]
        disp.y_range.end = ydata[-1]
        if revx:
            disp.x_range.start, disp.x_range.end = \
                disp.x_range.end, disp.x_range.start
        if revy:
            disp.y_range.start, disp.y_range.end = \
                disp.y_range.end, disp.y_range.start

        return disp

    def get_cmap_lims(self):

        '''Get the limits for the colourmap'''

        rmin_t, rmax_t = self.zmin.value, self.zmax.value
        rmin_v = rmax_v = None

        try:
            rmin_v = float(rmin_t)
        except ValueError:
            self.zmin.value = ''
        if rmin_v is not None:
            try:
                rmax_v = float(rmax_t)
            except ValueError:
                self.zmax.value = ''
            if rmax_v is not None:
                if rmax_v == rmin_v:
                    rmax_v += 0.1
                if rmax_v < rmin_v:
                    rmin_v, rmax_v = rmax_v, rmin_v

        return rmin_v, rmax_v


curdoc().add_root(App().gui)
curdoc().title = 'bokodapviewer'
