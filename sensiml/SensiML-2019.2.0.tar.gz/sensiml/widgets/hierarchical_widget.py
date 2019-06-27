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


import os
import IPython
from ipywidgets import widgets
from ipywidgets import Layout, Button, Box, FloatText, Textarea, Dropdown, Label, IntSlider, Checkbox, Text, Button, SelectMultiple
from IPython.display import display
from ipywidgets import IntText
from json import dumps as jdump
from sensiml.widgets.base_widget import BaseWidget

title_item_layout = Layout(
    display='flex',
    flex_flow='row',
    size=16,
    border='solid 2px',
    justify_content='space-between',
    overflow='visible'
)

label_value_layout = Layout(overflow='visible',
                            min_width='150px',)

category_item_layout = Layout(
    display='flex',
    flex_flow='row',
    size=16,
    border='solid 2px',
    justify_content='center',
    background_color='red',
    overflow='visible'
)

form_item_layout = Layout(
    display='flex',
    flex_flow='row',
    overflow='visible',
    justify_content='space-between'
)


pipeline_layout = Layout(display='flex',
                         flex_flow='column',
                         border='solid 2px',
                         align_items='stretch',
                         width='75%',
                         overflow='visible')

GENERATE_INDEX = 0
PLATFORM_INDEX = 1
DEBUG_INDEX = 2
TEST_DATA_INDEX = 3
APPLICATION_INDEX = 4
SAMPLE_RATE_INDEX = 5
DOWNLOAD_TYPE = 6
TEST_DATA = 7
PARENT_INDEX = 8
SUBMODEL_INDEX = 9


def clean_name(name):
    return ''.join(e if e.isalnum() else '_' for e in name)


class HierarchicalWidget(BaseWidget):
    def __init__(self, dsk=None, level='Project', folder='knowledgepacks'):
        self._dsk = dsk
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.setup(level=level)

    def setup(self, level):
        self.kb_description = {'parent': {},
                               'sub': {'Report': 'Report'}}

        self.kb_dict = {'parent': [],
                        'sub': []}

        self.level = level
        self.platforms = self._dsk.platforms()

    def select_platform(self, platform_name):
        self.platform = self.platforms.iloc[platform_name]
        self.platform_name = self.platform['Software Platform']

        if 'curie' in self.platform['Description'].lower():
            self.target_os_widget.options = ['ISPC']
            self.target_os_widget.value = self.target_os_widget.options[0]
            self.app_output_options_widget.options = ['ble', 'led', 'serial']
        elif 'nordic' in self.platform['Description'].lower():
            self.target_os_widget.options = ['NordicSDK']
            self.target_os_widget.value = self.target_os_widget.options[0]
            self.app_output_options_widget.options = ['ble', 'led', 'serial']
            self.app_output_options_widget.value = ['ble']
        elif 'simulator' in self.platform['Description'].lower():
            self.target_os_widget.options = ['x86']
            self.target_os_widget.value = self.target_os_widget.options[0]
            self.app_output_options_widget.options = ['serial']

    def generate_description(self, b):
        parent_name = None
        parent_uuid = None
        description = {}
        if not self.kb_description['parent']:
            print("No Parent Model Set.")
        for key in self.kb_description['parent']:
            description = {clean_name(key): {
                'uuid': self.kb_description['parent'][key], 'results': {}, 'source': 'motion'}}
            parent_name = clean_name(key)
            parent_uuid = self.kb_description['parent'][key]
        for box in self.kb_dict['parent'][0][1:]:
            description[parent_name]['results'].update(
                {format(box.children[0].description.split('-')[0]): clean_name(box.children[0].value)})
        for key in self.kb_description['sub']:
            if key != 'Report':
                sub_description = {'uuid': self.kb_description['sub'][key],
                                   'parent': parent_name,
                                   'segmenter_from': 'parent'}
                description.update({clean_name(key): sub_description})

        kp_uuid = parent_uuid
        board_name = self._dsk.platforms[self.platform_widget.value].board_name

        kp_platform = self._dsk.platforms[self.platform_widget.value].id
        kp_debug = self.debug_widget.value
        kp_test_data = self.test_data_widget.value
        kp_download_type = self.download_type_widget.value
        sample_rate = self.imu_sample_widget.value
        output_options = self.app_output_options_widget.value

        if kp_platform >= 3 and kp_platform < 99:  # Nordic Thingy and not simulator
            if 'ble' not in output_options:
                output_options.insert('ble')  # always output via ble
            kp_application = 'thingy_pme'
        else:
            if 'led' in output_options:
                kp_application = 'LED'
            else:
                kp_application = 'Default'

        if board_name == 'ARM GCC Generic' or board_name == 'x86 GCC Generic':
            kp_application = 'testdata_runner'

        if kp_uuid is not None:
            kp = self._dsk.get_knowledgepack(kp_uuid)
        else:
            #print('Invalid KnowledgePack name.')
            return None

        config = {'target_platform': kp_platform,
                  'test_data': kp_test_data,
                  'debug': kp_debug,
                  'application': kp_application,
                  'sample_rate': sample_rate,
                  'output_options': output_options,
                  'kb_description': description}

        # print(config)

        if kp_download_type == 'Library':
            kp.download_library(config=config, folder='knowledgepacks')
        if kp_download_type == 'Binary':
            kp.download_binary(config=config, folder='knowledgepacks')

    def set_parent_model(self, b):
        index = int(b.icon)

        kp = self._dsk.get_knowledgepack(
            self.kb_items[PARENT_INDEX].children[1].value)
        kp_item = []
        kp_item.append(Box([Label(value=kp.name),
                            Button(description='delete'),
                            ], layout=title_item_layout))

        for key, value in kp.class_map.items():
            kp_item.append(Box([Dropdown(options=self.kb_description['sub'],
                                         description='{} - {}'.format(key, value))],
                               layout=form_item_layout))

        self.kb_description['parent'] = {kp.name: kp.uuid}
        self.kb_dict['parent'] = [kp_item]
        self.generate_pipeline()

    def add_submodel(self, b):
        index = int(b.icon)
        kp = self._dsk.get_knowledgepack(
            self.kb_items[SUBMODEL_INDEX].children[1].value)
        kp_item = []
        if self.kb_description['sub'].get(kp.name, None) is not None:
            return

        if self.kb_description['parent'].get(kp.name, None) is not None:
            return

        kp_item.append(Box([Label(value=kp.name),
                            Button(description='delete'),
                            ], layout=title_item_layout))

        self.kb_description['sub'].update({kp.name: kp.uuid})
        self.kb_dict['sub'].append(kp_item)
        self.generate_pipeline()

    def get_kp_dict(self):
        if self.level.lower() == 'project':
            return {name: value for name, value in self._dsk.project.list_knowledgepacks()[['Name', 'kp_uuid']].values if name}
        elif self.level.lower() == 'pipeline':
            return {name: value for name, value in self._dsk.pipeline.list_knowledgepacks()[['Name', 'kp_uuid']].values if name}

        return {name: value for name, value in self._dsk.list_knowledgepacks()[['Name', 'kp_uuid']].values if name}

    @staticmethod
    def flatten(l):
        return [item for sublist in l for item in sublist]

    def get_model_list(self):
        return [Box([Label(value='Parent Model')], layout=category_item_layout)] + self.flatten(self.kb_dict['parent']) + \
            [Box([Label(value='Sub Model')], layout=category_item_layout)
             ] + self.flatten(self.kb_dict['sub'])

    def get_feature_file_list(self):
        ff = self._dsk.list_featurefiles(silent=True)
        if ff is not None:
            return list(ff['Name'].values)
        else:
            return []

    def get_platform_names(self):
        pf = {}
        for i in range(len(self.platforms)):
            pf['{} {}'.format(self.platforms.iloc[i]['Board'],
                              self.platforms.iloc[i]['Platform Version'])] = i

        return pf

    def update(self):

        self.test_data_widget.options = [None] + self.get_feature_file_list()

        self.kb_items[PARENT_INDEX].children[1].options = self.get_kp_dict()
        self.kb_items[SUBMODEL_INDEX].children[1].options = self.get_kp_dict()

        if self.kb_dict['parent']:
            for child in self.kb_dict['parent'][0][1:]:
                child.children[0].options = [
                    k for k, v in self.kb_description['sub'].items()]

    def create_widget(self):

        self.platform_widget = Dropdown(options=self.get_platform_names())
        self.target_os_widget = Dropdown()
        self.app_output_options_widget = SelectMultiple(
            options=['ble', 'led', 'serial'])
        self.download_type_widget = Dropdown(options=['Library', 'Binary'])
        self.imu_sample_widget = Dropdown(options=[100, 50, 25])
        self.debug_widget = Dropdown(options=[True, False])
        self.test_data_widget = Dropdown(options=[None])

        self.kb_items = [
            Box([Label(value='Model Builder'),
                 Button(icon='0', description="Generate Knowledgepack")], layout=form_item_layout),
            Box([Label(value='Select Hardware Platform', layout=label_value_layout), widgets.interactive(
                self.select_platform, platform_name=self.platform_widget)],  layout=form_item_layout),
            Box([Label(value='Select Target OS', layout=label_value_layout),
                 self.target_os_widget], layout=form_item_layout),
            Box([Label(value='Select Output', layout=label_value_layout),
                 self.app_output_options_widget], layout=form_item_layout),
            Box([Label(value='Download Type', layout=label_value_layout),
                 self.download_type_widget], layout=form_item_layout),
            Box([Label(value='IMU Sample Rate', layout=label_value_layout),
                 self.imu_sample_widget], layout=form_item_layout),
            Box([Label(value='Debug', layout=label_value_layout),
                 self.debug_widget], layout=form_item_layout),
            Box([Label(value='Test Data', layout=label_value_layout),
                 self.test_data_widget], layout=form_item_layout),
            Box([Label(value='Set Parent Model'),
                 Dropdown(options=[]),
                 Button(icon='1', description="Set")], layout=form_item_layout),
            Box([Label(value='Add Sub Model'),
                 Dropdown(options=[]),
                 Button(icon='2', description="Add")],
                layout=form_item_layout),
        ]

        self.kb_items[GENERATE_INDEX].children[1].on_click(
            self.generate_description)
        self.kb_items[PARENT_INDEX].children[2].on_click(self.set_parent_model)
        self.kb_items[SUBMODEL_INDEX].children[2].on_click(self.add_submodel)

        model_selector = Box(self.kb_items,
                             layout=pipeline_layout)
        display(model_selector)
        self.generate_pipeline()

    def generate_pipeline(self):
        if self._dsk is None:
            return

        self.update()
        try:
            self._pipeline.close()
        except:
            pass
        self.update()
        self._pipeline = (Box(self.get_model_list(), layout=pipeline_layout))
        display(self._pipeline)
