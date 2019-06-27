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

from ipywidgets import widgets
from ipywidgets import Layout, Button, HBox, VBox, Accordion, FloatText, Textarea, Dropdown, Label, IntSlider, Checkbox, Text, Button, SelectMultiple, Password
from IPython.display import display
from ipywidgets import IntText
from json import dumps as jdump
from sensiml.widgets.base_widget import BaseWidget
from IPython.display import clear_output
from sensiml.widgets import QueryWidget, AutoSenseWidget, DownloadWidget, FlashWidget, ModelExploreWidget
from IPython.core.display import HTML
try:
    get_ipython().__class__.__name__
    display(HTML("<style>.container { width:90% !important; }</style>"))
except:
    pass
layout = Layout(border='outset',
                width='100%')


class DashBoard(BaseWidget):

    def __init__(self, dsk=None, server='https://sensiml.cloud/', knowledgepack_level='pipeline', **kwargs):
        self._server = server
        self._kwargs = kwargs
        self._dsk = dsk

        if self._dsk:
            self._dsk._auto_sense_ran = False
            self._dsk._query_created = False

        self._create_widget(knowledgepack_level=knowledgepack_level)

    def _set_project(self, option):

        if not isinstance(option['new'], dict):
            return
        if option['new'].get('index', None) is None:
            return

        project_name = option['owner'].options[option['new']['index']]

        if not project_name:
            return

        self._dsk.project = project_name

        pipelines = self._dsk.list_sandboxes()
        if pipelines is not None:
            pipelines = [
                '']+sorted(list(pipelines.Name.values), key=lambda s: s.lower())
        else:
            pipelines = []

        self._widget_pipeline.options = pipelines
        self._widget_pipeline.observe(self._set_pipeline)
        self._refresh_project()

    def _set_pipeline(self, option):

        if not isinstance(option['new'], dict):
            return
        if option['new'].get('index', None) is None:
            return
        if not option['new'].get('index', None):
            return

        pipeline_name = option['owner'].options[option['new']['index']]
        self._dsk.pipeline = pipeline_name

        self._refresh_pipelines()

    def _logout(self, b):
        if self._dsk:
            self._dsk.logout()
            self._dsk = None
            self._clear_cell_output(None)

            self._widget_project.options = []
            self._widget_pipeline.options = []
            self._auto._clear()
            self._download._clear()
            self._explore._clear()
            self._button_connected.description = ''
            self._button_connected.icon = ''
            self._button_connected.style.button_color = '#00b300'
            self._button_connected.disabled = True

    def _clear_cell_output(self, b, return_display=True):
        clear_output(wait=True)

        if return_display:
            return display(self.v)

    def _on_button_clicked(self, b):
        from sensiml import SensiML

        if self._dsk is None:
            try:
                self._dsk = SensiML(server=self._server)

                self._dsk._auto_sense_ran = False
                self._dsk._query_created = False
            except:
                print("Login Failed.")
                return

        self._clear_cell_output(None, return_display=False)

        self._button_connected.description = 'Connected'
        self._button_connected.icon = 'link'
        self._button_connected.style.button_color = '#0075c1'

        self._widget_project.options = [
            '']+sorted(list(self._dsk.list_projects().Name.values), key=lambda s: s.lower())
        self._widget_project.observe(self._set_project)
        self._refresh_login()

    def _add_pipeline(self, b):

        if self._dsk is None:
            print("You must login first.")
            return
        if self._dsk.project is None:
            print("Project Must be set first.")
            return

        if not self._widget_new_pipeline.value:
            return None

        if self._widget_new_pipeline.value not in self._widget_pipeline.options:
            self._dsk.pipeline = self._widget_new_pipeline.value

        self._widget_pipeline.options = self._widget_pipeline.options + \
            (self._widget_new_pipeline.value,)
        self._widget_pipeline.value = self._widget_new_pipeline.value

        self._refresh_pipelines()

    def _create_widget(self, knowledgepack_level='Project'):

        self._button_connected = Button(description="Connected")
        self._button_loggout = Button(description="Logout")
        self._button_clear = Button(
            description="Clear Log", tooltip='Clear Log Text Below Dashboard')
        self._widget_project = Dropdown(description="Project", options=[])
        self._widget_pipeline = Dropdown(description="Pipeline", options=[])
        self._widget_new_pipeline = Text(description="New Pipeline", value='')
        self._button_add_pipeline = Button(description="Add", icon='plus')

        self._button_connected.on_click(self._on_button_clicked)
        self._button_clear.on_click(self._clear_cell_output)
        self._button_add_pipeline.on_click(self._add_pipeline)
        self._button_loggout.on_click(self._logout)

        login = VBox([
            HBox([VBox([self._button_connected,
                        self._button_loggout]),
                  VBox([self._widget_project,
                        self._widget_pipeline]),
                  VBox([HBox([self._widget_new_pipeline, self._button_add_pipeline]),
                        ])
                  ])], layout=layout)

        bottom = VBox([self._button_clear], layout=layout)

        self._query = QueryWidget(None)
        self._auto = AutoSenseWidget(None)
        self._download = DownloadWidget(None, level=knowledgepack_level)
        self._flash = FlashWidget(None)
        self._explore = ModelExploreWidget(None, level=knowledgepack_level)

        accordions = [Accordion(children=[self._query.create_widget()]),
                      Accordion(children=[self._auto.create_widget()]),
                      Accordion(children=[self._explore.create_widget()]),
                      Accordion(children=[self._download.create_widget()]),
                      Accordion(children=[self._flash.create_widget()])

                      ]
        accordions[0].set_title(0, 'Data Exploration')
        accordions[1].set_title(0, 'Model Building')
        accordions[2].set_title(0, 'Explore Models')
        accordions[3].set_title(0, 'Create Knowledge Pack')
        accordions[4].set_title(0, 'Deploy Knowledge Pack')

        for a in accordions:
            a.selected_index = None
        self.v = VBox([login] + accordions + [bottom])
        self.v.layout.border = "outset"

        self._on_button_clicked(None)

        if self._dsk:
            display(self.v)

    def _refresh_login(self):
        self._flash._dsk = self._dsk
        self._flash._refresh()

    def _refresh_project(self):
        self._query._dsk = self._dsk
        self._query._refresh()
        self._auto._clear()
        self._download._clear()
        self._explore._clear()

    def _refresh_pipelines(self):
        self._auto._dsk = self._dsk
        self._auto._refresh()
        self._download._dsk = self._dsk
        self._download._refresh()
        self._explore._dsk = self._dsk
        self._explore._refresh()
