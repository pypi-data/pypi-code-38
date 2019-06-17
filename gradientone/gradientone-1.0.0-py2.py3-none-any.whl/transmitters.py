#!/usr/bin/python

"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""


import base
import collections
import json
import os
import multiprocessing as multi
import requests
import traceback
from datetime import datetime

from os.path import exists
from requests_toolbelt.multipart.encoder import MultipartEncoder

import settings
from base import BaseClient, logger

from base import COMMAND_FILE
from base import t_diagnostic_logger as tlogger

os.environ['NO_PROXY'] = 'gradientone.com'
os.environ['no_proxy'] = 'gradientone.com'

TMPDIR = settings.TMPDIR
BASE_URL = settings.BASE_URL
COMPANYNAME = settings.COMPANYNAME
COMMON_SETTINGS = settings.COMMON_SETTINGS


class Transmitter(BaseClient):
    # Transmits trace data received from instrument up to the server

    def __init__(self, command_id="unknown_id"):
        self.session = requests.session()
        self.session.headers.update(base.get_headers())
        trace_dict = {
            "command_id": command_id,
        }
        self.trace_dict = collections.defaultdict(str, trace_dict)
        self.command = collections.defaultdict(str)
        self.command['id'] = command_id
        self.results_dict = collections.defaultdict(str)
        self.upload_polling_metadata = True
        self.metadata = {}

        self._is_unit_test = False
        self._is_integration_test = False

    @property
    def is_unit_test(self):
        """For testing client classes"""
        return self._is_unit_test

    @property
    def is_integration_test(self):
        """For testing client classes with server app"""
        return self._is_integration_test

    def format_csv(self):
        pass

    def generate_results_dict(self):
        self.results_dict['config_name'] = "unknown"

    def test_complete(self):
        """transmit test complete function sends a json object that is used
           to update DB on test status. Primarily metadata and indexing.
           No waveforms are sent here.
        """
        logger.info("Posting results")
        self.session = requests.session()
        self.session.headers.update(base.get_headers())
        self.post_result()
        tlogger.info("Transmitting the result blob")
        self.transmit_result_blob()
        if self.results_dict['config_name'] == 'I2C':
            # trigger the appropriate analysis handler
            _response = self.get(BASE_URL + "/analysis",
                                 params={"command_id": self.command['id'],
                                         "suite": "skywave"})
        if self.upload_polling_metadata:
            polling_metadata_url = (BASE_URL + "/polling/results/metadata/" +
                                    str(self.command['id']))
            self.post(polling_metadata_url, data=json.dumps(self.metadata))
        payload = {'id': self.command['id'],
                   'results': [{'result_id': self.metadata['result_id']}]}
        commands_url = BASE_URL + "/commands"
        response = self.put(commands_url, data=json.dumps(payload),
                            headers=base.get_headers())
        logger.info("Does command filename exist? %s" % exists(COMMAND_FILE))
        if os.path.exists(COMMAND_FILE):
            with open(COMMAND_FILE, 'r') as f:
                command = json.loads(f.read())
            logger.info("result id metadata %s" % self.metadata["result_id"])
            command['result_id'] = self.metadata['result_id']
            with open(COMMAND_FILE, 'w') as f:
                f.write(json.dumps(command))

    def transmit_result_blob(self, result_file=''):
        """Sends test results to the blobstore

        End to end waveforms are sent here.
        """
        if not result_file:
            filename = 'full-trace-%s.json' % self.metadata['result_id']
            result_file = os.path.join(TMPDIR, filename)
        logger.debug("transmitting blob")
        if not os.path.exists(result_file):
            logger.warning("%s does not exist" % filename)
            return
        else:
            tlogger.info("Transmitting waveform file")
            return self.transmit_file(result_file)

    def update_command_status(self, status):
        c_url = BASE_URL + '/commands'
        data = {
            'command_id': self.command['id'],
            'status': status,
        }
        self.put(c_url, json.dumps(data))


class ScopeTransmitter(Transmitter):
    """transmits data to server for scope information"""

    def __init__(self, trace_dict={}, **kwargs):
        Transmitter.__init__(self)
        self.trace_dict = collections.defaultdict(str, trace_dict)
        self.command = collections.defaultdict(str)
        self.metadata = collections.defaultdict(str)
        if not trace_dict:
            # Transmitter will most likely fail without a trace_dict
            logger.warning("ScopeTransmitter missing trace_dict!")
        if 'command' in trace_dict:
            self.command.update(trace_dict['command'])
        if 'metadata' in trace_dict:
            self.metadata.update(trace_dict['metadata'])
        else:
            self.metadata.update(self._get_metadata_only(trace_dict))
        self.generate_results_dict()
        self.slices = []
        self.asset_id = self.trace_dict['instrument_id']

    def _get_metadata_only(self, trace_dict):
        """Removes the command and trace data to get metadata only

        Summary:
            Iterates through the channels list to remove the y_values
            that are a long list. Also removes the command dictionary
            if one is present. This will leave just the metadata

        Returns:
            A dictionary with a copy of the just the metadata from
            the trace_dict, without the trace values themselves.
        """
        data = collections.defaultdict(int, trace_dict)
        for channel in data['channels']:
            if 'y_values' in channel:
                del channel['y_values']
            else:
                logger.info("Channel has no y_values: {}"
                            .format(channel))
        if 'command' in trace_dict:
            del trace_dict['command']
        return data

    def generate_results_dict(self):
        results_page_link = BASE_URL + '/results/' + self.metadata['result_id']
        self.results_dict = {
            'results_link': results_page_link,
            'gateway': settings.GATEWAY_ID,
            'company_nickname': COMPANYNAME,
            'test_plan': self.trace_dict['test_plan'],
            'config_name': self.trace_dict['config_name'],
            'raw_setup': self.trace_dict['raw_setup'],
            'config_excerpt': self.trace_dict['config_excerpt'],
            'config_scorecard': self.trace_dict['config_scorecard'],
            'g1_measurement': self.trace_dict['g1_measurement'],
            'g1_measurement_results': self.trace_dict['g1_measurement_results'],  # noqa
            # for the Result datastore object, we need the following
            'command_id': self.trace_dict['command_id'],
            'instrument_type': self.trace_dict['instrument_type'],
            'category': '',
            'tags': [],
            'plan_id': '',
            'dut_id': '',
            'user_id': self.trace_dict['user_id'],
        }
        # remove the ivi channel objects from the result
        for ch in self.metadata['channels']:
            if 'ivi' in ch:
                ch.pop('ivi')
        self.results_dict.update(self.metadata)

    def _save_slices(self):
        """Saves the slices to the slice directory"""
        self.update_command_status('saving slices')
        slice_dir = os.path.join(base.TMPDIR, 'slices')
        if not os.path.exists(slice_dir):
            os.makedirs(slice_dir)
        voltage_start_time = 0
        dict_of_slice_lists = collections.defaultdict(int)
        list_of_slices = []
        time_step = 0
        for channel in self.trace_dict['channels']:
            # some channels might only have metadata, no trace values
            if 'y_values' not in channel:
                # assign an empty list for these channels and continue on
                dict_of_slice_lists[channel['name']] = []
                continue
            voltages = channel['y_values']
            # create list of slices
            list_of_slices = [voltages[x:x + int(settings.MAX_LENGTH_FOR_BROWSER)]  # nopep8
                              for x in range(0, len(voltages), int(settings.MAX_LENGTH_FOR_BROWSER))]  # nopep8
            dict_of_slice_lists[channel['name']] = list_of_slices
            logger.debug("length of list of slices for %s: %s"
                         % (channel['name'], len(list_of_slices)))
            self.metadata['total_points'] = len(voltages)
            # if it's not set, set the time_step using the channel's
            if not time_step and 'time_step' in channel:
                time_step = channel['time_step']
        result_id = self.metadata['result_id']
        for idx, slice_points in enumerate(list_of_slices):
            slices_by_channel = {}
            for ch in dict_of_slice_lists:
                if idx + 1 > len(dict_of_slice_lists[ch]):
                    logger.debug("""Warning! Slice index greater than length of
                        list of slices for %s""" % ch)
                else:
                    slices_by_channel[ch] = dict_of_slice_lists[ch][idx]
            voltage_start_time += time_step * len(slice_points)
            slice_data = {
                'result_id': result_id,
                'command_id': self.trace_dict['command_id'],
                'slice_index': idx,
                'num_of_slices': len(list_of_slices),
                'voltage_start_time': voltage_start_time,
                'time_step': time_step,
                'data': slices_by_channel,
            }
            self.slices.append(slice_data)
            slice_data = json.dumps(slice_data)
            filename = result_id + '-slice-' + str(idx) + '.json'
            slice_file = os.path.join(slice_dir, filename)
            with open(slice_file, 'w') as f:
                f.write(slice_data)
        self.metadata['num_of_slices'] = len(list_of_slices)
        max_len = int(settings.MAX_LENGTH_FOR_BROWSER)
        slice_length = max_len
        if 'total_points' in self.metadata:
            if self.metadata['total_points'] < max_len:
                slice_length = self.metadata['total_points']
        self.metadata['slice_length'] = slice_length

    def _start_slice_transmission_process(self):
        """Starts a separate process for slice transmission

        Summary:
            This starts a new process that transmits slices of data
            for long waveforms. This frees up the instrument to handle
            new commands.

        Returns:
            None. This method does not return a value
        """
        name = self.metadata['result_id'] + '_slice_transmitter'
        args = (self.command['id'],)
        ps = multi.Process(target=transmit_slices_tgt, name=name, args=args)
        ps.start()

    def transmit_config(self):
        """Posts config to server for storage"""
        if 'raw_setup' in self.trace_dict:
            info = {'raw_setup': self.trace_dict['raw_setup']}
        else:
            info = {}
        payload = {
            'config_excerpt': self.trace_dict['config_excerpt'],
            'config_data': {
                'new_config_name': self.trace_dict['command_id'],
                'info': info,
                'instrument_type': self.trace_dict['instrument_type'],
                'company_nickname': COMPANYNAME,
            }
        }
        create_config_url = BASE_URL + "/configurations"
        self.post(
            url=create_config_url,
            data=json.dumps(payload),
            headers=base.get_headers()
        )

    def transmit_logs(self, to_blob=False):
        filename = str(self.command['id']) + '.log'
        if to_blob:
            # TODO: add functionality
            # transmit_logs(command_id=self.command['id'])
            return
        # else it will just go to memcache
        multipartblob = MultipartEncoder(
            fields={
                'logfile': (filename, open('client.log', 'rb'), 'text/plain'),
                'testrunid': str(self.command['id']),
            }
        )
        log_url = (BASE_URL + "/logs/" + str(self.command['id']))
        headers = {'Content-Type': multipartblob.content_type}
        resp = self.post(log_url, data=multipartblob, headers=headers)
        logger.debug(resp.text)

    def transmit_trace(self):
        """Transmits the trace result, including the slices

        """
        self._save_slices()
        self._start_slice_transmission_process()
        # complete transmission indexing blobstore data
        self.test_complete()
        tid = self.trace_dict['command_id']
        tlogger.info("Posting logfile")
        self.post_logfile(command_id=tid)

    def shrink(self, voltage_list, time_step, mode="normal", limit=400):
        len_voltage_list = len(voltage_list)
        dec_factor = len_voltage_list / int(limit)
        if dec_factor == 0:
            dec_factor = 1
        new_time_step = dec_factor * float(time_step)
        shrunk_list = []
        index = 0
        while index < len_voltage_list:
            if mode == "normal":
                shrunk_list.append(voltage_list[index])
                index += dec_factor
            else:  # implement other modes here
                pass
        shrunk_data = {
            'y_values': shrunk_list,
            'time_step': new_time_step,
        }
        return shrunk_data

    def generate_thumbnail_data(self):
        try:
            filename = 'full-trace-%s.json' % self.metadata['result_id']
            infile = os.path.join(TMPDIR, filename)
            with open(infile, 'r') as f:
                trace_data = json.loads(f.read())
            channels = []
            for ch in trace_data['channels']:
                shrunk_channel = {'name': ch['name']}
                data = self.shrink(ch['y_values'], ch['time_step'])
                shrunk_channel.update(data)
                channels.append(shrunk_channel)
            return {'channels': channels}
        except Exception as e:
            logger.warning(e, exc_info=True)

    def post_result(self):
        tlogger.info("Generating thumbnail data")
        thumbnail_data = self.generate_thumbnail_data()
        # alias to shorten line length
        cfg_ex = self.results_dict['config_excerpt']
        logger.info("cfg_ex  is {}".format(cfg_ex))
        payload = {
            # 'result' is for the datastore entity
            'result': {
                'id': self.results_dict['result_id'],
                'command_id': self.results_dict['command_id'],
                'config_name': self.results_dict['config_name'],
                'instrument_type': self.results_dict['instrument_type'],
                'tags': self.results_dict['tags'],
                'plan_id': self.results_dict['plan_id'],
                'info': self.results_dict,
                'user_id': self.results_dict['user_id']
            },

            'fields': [
                {
                    'name': 'config_name',
                    'value': self.results_dict['config_name'],
                    'type': 'text'
                },
                {
                    'name': 'gateway',
                    'value': self.results_dict['gateway'],
                    'type': 'text'
                },
                {
                    'name': 'instrument_type',
                    'value': self.results_dict['instrument_type'],
                    'type': 'text'
                },
                {
                    'name': 'command_id',
                    'value': self.results_dict['command_id'],
                    'type': 'text'
                },
                {
                    'name': 'start_datetime',
                    'value': str(datetime.now()),
                    'type': 'text'
                },
                {
                    'name': 'thumbnail_json',
                    'value': json.dumps(thumbnail_data),
                    'type': 'text'
                },
                {
                    'name': 'serial',
                    'value': self.metadata['serial'],
                    'type': 'text'
                },
                {
                    'name': 'user_id',
                    'value': self.results_dict['user_id'],
                    'type': 'atom'
                },
            ],
            'index_name': 'results'
        }
        if isinstance(cfg_ex, dict):
            if "acquisition" in cfg_ex:
                if "type" in cfg_ex["acquisition"]:
                    payload['fields'].append({
                        'name': 'acquisition_type',
                        'value': cfg_ex['acquisition']['type'],
                        'type': 'text'
                    })
            if "trigger" in cfg_ex:
                if "source" in cfg_ex["trigger"]:
                    payload['fields'].append({
                        'name': 'trigger_source',
                        'value': cfg_ex['trigger']['source'],
                        'type': 'text'
                    })
                if "type" in cfg_ex["trigger"]:
                    payload['fields'].append({
                        'name': 'trigger_type',
                        'value': cfg_ex['trigger']['type'],
                        'type': 'text'
                    })
                if "level" in cfg_ex["trigger"]:
                    payload['fields'].append({
                        'name': 'trigger_level',
                        'value': cfg_ex['trigger']['level'],
                        'type': 'number'
                    })
        channels = self.results_dict['channels']
        channel_num = 0
        for channel in channels:
            channel_num += 1
            if not channel['name']:
                channel['name'] = 'ch' + str(channel_num)
            field = {
                'name': channel['name'] + '_enabled',
                'value': channel['enabled'],
                'type': 'text',
            }
            payload['fields'].append(field)
        for channel in self.results_dict['channels']:
            self._add_channel_measurement_fields(payload, channel)
            if 'y_values' in channel:
                del channel['y_values']  # remove because it's too large
        self._validate_fields(payload['fields'])
        url = BASE_URL + "/results"
        tlogger.info("Posting results")
        self.post(url, data=json.dumps(payload))

    def _add_channel_measurement_fields(self, payload, channel):
        if 'waveform_measurements' not in channel:
            msg = "no waveform_measurements to add measurement fields to"
            logger.warning(msg)
            return
        for measurement in channel['waveform_measurements']:
            field = self._get_measurement_field(measurement, channel)
            if field:
                payload['fields'].append(field)

    def _get_measurement_field(self, measurement, channel):
        field = {}
        try:
            field['name'] = channel['name'] + '_' + measurement['ivi_name']
            field['value'] = measurement['value']
            if field['value'] == 'N/A':
                return field
            field['type'] = 'number'
        except KeyError:
            logger.debug("KeyError in _get_measurement_field %s" % measurement)
        except Exception as e:
            logger.warning(e, exc_info=True)
        return field

    def _validate_fields(self, fields):
        used_field_names = []
        valid_fields = []
        for field in fields:
            try:
                if field['name'] in used_field_names:
                    logger.warning("%s already used" % field['name'])
                val = field['value']
                max_val = settings.MAX_VALID_MEAS_VAL
                if isinstance(val, (int, float)) and val > max_val:
                    val = max_val
                field['value'] = val
                valid_fields.append(field)
            except KeyError:
                logger.debug("KeyError in _validate_fields %s" % field)
            except Exception as e:
                logger.debug(e, exc_info=True)
        return valid_fields


def transmit_slices_tgt(command_id):
    """Target function for transmitting slices in a separate process"""
    slice_transmitter = SliceTransmitter(command_id)
    slice_transmitter.transmit_slices()


class SliceTransmitter(Transmitter):
    """For transmitting trace slices saved in a directory"""
    def transmit_slices(self):
        slice_dir = os.path.join(base.TMPDIR, 'slices')
        if not os.path.exists(slice_dir):
            return
        self.update_command_status('transmitting slices')
        for filename in os.listdir(slice_dir):
            if '-slice-' in filename:
                slice_file = os.path.join(slice_dir, filename)
                self.transmit_file(slice_file, mode='r')
                self.remove_file(slice_file)
                result_id = filename.split('-slice-')[0]
                slice_idx = filename.split('-slice-')[-1].split('.')[0]
                metadata = {
                    'result_id': result_id,
                    'slice_index': slice_idx,
                    'ready': True,
                }
                url = BASE_URL + '/results/' + result_id + '/slices/metadata'
                self.put(url, data=json.dumps(metadata))
        self.update_command_status('complete')
