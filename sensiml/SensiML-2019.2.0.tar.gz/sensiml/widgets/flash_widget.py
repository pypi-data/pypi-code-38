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


import sys
import os
import glob
import serial
from os import listdir, system, makedirs
from subprocess import Popen, PIPE
from os.path import isfile, join, abspath, dirname, exists, splitext
from ipywidgets import widgets
from ipywidgets import Layout, Button, VBox, HBox, Textarea, Dropdown, Text, Button
from IPython.display import display
from ipywidgets import IntText
from sensiml.widgets.base_widget import BaseWidget
import zipfile

if sys.platform == 'win32':
    nrfutil = os.path.join(os.path.dirname(sys.executable), 'nrfutil.exe')
    if not os.path.exists(nrfutil):
        nrfutil = os.path.join(os.path.dirname(
            sys.executable), 'Scripts', 'nrfutil.exe')
else:
    nrfutil = os.path.join(os.path.dirname(sys.executable), 'nrfutil')


# 11/21/17: Is there a better way to do this? Add it to the model as well?
extensions_by_platform = {
    'Nordic Thingy 52': '.zip'
}

commands_by_platform = {
    'Nordic Thingy 52': {
        # 'OTA': r'{} pkg generate --application "{}" --application-version 1 --hw-version 52 --sd-req 0x98 --key-file "{}" "{}"',
        'Flash': {
            'Jlink': 'nrfjprog --program "{}" -f nrf52 --sectorerase && nrfjprog --reset -f nrf52',
            # 'BLE-DFU' : 'nrfutil dfu ble -ic NRF52 -pkg {} -p {} -n "ThingyDfu" ',
            # 'Serial' : 'nrfutil dfu serial -pkg {} -p {}'
        }
    },

}


SUPPORTED_BOARDS = ["Nordic Thingy"]


class FlashWidget(BaseWidget):
    def __init__(self, dsk=None, folder='knowledgepacks'):
        self._dsk = dsk
        self._folder = folder
        self._flashing_file = ''
        self.platforms = None
        if not exists(folder):
            makedirs(folder)

    def _refresh_platform_files(self, b=None):
        if self._dsk is None:
            return

        key_name = self.platform_name.replace(' ', '-')
        platform_search = '{}_{}'.format(
            key_name, self.platform_version).lower()
        ext_match = extensions_by_platform.get(self.platform_name, '.zip')

        platform_files = [f for f in listdir(self._folder) if isfile(join(self._folder, f))
                          and platform_search in f.lower() and splitext(f)[-1] == ext_match]

        self.flashable_files_widget.options = platform_files
        if len(platform_files) > 0:
            self.flashable_files_widget.value = platform_files[0]

    def _refresh_flash_methods(self):
        flash_methods = []
        if commands_by_platform.get(self.platform_name, None):
            flash_methods = list(
                commands_by_platform[self.platform_name]['Flash'].keys())
        self.flash_methods_widget.options = flash_methods

    def select_platform(self, platform_name):
        if self.platforms is None:
            return

        self.kp_platform_id = self._dsk.platforms[self.platform_widget.value].id
        self.platform_name = self.platforms.iloc[platform_name]['Software Platform']
        self.platform_version = self.platforms.iloc[platform_name]['Platform Version']

        self._refresh_platform_files()
        self._refresh_flash_methods()

        # if self._dsk.platforms[self.platform_widget.value].ota_capable:
        #    self.ota_button.layout.visibility = "visible"
        # else:
        self.ota_button.layout.visibility = "hidden"

        self.description_widget.value = self.platforms.iloc[platform_name]['Description']

    def get_platform_names(self):
        pf = {}
        for i in range(len(self.platforms)):
            if self.platforms.iloc[i]['Board'] in SUPPORTED_BOARDS:
                pf['{} {}'.format(self.platforms.iloc[i]['Board'],
                                  self.platforms.iloc[i]['Platform Version'])] = i

        return pf

    def _wait_for_process(self, command):
        print('Running the following command: ')
        print(command)
        sub_proc = Popen(command[0], stdout=PIPE, stderr=PIPE, shell=True)
        p_val = sub_proc.poll()
        while(p_val is None):
            print(sub_proc.stdout.read())
            print(sub_proc.stderr.read())
            p_val = sub_proc.poll()

        if p_val is 0:
            print("Process Completed successfully.")
        else:
            print("And error occured. Error code {}".format(p_val))

    def on_flash_button_clicked(self, b):
        if self.platforms is None:
            return
        if not self.flashable_files_widget.value:
            return

        available_commands = commands_by_platform[self.platform_name]['Flash']

        if 'Nordic' in self.platform_name:
            self._flashing_file = unzip_folder(
                abspath(join(self._folder, self.flashable_files_widget.value)))
            command = [available_commands['Jlink'].format(self._flashing_file)]

        else:
            print('Platform is not yet supported.')
            return

        self._wait_for_process(command)

    def on_generate_button_clicked(self, b=None):
        if self.platforms is None:
            return
        if not self.flashable_files_widget.value:
            return

        print('Generating OTA Package for platform{}'.format(self.platform_name))

        flash_file = unzip_folder(
            abspath(join(self._folder, self.flashable_files_widget.value)))
        output_file = abspath(join(self._folder, '{}.zip'.format(flash_file)))
        self.kp_platform_id = self._dsk.platforms[self.platform_widget.value].id

        if 'Thingy' in self.platform_name:  # This is Nordic Thingy
            keyfile = join(os.path.dirname(flash_file),
                           'sensiml_example_key.pem')
            write_key_file(keyfile)
            command = [commands_by_platform['Nordic Thingy 52']['OTA'].format(
                nrfutil, flash_file, keyfile, output_file)]
            self._wait_for_process(command)
        else:
            print('Platform not supported for generating OTA package')

    def _refresh(self, b=None):
        if self._dsk is None:
            return
        self.platforms = self._dsk.platforms()
        self.platform_widget.options = self.get_platform_names()

    def create_widget(self):
        self.platform_widget = widgets.Dropdown(description='Platform')
        self.description_widget = widgets.Label(layout=Layout(width='66%'))
        self.flashable_files_widget = widgets.Dropdown(
            description='Binary', layout=Layout(width='85%'))
        self.flash_methods_widget = widgets.Dropdown(
            description="Flash Method")
        self.ota_button = Button(description="Generate OTA")
        self.flash_button = Button(description="Flash")
        self.ota_button.layout.visibility = 'hidden'
        self.refresh_button = Button(
            icon='refresh', tooltip='Refresh File List', layout=Layout(width='15%'))

        if self._dsk:
            self._refresh()

        self.ota_button.on_click(self.on_generate_button_clicked)
        self.flash_button.on_click(self.on_flash_button_clicked)
        self.refresh_button.on_click(self._refresh_platform_files)

        return VBox([
            HBox([widgets.interactive(self.select_platform,
                                      platform_name=self.platform_widget), self.description_widget]),
            HBox([self.flashable_files_widget, self.refresh_button]),
            HBox([self.flash_methods_widget, self.flash_button, self.ota_button])
        ])


def unzip_folder(path_to_zip_file):

    base_name = os.path.basename(path_to_zip_file[:-4])
    hex_path = os.path.join(path_to_zip_file[:-4], base_name+'.hex')

    zip_ref = zipfile.ZipFile(path_to_zip_file, 'r')
    zip_ref.extractall(path_to_zip_file[:-4])
    zip_ref.close()

    return hex_path


def write_key_file(path_to_keyfile):
    example_key_file = ["-----BEGIN EC PRIVATE KEY-----",
                        "MHcCAQEEIHAamBrS46EBrnzzSndN7Gbmc89sj4LLsURIed8K6ynRoAoGCCqGSM49",
                        "AwEHoUQDQgAEFbkmg51LDZLkhpGxi/aqCGK7cZ0r20CVTFz4geb6t89YyNCamxJZ",
                        "cIEyi5PxDhWRvBy4pksO7AOdjFiGj4eGkg==",
                        "-----END EC PRIVATE KEY-----"]

    with open(path_to_keyfile, 'w') as out:
        for line in example_key_file:
            out.write(line)
            out.write('\n')
