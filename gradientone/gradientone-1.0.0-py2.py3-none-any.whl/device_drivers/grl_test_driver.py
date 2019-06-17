#!/usr/bin/python

"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""

import collections
import json
import gateway_helpers
from data_manipulation import grl
from device_drivers import usb_controller
from ivi_instruments import get_instrument
from scope_driver import ScopeDriver, DEFAULT_TEK_CONFIG

import datetime
import time
import traceback

from gateway_helpers import dt2ms, \
    round_sig, logger


class GRLTestDriver(ScopeDriver):

    def __init__(self, setup, instrument=None, *args, **kwargs):
        """initializes driver for grl tests

           setup - instructions from the server, should contain
           a 'config' which keys to a list of dicts with instructions
           for either the power controller (GRL-USB-PD) or the
           Tektronix scope (TektronixDPO7354C). This 'config' is
           assigned to the 'grl_config' attribute', a list used
           when the start_test is called
        """
        self.ce_dict = collections.defaultdict(lambda: {})
        self.ce_dict.update(DEFAULT_TEK_CONFIG)
        setup['config']['config_excerpt'] = json.dumps(self.ce_dict)
        ScopeDriver.__init__(self, setup, instrument)
        self.exception_counter = 0
        self.logger = gateway_helpers.logger
        self.config = collections.defaultdict(lambda: {})
        self.config.update(setup['config'])
        self.config['config_excerpt'] = self.ce_dict
        self.instr = instrument
        self.channels = self.instr.channels
        self.time_step = 0.000001

        if instrument:
            self.tek = instrument
        else:
            try:
                self.logger.info("getting instrument")
                self.tek = get_instrument(self.command)
                self.tek.utility.reset()
            except Exception:
                self.exception_counter += 1
                self.logger.info("exception getting instrument", exc_info=True)
        try:
            self.logger.info("getting instrument")
            self.usbc = usb_controller.RawUsbController(vendor_id=0x227f,
                                                        product_id=0x0002)
        except Exception:
            self.exception_counter = 0
            self.logger.info("exception getting usb controller", exc_info=True)
        self.grl_config = self.grl_converter(setup['grl_config'])

    def grl_converter(self, config):
        for item in config:
            coms = item['commands']
            if not isinstance(coms, list):
                continue
            for i, c in enumerate(coms):
                coms[i] = c.decode('hex').strip()
        return config

    def set(self, obj, attr, val):
        """Sets the objects attribute (attr) with the value supplied and logs
        the success or error"""
        self.check_commands_completed()
        try:
            setattr(obj, attr, val)
            self.logger.info("TEK SUCCESS set %s with %s" % (attr, val))
        except Exception:
            self.logger.info("TEK ERROR: %s not set with %s"
                             % (attr, val), exc_info=True)
            self.exception_counter += 1

    def write(self, command="", tek=None):
        """Writes to the tek with the _write function and logs the success or
        error. If no tek is supplied, the class tek object will be used."""
        self.check_commands_completed()
        if not tek:
            tek = self.tek
        try:
            tek._write(command)
            self.logger.info("TEK SUCCESS write:%s" % command)
        except Exception:
            self.logger.info("TEK ERROR: exception with write:%s"
                             % command, exc_info=True)
            self.exception_counter += 1

    def start_test(self):
        configs = self.grl_config
        self.post_status_update("Commencing Transmitter Eye Diagram Test")
        for idx, config in enumerate(configs):
            if idx == 1:
                self.post_status_update("Configuring Scope")
            if idx == 6:
                self.post_status_update("Sending BIST Signal")
            if config['device'] == 'TektronixDPO7354C':
                self.config_scope(config)
            elif config['device'] == 'GRL-USB-PD':
                self.write_to_usbc(config['commands'])
            time.sleep(1)
        self.overlay()
        self.post_status_update("Completed Transmitter Eye Diagram Test")

    def config_scope(self, config):
        if config['command_type'] == 'scpi':
            for command in config['commands']:
                self.write(command)
        elif config['command_type'] == 'python-ivi':
            self.pass_ivi_cmds(config['commands'])

    def write_to_usbc(self, commands):
        for command in commands:
            try:
                self.usbc.write(command=command)
            except Exception as e:
                self.logger.warning(e, exc_info=True)
                self.exception_counter += 1

    def get_voltage_list(self, volts):
        return [round_sig(float(volt)) for volt in volts]

    def pass_ivi_cmds(self, commands):
        for command in commands:
            if command == 'fetch_waveform':
                self.post_status_update("Fetching Waveform")
                self.times['fetch_measurements_start'] = time.clock()
                self._set_enabled_list()
                self.time_step = 0.000001
                self.slice_dict = collections.defaultdict(int)
                self.first_slice = collections.defaultdict(int)
                start_tse = int(dt2ms(datetime.datetime.now()))
                self.trace_dict['Start_TSE'] = start_tse  # eventually remove
                self.trace_dict['start_tse'] = start_tse  # this is better
                logger.debug("enabled_list: %s" % self.enabled_list)
                if not self.enabled_list:
                    self.enabled_list['ch1']
                meas_dict = {}
                try:
                    ch = "ch1"
                    voltage_list = None
                    logger.debug('invoking fetch_waveform')
                    tek_channel = self.tek.channels[0]
                    waveform = tek_channel.measurement.fetch_waveform()
                    logger.debug("waveform length: %s" %
                                 (len(waveform.x)))
                    self.time_step = waveform.x_increment
                    voltage_list = self.get_voltage_list(waveform.y)
                    slice_list = self.get_slice_list(voltage_list)
                    self.slice_dict[ch] = slice_list
                    self.first_slice[ch] = slice_list[0]
                    meas_dict[ch] = collections.defaultdict(str)
                    channel_data = {
                        'y_values': voltage_list,
                        'time_step': self.time_step,
                        'start_time': waveform[0][0],
                        'end_time': waveform[-1][0],
                    }
                    self.trace_dict['channels'].append(channel_data)
                    self.write_to_json_file(data=voltage_list,
                                            filename='grl-data.json')
                except Exception:
                    logger.info("failed to fetch waveform for", ch)
                    logger.debug(traceback.format_exc())
                self.trace_dict['raw_sec_btw_samples'] = self.time_step
                self.times['fetch_measurements_end'] = time.clock()
                return meas_dict
            elif command == 'fetch_setup':
                self.post_status_update("Fetching Setup")
                self.instrument_setup = self.tek.system.fetch_setup()

    def get_outputs(self, index=0):
        pass

    def overlay(self):
        overlay_volts = grl.get_volts_for_overlay(volts_file='grl-data.json')
        file_key = 'overlay-' + str(self.command_id)
        grl.count_and_post(overlay_volts, file_key=file_key)
