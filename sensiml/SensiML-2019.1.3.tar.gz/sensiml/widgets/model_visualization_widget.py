##################################################################################
#  SENSIML CONFIDENTIAL                                                          #
#                                                                                #
#  Copyright (c) 2017-18  SensiML Corporation.                                   #
#                                                                                #
#  The source code contained or  described  herein and all documents related     #
#  to the  source  code ("Material")  are  owned by SensiML Corporation or its   #
#  suppliers or licensors. Title to the Material remains with SensiML Corpora-   #
#  tion  or  its  suppliers  and  licensors. The Material may contain trade      #
#  secrets and proprietary and confidential information of SensiML Corporation   #
#  and its suppliers and licensors, and is protected by worldwide copyright      #
#  and trade secret laws and treaty provisions. No part of the Material may      #
#  be used,  copied,  reproduced,  modified,  published,  uploaded,  posted,     #
#  transmitted, distributed,  or disclosed in any way without SensiML's prior    #
#  express written permission.                                                   #
#                                                                                #
#  No license under any patent, copyright,trade secret or other intellectual     #
#  property  right  is  granted  to  or  conferred upon you by disclosure or     #
#  delivery of the Materials, either expressly, by implication,  inducement,     #
#  estoppel or otherwise.Any license under such intellectual property rights     #
#  must be express and approved by SensiML in writing.                           #
#                                                                                #
#  Unless otherwise agreed by SensiML in writing, you may not remove or alter    #
#  this notice or any other notice embedded in Materials by SensiML or SensiML's #
#  suppliers or licensors in any way.                                            #
#                                                                                #
##################################################################################


from ipywidgets import HBox, VBox, Dropdown, Button, Image, Layout, Accordion
import numpy as np
from pandas import DataFrame
from bqplot.marks import Scatter, Bars, Lines
from bqplot.scales import LinearScale, OrdinalScale
from bqplot.figure import Figure
from bqplot import Tooltip
from bqplot.axes import Axis
import time
import numpy as np
import threading
import os
from collections import OrderedDict
from qgrid import show_grid
import shutil
import os
import json
from pandas import DataFrame, concat
import copy
from six import text_type



class ModelVisualizationWidget():
    """
    model (knowledpack): a data frame of feature vectors along with a label column and other metadata
    logpath (str): Path to log file for streaming data to widget
    logtype (str): "classifier" or
    bins (int): the number of bins in the histograms
    label_column (str): the name of the column in the features dataframe that refers to the label infomration
    group_columns (list): if you want other metadata in the tooltip, these columns will be added
    f_lim (dict): this sets the limits for max and min of the plots to a constant
        {'max':10, 'min':10}. otherwise defaults to the values of the current features
        which can be missleading.
    colors (list): list of colors to use. Internally has a list of 10. If the labels
        are longer you will need to pass your own

    """

    def __init__(self, model, logpath='', logtype='classifier', feature_vectors=None, bins=25, label_column=None, group_columns=None, f_lim={'max':255,'min':0}, colors=None, max_vectors=1000):


        if model:
            if hasattr(model, "knowledgepack"):
                model = model.knowledgepack

        self._max_vectors = max_vectors
        self._label_column = label_column
        self._group_columns = group_columns
        if self._label_column is None:
            if hasattr(model, 'query_summary') and model.query_summary:
                self._label_column = model.query_summary['label_column']
            elif hasattr(model, 'pipeline_summary') and model.pipeline_summary:
                self._label_column = model.pipeline_summary[0]['label_column']
            else:
                print("Please specify the label column name")
                return

        if self._group_columns is None:
            self._group_columns = ['Subject']


        self._feature_list = [x['Feature'] for x in model.feature_summary]
        self._neurons = model.neuron_array
        self._features = DataFrame(columns=[self._label_column]+self._group_columns+self._feature_list)
        if feature_vectors is not None:
            if 'Subject' not in feature_vectors.columns:
                feature_vectors['Subject'] = 1
            self._features = copy.deepcopy(feature_vectors[self._features.columns])
            self._features[self._label_column] = feature_vectors[self._label_column].astype(str)

        self._class_map = OrderedDict({'Unknown':0})

        increment=1
        if '0' in model.class_map:
            increment=0
        for i in range(1, len(model.class_map)+increment):
            self._class_map[str(model.class_map[str(i)])] = i

        self._reverse_class_map = {int(k):str(v) for k,v in model.class_map.items()}
        self._reverse_class_map[0] = 'Unknown'


        if hasattr(model, 'device_configuration'):
            self._norm = model.device_configuration['distance_mode']
        else:
            self._norm = model.configuration['distance_mode']


        self._logpath = logpath
        self._logtype = logtype
        self._log_reader = None
        if self._logpath and logtype.lower() not in ['classifier']:
            print("Invalid logtype, set to either classifer")
            return


        self._colors = colors
        self._f_lim = f_lim

        self._bins = bins
        self._counter = 0
        self._hists_y = []
        self._hists_x = []
        self._scatters = []
        self._neuron_scatters = []

        legend_x = []
        legend_y = []
        legend_colors = []

        dist = text_type("480px")
        third_dist = text_type("160px")
        box_color = 'black'

        if self._colors is None:
            self._colors = ["#16a085","#8e44ad","#d35400","#2c3e50",
                      "#2980b9","#c0392b", "#27ae60", "#6E2C00",
                      "#1A5276", "#17202A"]


        self._feature_x = Dropdown(description='Feature 1')
        self._feature_y = Dropdown(description='Feature 2')

        self._feature_x.options = [x for x in self._feature_list]
        self._feature_y.options = [x for x in self._feature_list]

        self._feature_map = {x:index for index,x in enumerate(self._feature_x.options)}

        feature1 = self._feature_x.options[0]
        feature2 = self._feature_y.options[0]

        if self._f_lim:
            sc_x = LinearScale(min=f_lim['min'], max=f_lim['max'])
            sc_y = LinearScale(min=f_lim['min'], max=f_lim['max'])
        else:
            sc_x = LinearScale()
            sc_y = LinearScale()

        hist_scale_y = LinearScale(min=0)
        hist_scale_x = LinearScale(min=0)
        x_ord_legend = OrdinalScale()
        y_lin_legend = LinearScale()

        feature_tt = Tooltip(fields=['name'], labels=[', '.join(['index', self._label_column]+self._group_columns)])
        neuron_tt = Tooltip(fields=['name'], labels=['Neuron:Category:AIF'])

        self._h_bins = self._get_h_bins()

        self._neuron_df, neuron_names = self._make_neuron_center()
        neuron_groups = self._neuron_df.groupby([self._label_column])


        for label, index in self._class_map.items():
            if label not in neuron_groups.groups.keys():
                group = (label, DataFrame(columns=self._neuron_df.columns))
                legend_y.append(0)
            else:
                group = (label, neuron_groups.get_group(label))
                legend_y.append(group[1][self._feature_list[0]].count())

            legend_x.append(label)

            # create a scatter plot for each group
            self._neuron_scatters.append(Scatter(x=group[1][feature1].values,
                                    y=group[1][feature1].values,
                                    names=neuron_names[index],
                                    display_names=False,
                                    default_opacities=[0.5],
                                    default_size=30,
                                    scales={'x': sc_x, 'y': sc_y},
                                    colors=[self._colors[index]],
                                    tooltip=neuron_tt,
                                    marker='square'
                                    ))

            # create a scatter plot for each group
            self._scatters.append(Scatter(x=[],
                                    y=[],
                                    names=[],
                                    display_names=False,
                                    default_opacities=[0.5],
                                    default_size=30,
                                    scales={'x': sc_x, 'y': sc_y},
                                    colors=[self._colors[index]],
                                    tooltip=feature_tt,
                                    ))

            # create a histograms using a bar chart for each group
            # histogram plot for bqplot does not have enough options (no setting range, no setting orientation)
            #h_y, h_x = np.histogram(values, bins=h_bins_x)
            self._hists_x.append(Bars(x=[],
                                y=[],
                                opacities=[0.3]*bins,
                                scales={'x': sc_x, 'y': hist_scale_x},
                                colors=[self._colors[index]],
                                orientation='vertical'))

            self._hists_y.append(Bars(x=[],
                                y=[],
                                opacities=[0.3]*bins,
                                scales={'x': sc_x, 'y': hist_scale_y},
                                colors=[self._colors[index]],
                                orientation='horizontal'))

        self._neuron_patches = self._init_neurons(feature1, feature2, {"x":sc_x, "y":sc_y})


        # legend will show the names of the labels as well as a total count of each
        self._legend_bar = Bars(x=legend_x,
                   y=[1]*len(self._class_map.keys()),
                   colors=self._colors,
                   opacities=[0.3]*6,
                   scales={'x': x_ord_legend, 'y':y_lin_legend},
                   orientation='horizontal')

        ax_x_legend = Axis(scale=x_ord_legend,
                    tick_style={'font-size':16},
                    label='',
                    orientation='vertical',
                          )
                    #tick_values=features.groupby(self._label_column).count()[self._feature_list[0]].index)

        ax_y_legend = Axis(scale=y_lin_legend,
                           orientation='horizontal',
                           color='white',
                           num_ticks=0)

        #these are blank blank axis that are used to fill in the boarder for the top and right of the figures
        ax_top = Axis(scale=sc_x, color=box_color, side='top', tick_style={'font-size':0})
        ax_right = Axis(scale=sc_x, color=box_color, side='right', tick_style={'font-size':0})
        ax_left = Axis(scale=sc_x, color=box_color,  side='left', tick_style={'font-size':0})
        ax_bottom = Axis(scale=sc_x, color=box_color, side='bottom', tick_style={'font-size':0})

        #scatter plot axis
        self._ax_x = Axis(label=feature1, scale=sc_x, color=box_color)
        self._ax_y = Axis(label=feature2, scale=sc_y, orientation='vertical', color=box_color)

        #count column of histogram
        ax_count_vert  = Axis(label='', scale=hist_scale_y, orientation='vertical', color=box_color, num_ticks=3)
        ax_count_horiz = Axis(label='', scale=hist_scale_x, orientation='horizontal', color=box_color, num_ticks=3)

        #histogram bin axis
        ax_hist_x = Axis(label='', scale=sc_x, orientation='vertical', color=box_color)
        ax_hist_y = Axis(label='', scale=sc_x, orientation='horizontal', color=box_color)

        #create figures for each plot
        f_scatter = Figure(axes=[self._ax_x, self._ax_y, ax_top, ax_right],
                           background_style={'fill':'white'}, #css is inserted directly
                           marks=self._neuron_patches+self._neuron_scatters+self._scatters,
                           min_aspect_ratio=1,
                           max_aspect_ratio=1,
                           fig_margin =  {"top":0, "bottom":60, "left":60, "right":0},
                           )

        f_hists_y = Figure(axes=[ax_left, ax_count_horiz, ax_top, ax_right],
                           background_style={'fill':'white'},
                           marks=self._hists_y,
                           min_aspect_ratio=.33,
                           max_aspect_ratio=.33,
                           fig_margin =  {"top":0, "bottom":60, "left":10, "right":0},
                          )

        f_hists_x = Figure(axes=[ax_count_vert, ax_top, ax_right],
                           background_style={'fill':'white'},
                           marks=self._hists_x,
                           min_aspect_ratio=3,
                           max_aspect_ratio=3,
                           fig_margin =  {"top":20, "bottom":10, "left":60, "right":0},
                          )

        f_legend = Figure(marks=[self._legend_bar], axes=[ax_x_legend, ax_y_legend], title='',
                                     legend_location ='bottom-right',
                                     background_style = {'fill':'white'},
                                     min_aspect_ratio=1,
                                     max_aspect_ratio=1,
                                     fig_margin =  {"top":20, "bottom":30, "left":80, "right":20})

        self._class_button = Button()
        self._collect_button = Button(description='Stream')
        self._update_button = Button(description='Update Features')
        self._import_button = Button(description="Import Log")
        self._clear_button = Button(description='Clear Features')

        dir_path = os.path.dirname(os.path.realpath(__file__))

        if os.path.exists(os.path.join(dir_path,'..','image',"sensiml.png")):
            file = open(os.path.join(dir_path,'..','image',"sensiml.png"), "rb")
            image = file.read()
            sensiml_logo = Image(
                value=image,
                format='png',
                width=300,
                height=400,
            )
        else:
            sensiml_logo=Image(width=300,height=400)

        self._grid = show_grid(self._features, grid_options={'maxVisibleRows':10, 'minVisibleRows':5})
        # we already set the ratios, but it is necessary to set the size explicitly anyway
        # this is kind of cool, inserts this into the style in html
        f_legend.layout.height = third_dist
        f_legend.layout.width = third_dist
        f_hists_x.layout.height = third_dist
        f_hists_x.layout.width = dist
        f_hists_y.layout.height = dist
        f_hists_y.layout.width = third_dist
        f_scatter.layout.height = dist
        f_scatter.layout.width = dist
        self._class_button.layout.width=text_type("300px")
        self._class_button.layout.height=text_type("200px")
        self._collect_button.style.button_color = 'lightgreen'


        self._collect_button.on_click(self._stream_log)
        self._import_button.on_click(self._read_log)
        self._update_button.on_click(self._update_from_grid)
        self._clear_button.on_click(self._clear_features)

        accordion= Accordion(children=[self._grid])
        accordion.set_title(0, 'Feature Vectors')
        accordion.selected_index = None

        # when the user selects a different feature, switch the data plotted
        self._feature_x.observe(self._change_x_feature, 'value')
        self._feature_y.observe(self._change_y_feature, 'value')


        #display the widgets'
        self._widget = VBox([
                    HBox([
                        VBox([sensiml_logo,
                              Button(layout=Layout(visibility='hidden')),
                              self._class_button,
                               Button(layout=Layout(visibility='hidden')),
                               HBox([self._collect_button, self._import_button]),
                               HBox([self._update_button, self._clear_button]),
                              Button(layout=Layout(visibility='hidden')),
                               self._feature_x,
                               self._feature_y,
                              ]),
                        VBox([
                           HBox([f_hists_x, f_legend]),
                          HBox([f_scatter, f_hists_y])
                            ]),

                        ]),

                    accordion],
                        layout = Layout(border='outset',
                width='100%'))

        display(self._widget)

    # we create some functions that allow changes when the widgets notice an event
    def _change_x_feature(self, b):
        feature_groups = self._features.groupby([self._label_column])
        for label, index in self._class_map.items():
            if label not in feature_groups.groups.keys():
                continue
            group = feature_groups.get_group(label)
            self._scatters[index].y = group[self._feature_y.value]
            self._scatters[index].x = group[self._feature_x.value]
            h_y, h_x = np.histogram(group[self._feature_x.value].values, bins=self._h_bins)
            self._hists_x[index].y = h_y
            self._hists_x[index].x = h_x+self._hist_shift

        self._update_neurons(self._feature_x.value, self._feature_y.value)

        self._ax_x.label = self._feature_x.value

    def _change_y_feature(self, b):
        feature_groups = self._features.groupby([self._label_column])
        for label, index in self._class_map.items():
            if label not in feature_groups.groups.keys():
                continue
            group = feature_groups.get_group(label)
            self._scatters[index].y = group[self._feature_y.value]
            self._scatters[index].x = group[self._feature_x.value]
            h_y, h_x = np.histogram(group[self._feature_y.value].values, bins=self._h_bins)
            self._hists_y[index].y = h_y
            self._hists_y[index].x = h_x+self._hist_shift


        self._update_neurons(self._feature_x.value, self._feature_y.value)

        self._ax_y.label = self._feature_y.value

    def _stream_log(self, b):
        if self._logpath:
            if self._collect_button.description == 'Stream':
                self._collect_button.description = 'Streaming..'
                self._collect_button.style.button_color = 'red'
                thread = threading.Thread(target=self._stream_logfile)
                thread.start()
            else:
                self._collect_button.description = 'Stream'
                self._collect_button.style.button_color = 'lightgreen'
                self._grid.df = self._features

    def _read_log(self, b):
        if self._logpath:
            if self._collect_button.description == 'Streaming..':
                pass
            else:
                self._clear_features(None)
                time.sleep(3)
                log_reader = get_next_class_classifier_read(self._logpath)
                self._read_logfile(log_reader)
                self._grid.df = self._features


    def _update_from_grid(self, b):
        if self._collect_button.description == 'Stream':
            self._features = self._grid.get_changed_df()[[self._label_column]+self._group_columns+self._feature_list]
            self._change_y_feature(None)
            self._change_x_feature(None)

    def _clear_features(self, b):
        if self._collect_button.description == 'Stream':
            for index in range(len(self._scatters)):
                self._scatters[index].y = []
                self._scatters[index].x = []
                self._hists_y[index].y = []
                self._hists_y[index].x = []
            self._features = self._grid.df[0:0]
            self._grid.df = self._grid.df[0:0]


    def _stream_logfile(self):
        self._reset_logger()
        while self._collect_button.description == 'Streaming..':
            result = next(self._log_reader)
            if result:
                data = {self._label_column: result[0],
                    'Subject': 'Test',
                    }
                data.update({self._feature_list[index]: result[1][index] for index in range(len(result[1]))})
                try:
                    self._add_data(DataFrame([data]))
                except:
                    pass
            else:
                time.sleep(3)

        self._log_reader.close()

    def _read_logfile(self, log_reader):
        result = True
        count=0
        M = []
        for result in log_reader:
            if result:
                count+=1
                data = {self._label_column: result[0],
                    'Subject': 'Test',
                    }
                data.update({self._feature_list[index]: result[1][index] for index in range(len(result[1]))})
                M.append(data)

        self._add_datapoints(DataFrame(M))
        self._change_x_feature(None)


    def _add_datapoints(self, datapoints):
        categories = datapoints[self._label_column].values
        labels = map(lambda x: self._reverse_class_map[x], categories)
        datapoints[self._label_column] = labels
        self._features = concat([self._features, datapoints]).reset_index(drop=True)[[self._label_column]+self._group_columns+self._feature_list]
        datapoints_groups = datapoints.groupby(self._label_column)

        for label in datapoints_groups.groups.keys():
            cat = self._class_map[label]
            x = datapoints_groups.get_group(label)[self._feature_x.value].iloc[0]
            y = datapoints_groups.get_group(label)[self._feature_y.value].iloc[0]
            names = self._get_names(datapoints_groups.get_group(label))
            self._scatters[cat].x = np.hstack([self._scatters[cat].x, x])
            self._scatters[cat].y = np.hstack([self._scatters[cat].y, y])
            self._scatters[cat].names = np.hstack([self._scatters[cat].names, names])

        feature_group = self._features.groupby([self._label_column])
        for label in feature_group.groups.keys():
            cat = self._class_map[label]
            h_y, h_x = np.histogram(feature_group.get_group(label)[self._feature_y.value].values, bins=self._h_bins)
            self._hists_y[cat].y = h_y
            self._hists_y[cat].x = h_x+self._hist_shift
            h_y, h_x = np.histogram(feature_group.get_group(label)[self._feature_x.value].values, bins=self._h_bins)
            self._hists_x[cat].y = h_y
            self._hists_x[cat].x = h_x+self._hist_shift

    def _add_data(self, datapoint):
        cat = datapoint[self._label_column].iloc[0]
        label = self._reverse_class_map[cat]
        datapoint[self._label_column] = label
        self._features = concat([self._features, datapoint]).reset_index(drop=True)[[self._label_column]+self._group_columns+self._feature_list]
        x = datapoint[self._feature_x.value].iloc[0]
        y = datapoint[self._feature_y.value].iloc[0]
        name = self._get_name(datapoint)
        self._scatters[cat].x = np.hstack([self._scatters[cat].x, x])
        self._scatters[cat].y = np.hstack([self._scatters[cat].y, y])
        self._scatters[cat].names = np.hstack([self._scatters[cat].names, name])
        self._class_button.description = str(self._reverse_class_map[cat])
        self._class_button.style.button_color = 'white'
        self._class_button.style.button_color = self._colors[cat]
        feature_group = self._features.groupby([self._label_column])
        h_y, h_x = np.histogram(feature_group.get_group(label)[self._feature_y.value].values, bins=self._h_bins)
        self._hists_y[cat].y = h_y
        self._hists_y[cat].x = h_x+self._hist_shift
        h_y, h_x = np.histogram(feature_group.get_group(label)[self._feature_x.value].values, bins=self._h_bins)
        self._hists_x[cat].y = h_y
        self._hists_x[cat].x = h_x+self._hist_shift
        #self._legend_bar.y[cat]+=1

    def _get_name(self, f):
        self._counter += 1
        return '{},'.format(self._counter)+','.join([str(x) for x in f[[self._label_column]+self._group_columns].iloc[0].values])

    def _get_names(self, f):
        M = []
        for i in range(len(f)):
            self._counter+=1
            M.append('{},'.format(self._counter)+','.join([str(x) for x in f[[self._label_column]+self._group_columns].iloc[i].values]))
        return M


    def _init_neurons(self, feature_x, feature_y, scale):
        neuron_patches = []
        for neuron in self._neurons:
            x = neuron['Vector'][self._feature_map[feature_x]]
            y = neuron['Vector'][self._feature_map[feature_y]]
            aif   = neuron['AIF']

            if neuron['Category'] < 30000: # if it is not degenerated neuron
                clr = self._colors[neuron['Category']]
                if self._norm == 0:
                    dim = len(neuron['Vector'])
                    aif = 2*aif/dim
                    neuron_patches.append(Lines( x=[x,x+aif,x,x-aif],
                                                y=[y-aif,y,y+aif,y],
                                                opacities=[.2],
                                                fill='inside',
                                                colors=[clr],
                                                scales=scale))
                else:
                    aif=aif/2
                    neuron_patches.append(Lines(x=[x-aif,x+aif,x+aif,x-aif],
                                                y=[y-aif,y-aif,y+aif,y+aif],
                                                opacities=[.2],
                                                fill='inside',
                                                colors=[clr],
                                                scales=scale))

        return neuron_patches

    def _update_neurons(self, feature_x, feature_y):
        for index, neuron in enumerate(self._neurons):
            x = neuron['Vector'][self._feature_map[feature_x]]
            y = neuron['Vector'][self._feature_map[feature_y]]
            aif = neuron['AIF']

            if neuron['Category'] < 30000: # if it is not degenerated neuron
                if self._norm == 0:
                    dim = len(neuron['Vector'])
                    aif = 2*aif/dim
                    self._neuron_patches[index].x = [x,x+aif,x,x-aif]
                    self._neuron_patches[index].y =[y-aif,y,y+aif,y]
                else:
                    aif=aif/2
                    self._neuron_patches[index].x=[x-aif,x+aif,x+aif,x-aif]
                    self._neuron_patches[index].y=[y-aif,y-aif,y+aif,y+aif]

        neuron_groups = self._neuron_df.groupby([self._label_column])

        for label, index in self._class_map.items():
            if label in neuron_groups.groups.keys():
                self._neuron_scatters[index].y = neuron_groups.get_group(label)[feature_y].values
                self._neuron_scatters[index].x = neuron_groups.get_group(label)[feature_x].values

    # simple function to return the bins for the plot
    def _get_h_bins(self):
        self._hist_shift = 0
        if self._f_lim:
            delta = (self._f_lim['max']-self._f_lim['min'])/float(self._bins)
            self._hist_shift = delta/2
            return np.arange(self._f_lim['min'], self._f_lim['max']+delta,delta)

    def _make_neuron_center(self):
        neuron_centers = []
        names = [[] for i in range(len(self._class_map.keys()))]
        for index, neuron in enumerate(self._neurons):
            neuron_center = {self._feature_list[i]:neuron['Vector'][i] for i in range(len(self._feature_list))}
            neuron_center[self._label_column] = self._reverse_class_map[neuron['Category']]
            neuron_centers.append(neuron_center)
            names[neuron['Category']].append('{0}:{1}:{2}'.format(neuron['Identifier'],neuron['Category'],neuron['AIF']))

        return DataFrame(neuron_centers), names

    def _reset_logger(self):
        if self._log_reader:
            self._log_reader.close()
        if self._logpath:
            if self._logpath and self._logtype.lower()=='classifier':
                self._log_reader = get_next_class_classifier_stream(self._logpath)


def get_next_class_classifier_stream(filepath):
    feature_vector=[]

    if os.path.exists('.features.log'):
        os.remove('.features.log')
    shutil.copyfile(filepath, '.features.log')
    with open('.features.log', 'r') as fid:
        fid.readlines()
        while 1:
            where = fid.tell()
            line = fid.readline()
            if not line:
                yield
                shutil.copyfile(filepath, '.features.log')
                fid.seek(where)
            else:
                if "FeatureVector" in line:
                    try:
                        classification = json.loads(line)
                        yield([classification['Classification'], classification['FeatureVector']])
                    except:
                        pass


def get_next_class_classifier_read(filepath):
    feature_vector=[]

    if os.path.exists('.features.log'):
        os.remove('.features.log')
    shutil.copyfile(filepath, '.features.log')
    with open('.features.log', 'r') as fid:
        for line in fid.readlines():
            if not line.rstrip():
                continue
            if "FeatureVector" in line:
                try:
                    classification = json.loads(line)
                    yield([classification['Classification'], classification['FeatureVector']])
                except:
                    pass