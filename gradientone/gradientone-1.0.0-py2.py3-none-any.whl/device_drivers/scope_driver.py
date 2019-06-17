#!/usr/bin/python

"""

Copyright (C) 2016-2017 GradientOne Inc. - All Rights Reserved
Unauthorized copying or distribution of this file is strictly prohibited
without the express permission of GradientOne Inc.

"""
import device_drivers_parent_path
device_drivers_parent_path.insert()

import base
import datetime
import time
import collections
from collections import defaultdict
from csv import DictReader
import gateway_helpers
import json
import logging
import os
import os.path
import socket
import traceback
import usb
import copy
import settings
from gateway_helpers import dt2ms, round_sig, logger
from base_driver import BaseDriver
from dummy_scope import DummyScope
from base import t_diagnostic_logger as tlogger
from base import ReadSettingsError, WriteSettingsError, FetchScreenshotError
from base import FetchWaveformError, FetchMeasurementError
from gateway_helpers import timeout

COMMAND_FILE = settings.COMMAND_FILE
COMPANYNAME = settings.COMPANYNAME
TMPDIR = settings.TMPDIR
BASE_URL = settings.BASE_URL
GATEWAY_ID = settings.GATEWAY_ID


DEFAULT_TEK_CONFIG = {
    "outputs": {
        "impedance": 50,
        "enabled": True
    },
    "output_noise": {
        "enabled": False,
        "percent": 0
    },
    "channels": [{
        "range": 2,
        "offset": 0,
        "enabled": True,
        "coupling": "dc",
        "name": "ch1"
    }, {
        "range": 1,
        "offset": 0,
        "enabled": False,
        "coupling": "dc",
        "name": "ch2"
    }, {
        "range": 1,
        "offset": 0,
        "enabled": False,
        "coupling": "dc",
        "name": "ch3"
    }, {
        "range": 1,
        "offset": 0,
        "enabled": False,
        "coupling": "dc",
        "name": "ch4"
    }],
    "trigger": {
        "source": "ch1",
        "type": "edge",
        "coupling": "dc",
        "level": 0.288,
        "edge_slope":"positive",
        "holdoff":1.6e-08,
    },
    "acquisition": {
        "number_of_points_minimum": 1000,
        "start_time": -4.999999999999996e-06,
        "number_of_envelopes": 0,
        "time_per_record": 9.999999999999999e-06,
        "type": "average",
        "number_of_averages": 512
    },
    "standard_waveform": {
        "dc_offset": 0,
        "symmetry": 50,
        "duty_cycle_high": 50,
        "start_phase": 0,
        "waveform": "square",
        "frequency": 220000,
        "amplitude": 1,
        "pulse_width": 1e-06
    }
}


class IviDeviceDriver(BaseDriver):

    """driver for ivi instruments"""

    def __init__(self, command, instrument=None, *args, **kwargs):
        BaseDriver.__init__(self, command, *args, **kwargs)
        self.instr = instrument
        try:
            self.instr._write("*CLS")
        except Exception as e:
            logger.info("IviDeviceDriver *CLS exc: {}".format(e))
        try:
            self.ivi_channels = self.instr.channels
        except Exception as e:
            self.ivi_channels = []
            logger.info("IviDeviceDriver ivi_channels exc: {}".format(e))

    @timeout(20)
    def fetch_raw_setup_wrapper(self):
        result = self.instr.system.fetch_setup()
        return result

    def fetch_raw_setup(self, last_try=False):
        msg = "Fetching raw setup"
        tlogger.info(msg)
        try:
            raw_setup = self.fetch_raw_setup_wrapper()
            msg = "Raw setup acquired successfully"
            self._log_activity(msg)
        except gateway_helpers.TimeoutError:
            msg = "Failed to read raw setup due to a timeout error"
            self._log_activity(msg, level='warning')
            tlogger.error(msg)
            return None
        except Exception:
            self.logger.warning("Fetch setup failed", exc_info=True)
            if last_try:
                msg = "Failed to read raw setup to an unkonwn error"
                self._log_activity(msg, level='warning')
                tlogger.error(msg)
                raise ReadSettingsError
                return None
            else:
                raw_setup = self.fetch_raw_setup_wrapper(last_try=True)
        msg = "Fetched raw setup successfully"
        tlogger.info(msg)
        if raw_setup is None:
            return None
        else:
            return raw_setup

    @timeout(10)
    def system_load_setup_wrapper(self, ascii_config):
        self.instr.system.load_setup(ascii_config)
        return

    def load_raw_setup(self, try_count=0):
        logger.debug("loading raw setup")
        ascii_config = self.config['info']['raw_setup'].encode('ascii')
        try:
            self.system_load_setup_wrapper(ascii_config)
        except gateway_helpers.TimeoutError:
            logger.debug("Load setup failed", exc_info=True)
            tlogger.info("Load setup failed")
            msg = "Loading setup timed out"
            self._log_activity(msg, level='warning')
        except Exception:
            self.logger.warning("failed loading raw setup", exc_info=True)
            if try_count > 10:
                logger.debug("not retrying")
                msg = "Load setup failed"
                self._log_activity(msg, level='warning')
                raise WriteSettingsError
            else:
                # reset the instrument object and retry load_raw_setup
                io_string = self.instr.driver_operation.io_resource_descriptor
                self.instr.close()
                time.sleep(1)
                logger.debug("retrying...")
                self.instr.initialize(resource=io_string)
                try_count = try_count + 1
                self.load_raw_setup(try_count)

    def _setinstr(self, ivi_obj, key, value, label=''):
        try:
            setattr(ivi_obj, key, value)
            self.config_scorecard['success'].append(label + key)
            return True
        except Exception:
            logger.debug("failed setting %s" % label + key)
            logger.debug(traceback.format_exc())
            self.exception_count += 1
            self.config_scorecard['failure'].append(label + key)
            return False

    def _setinstr_with_tries(self, ivi_obj, key, value, label='', tries=3):
        for attempt in range(tries):
            try:
                setattr(ivi_obj, key, value)
                self.config_scorecard['success'].append(label + key)
                return
            except usb.core.USBError as e:
                logger.debug("USB Error in setting instrument", exc_info=True)
                self.handle_usb_error(e)
            except Exception:
                logger.debug("failed to set ivi setting: %s %s" %
                             (key, value), exc_info=True)
                self.exception_count += 1
                time.sleep(0.1)
        self.config_scorecard['failure'].append(label + key)
        raise WriteSettingsError


class InvalidConfigError(Exception):

    def __init__(self, config={}, *args, **kwargs):
        logger.warning("Invalid Config: {};".format(config))
        super(InvalidConfigError, self).__init__(*args, **kwargs)


class ScopeDriver(IviDeviceDriver):

    """driver for oscilloscopes"""

    def __init__(self, command, instrument=None, *args, **kwargs):
        IviDeviceDriver.__init__(self, command, instrument, *args, **kwargs)
        self.trace_dict = {}
        self.channels = []  # for storing channel info by channel
        self.trace_dict['channels'] = self.channels  # store it with other data
        try:
            self.command = collections.defaultdict(str, command)
        except TypeError:
            default_command = {'info': {}}
            logger.warning("Failed to created command defaultdict, due to "
                           "TypeError. Setting the command attribute to {}"
                           .format(default_command))
            self.command = collections.defaultdict(str, default_command)
        self.channel_names = [c.name for c in self.ivi_channels]
        try:
            self._analog_channel_names = self.instr._analog_channel_name
        except Exception as e:
            self._analog_channel_names = []
            logger.debug("ScopeDriver _analog_channel_names exc: {}".format(e))
        self.ch_idx_dict = {}
        for idx, ch in enumerate(self.channel_names):
            self.ch_idx_dict[ch] = idx
        self.slice_dict = collections.defaultdict(int)
        self.enabled_list = ['ch1']  # by default, only ch1 enabled
        self.set_adders = 0
        self.exception_count = 0
        self.screenshot_blob_key = ''
        self.g1_measurement_results = collections.defaultdict(int)
        self._horizontal_divisions = 10
        self._vertical_divisions = 10
        dd = collections.defaultdict(str)
        self.ce_dict = collections.defaultdict(lambda: dd)
        self.config_scorecard = {
            'success': [],
            'failure': [],
            'errors': {
                'usb_timeouts': 0,
                'usb_resource_busy': 0,
            },
            'times': {
                'start_to_finish': 0,
                'load_config': 0,
                'fetch_waveform': 0,
                'fetch_measurements': 0,
            }
        }
        self.times = {
            'init': time.time(),
            'load_config_start': 0,
            'load_config_end': 0,
            'fetch_measurements_start': 0,
            'fetch_measurements_end': 0,
            'complete': 0,
        }
        self.config = collections.defaultdict(lambda: {})
        self.config.update(self.command['info'])
        capture_modes = ['Capture', 'Quickset', 'Autoset']
        if self.command['name'] in capture_modes:
            logger.debug(
                "creating cloud capture/autoset/quickset driver instance")
            self.capture_mode = True
        else:
            logger.debug("creating user-configured driver instance")
            self.capture_mode = False

        if self.command['label'] == 'grl_test':
            logger.debug("using DEFAULT_TEK_CONFIG")
            self.ce_dict.update(DEFAULT_TEK_CONFIG)
        elif self.command['name'] == 'Config':
            ce = self.command['info']['config_excerpt']
            validated = self.validate_config_excerpt(ce)
            if validated == {}:
                raise InvalidConfigError(config=ce)
            self.ce_dict.update(ce)
        else:
            self.ce_dict.update(self.command['info'])
        self.command_id = str(self.command['id'])
        base_meas = [
            {
                'ivi_name': 'frequency',
                'display_name': 'Frequency',
                'units': 'Hz',
            },
        ]
        self.meas_list = []
        self.meas_list.extend(base_meas)
        if not settings.SIMULATED:
            if self.command['info']['instrument_type'] == 'TektronixMSO5204B':
                specific_meas = [
                    {
                        'ivi_name': 'voltage_cycle_average',
                        'display_name': 'Voltage Cycle Average',
                        'units': 'V',
                    },
                    {
                        'ivi_name': 'overshoot_negative',
                        'display_name': 'Overshoot Negative',
                        'units': 'V',
                    },
                    {
                        'ivi_name': 'overshoot_positive',
                        'display_name': 'Overshoot Positive',
                        'units': 'V',
                    },
                ]
                self.meas_list.extend(specific_meas)

            elif self.command['info']['instrument_type'] == 'RigolMSO2302A':
                self.meas_list.append({
                    'ivi_name': 'overshoot',
                    'display_name': 'Overshoot',
                    'units': 'V',
                })
            elif self.command['info']['instrument_type'] == 'RigolDS1054Z':
                self.meas_list.append({
                    'ivi_name': 'overshoot',
                    'display_name': 'Overshoot',
                    'units': 'V',
                })
        self.test_plan = False
        self.acq_dict = {
            'time_per_record': '',
            'number_of_points_minimum': '',
            'type': '',
            'start_time': '',
            'number_of_averages': '',
            'number_of_envelopes': '',
            'record_length': '',
        }
        if settings.SIMULATED:
            self.ce_dict['enabled_list'] = self.enabled_list
        logger.debug("ce_dict after init: %s" % self.ce_dict)
        if 'channels' not in self.ce_dict:
            # if empty, initialize with names in self.channel_names:
            self.ce_dict['channels'] = []
            for ch_name in self.channel_names:
                self.ce_dict['channels'].append({'name': ch_name})
        logger.debug("trying to get channels object")
        self.ivi_channels = self.instr.channels
        self.logger = base.logger
        self.first_slice = collections.defaultdict(int)
        self.time_step = None
        self.waveform_length = 0
        self.slice_length = 0
        self.trace_dict['channels'] = self.channels
        self.channel_settings = ['range', 'offset', 'position', 'coupling']
        self.category = 'Oscilloscope'
        self.device_under_test = ''
        try:
            self.instrument_serial = instrument.identity.instrument_serial_number  # noqa
        except socket.error as e:
            logger.warning("Socket error {} when asking for serial number"
                           .format(e))
            instrument.close()
            raise
        except Exception as e:
            logger.warning("Unexpected exception when asking for serial. {}"
                           .format(e), exc_info=True)
            raise
        self._is_unit_test = self.command['unit_test']

    @timeout(5)
    def set_timebase_wrapper(self, instrument, key, value):
        self._setinstr_with_tries(instrument, key,
                                  value, label='timebase_',
                                  tries=3)
        return

    def set_timebase(self, timebase_dict):
        for key in timebase_dict:
            self.set_adders += 1
            tlogger.info("Programming the timebase setting %s to %s " %
                         (key, timebase_dict[key]))
            try:
                self.set_timebase_wrapper(
                    self.instr.timebase, key, timebase_dict[key])
            except gateway_helpers.TimeoutError:
                logger.error("Failed to write timebase setting: %s to %s" % (
                    key, timebase_dict[key]), exc_info=True)
                tlogger.error("Failed to write timebase setting: %s to %s" % (
                    key, timebase_dict[key]), exc_info=True)
                msg = "Failed to write timebase setting %s to %s " % (
                    key, timebase_dict[key])
                self._log_activity(msg, level='warning')
                raise WriteSettingsError
            except Exception:
                logger.error("Failed to write timebase setting: %s to %s" % (
                    key, timebase_dict[key]), exc_info=True)
                tlogger.error("Failed to write timebase setting: %s to %s" % (
                    key, timebase_dict[key]), exc_info=True)
                msg = "Failed to write timebase setting %s to %s " % (
                    key, timebase_dict[key])
                self._log_activity(msg, level='warning')
                raise WriteSettingsError

    def load_config(self):
        tlogger.info("Loading a user created config")
        self.times['load_config_start'] = time.clock()
        if 'info' in self.config and self.config['info'] is not None:
            if 'raw_setup' in self.config['info']:
                tlogger.info("Loading raw setup")
                self.load_raw_setup()
            else:
                tlogger.info("No raw setup to load")

        # Sometimes the instrument needs time before it's ready to load
        # configuration acquisition, but more testing needed to verify
        # if this is still needed. This is an area where we could optimize
        # speed. It's possible this is only needed after load_raw_setup,
        # or only needed for certain instrument types
        time.sleep(2)
        if 'acquisition' in self.ce_dict:
            self._set_acquisition(self.ce_dict['acquisition'])
        self.set_channels()
        self.load_special_fields()
        if 'optional features' in self.command['info']:
            self._load_optional_features()
        tlogger.info("pre trigger check insturent")
        if 'trigger' in self.ce_dict:
            self.set_trigger(self.ce_dict['trigger'])
        self.times['load_config_end'] = time.clock()

    def load_special_config_fields(self):
        pass

    def load_special_fields(self):
        if 'timebase' in self.ce_dict:
            self.set_timebase(self.ce_dict['timebase'])
        if 'horizontal' in self.ce_dict:
            self.set_timebase(self.ce_dict['horizontal'])
        try:
            afg_enabled = self.ce_dict['outputs']['enabled']
            tlogger.info("Enabling the AFG")
            logger.debug("afg_enabled is: %s" % afg_enabled)
        except KeyError:
            logger.debug("afg_enabled KeyError, setting False")
            afg_enabled = self.ce_dict['outputs']['enabled'] = False
        if afg_enabled:
            try:
                self.set_outputs(self.ce_dict['outputs'])
                self.set_standard_waveform(self.ce_dict['standard_waveform'])
            except:
                logging.warning("AFG Enabled, but exception setting output",
                                exc_info=True)

    def load_autoset(self):
        """loads autoset/autoscale command to scope

        After channels loaded, returns boolean channels_enabled
        """
        tlogger.info("Loading the autoset configuration")
        self.set_autoscale()
        time.sleep(5)
        channels_enabled = []
        for ch in self.channel_names:
            if self.instr.channels[self.ch_idx_dict[ch]].enabled:
                channels_enabled.append(ch)
        if channels_enabled:
            return True
        else:
            logger.warning('No Channels Enabled')
            return False

    @timeout(5)
    def set_autoscale_wrapper(self):
        self.instr.measurement.auto_setup()
        return

    def set_autoscale(self):
        """issues autoscale command"""
        try:
            self.set_autoscale_wrapper()
        except gateway_helpers.TimeoutError:
            logger.debug("Autoscale failed", exc_info=True)
            tlogger.info("Autoscale failed", exc_info=True)
        except Exception:
            logger.debug("Autoscale failed", exc_info=True)
            tlogger.info("Autoscale failed", exc_info=True)
            msg = "Failed to write autoscale command"
            self._log_activity(msg, level='warning')
            raise WriteSettingsError

    def check_any_channel_enabled(self):
        """Checks if any channel is enabled. If none, return False"""
        channels_enabled = []
        for channel in self.instr.channels[0:4]:
            if channel.enabled:
                channels_enabled.append(channel.name)
        logger.info("check_any_channel_enabled() channels_enabled: {}"
                    .format(channels_enabled))
        if channels_enabled:
            tlogger.info(
                "Capture command does not load a config. Check channel enabled is: %s" % channels_enabled)
            return True
        else:
            logger.warning('No Channels Enabled')
            tlogger.info(
                "Capture command does not load a config. No channels enabled.")
            return False

    def check_scope_acquisition_length(self):
        """Checks current setting of acquisition length"""
        logger.info("Checking acquisition length")
        key = "record_length"
        try:
            length = self.get_acquisition_wrapper(key)
        except gateway_helpers.TimeoutError:
            logger.debug("exception in reading acquisition length", exc_info=True)
            msg = "Failed to read acquisition length"
            self._log_activity(msg, level='warning')
            raise ReadSettingsError
        except Exception:
            logger.error("exception in reading acquisition length", exc_info=True)
            msg = "Failed to read acquisition length"
            self._log_activity(msg, level='warning')
            raise ReadSettingsError
        msg = ("Acquisition length is %s " % length)
        logger.info((msg).rjust(len(msg) + 9))
        if length > 1000000:
            msg = ("The memory depth of this waveform capture is large or set to AUTO. When "
                   "status returns to ready you can run another test")
            self._log_activity(msg, data={'alert': msg}, level='info')

    def _validate_acq_dict(self, acq_dict):
        if 'record_length' in acq_dict:
            del acq_dict['record_length']
        logger.debug("setting acquisition: " + str(acq_dict))
        def_acq_dict = collections.defaultdict(str, acq_dict)
        if def_acq_dict['type'] != 'average':
            if 'number_of_averages' in acq_dict:
                del acq_dict['number_of_averages']
        if def_acq_dict['type'] != 'envelope':
            if 'number_of_envelopes' in acq_dict:
                del acq_dict['number_of_envelopes']

    @timeout(5)
    def set_acquisition_wrapper(self, instrument, key, value):
        self._setinstr_with_tries(instrument, key,
                                  value, label='acquisition_',
                                  tries=3)
        return

    def _set_acquisition(self, acq_dict):
        self._validate_acq_dict(acq_dict)
        for key in acq_dict:
            self.set_adders += 1
            tlogger.info("Programming the acquisition setting %s to %s " %
                         (key, acq_dict[key]))
            try:
                self.set_acquisition_wrapper(
                    self.instr.acquisition, key, acq_dict[key])
            except gateway_helpers.TimeoutError:
                logger.error("Failed to write acquisition setting %s to %s " % (
                    key, acq_dict[key]), exc_info=True)
                tlogger.error("Failed to write acquisition setting %s to %s " % (
                    key, acq_dict[key]), exc_info=True)
                msg = "Failed to write acquisition setting %s to %s " % (
                    key, acq_dict[key])
                self._log_activity(msg, level='warning')
                raise WriteSettingsError
            except Exception:
                logger.error("Failed to write acquisition setting %s to %s " % (
                    key, acq_dict[key]), exc_info=True)
                tlogger.info("Failed to write acquisition setting %s to %s " % (
                    key, acq_dict[key]), exc_info=True)
                msg = "Failed to write acquisition setting %s to %s " % (
                    key, acq_dict[key])
                self._log_activity(msg, level='warning')
                raise WriteSettingsError

    @timeout(5)
    def set_trigger_wrapper(self, instrument, key, value):
        self._setinstr_with_tries(instrument, key,
                                  value, label='trigger_',
                                  tries=3)
        return

    @timeout(5)
    def set_trigger_edge_slope_wrapper(self, trigger, edge_slope):
        trigger.edge.slope = edge_slope
        return

    def set_trigger(self, trigger_dict):
        logger.debug("setting trigger")
        trigger = self.instr.trigger
        if trigger_dict['type'] == 'other':
            pass
        else:
            for key in trigger_dict:
                tlogger.info("Programming the trigger setting %s to %s " %
                             (key, trigger_dict[key]))
                try:
                    if key =='edge_slope':
                        self.set_trigger_edge_slope_wrapper(trigger, trigger_dict['edge_slope'])
                    else:
                        self.set_trigger_wrapper(trigger, key, trigger_dict[key])
                except gateway_helpers.TimeoutError:
                    logger.error("Failed to write trigger setting %s to %s " %
                                 (key, trigger_dict[key]), exc_info=True)
                    tlogger.info("Failed to write trigger setting %s to %s " %
                                 (key, trigger_dict[key]), exc_info=True)
                    msg = "Failed to write trigger setting %s to %s " % (
                        key, trigger_dict[key])
                    self._log_activity(msg, level='warning')
                    raise WriteSettingsError
                except Exception:
                    logger.error("Failed to write trigger setting %s to %s " %
                                 (key, trigger_dict[key]), exc_info=True)
                    tlogger.info("Failed to write trigger setting %s to %s " %
                                 (key, trigger_dict[key]), exc_info=True)
                    msg = "Failed to write trigger setting %s to %s " % (
                        key, trigger_dict[key])
                    self._log_activity(msg, level='warning')
                    raise WriteSettingsError

    @timeout(5)
    def set_standard_waveform_wrapper(self, standard_waveform, key, value):
        logger.debug("key is %s value is %s " % (key, value))
        self._setinstr(standard_waveform, key, value,
                       label='standard_waveform_')
        return

    @timeout(5)
    def standard_waveform_wrapper(self, index):
        return self.instr.outputs[index].standard_waveform

    def set_standard_waveform(self, waveform_dict, index=0):
        logger.debug("set standard_waveform")
        try:
            standard_waveform = standard_waveform_wrapper(index)
        except gateway_helpers.TimeoutError:
            logger.debug("Standard waveform failed", exc_info=True)
            tlogger.info("Standard waveform failed", exc_info=True)
        if not standard_waveform:
            logger.debug("no standard_waveform to set")
            return False

        for key in waveform_dict:
            try:
                self.set_standard_waveform_wrapper(
                    standard_waveform, key, waveform_dict[key])
                tlogger.info("Programming the standard waveform setting %s to %s " % (
                    key, waveform_dict[key]))
            except gateway_helpers.TimeoutError:
                logger.debug("Standard waveform setting failed", exc_info=True)
                tlogger.info("Standard waveform setting failed", exc_info=True)
        return True

    @timeout(5)
    def set_outputs_wrapper(self, output, key, value):
        self._setinstr(output, key, value, label='output_')
        return

    @timeout(5)
    def set_output_noise_enabled_wrapper(self):
        output.noise.enabled = self.ce_dict['output_noise']['enabled']
        return

    @timeout(5)
    def set_output_noise_percent_wrapper(self):
        output.percent.enabled = int(self.ce_dict['output_noise']['percent'])
        return

    def set_outputs(self, output_dict, index=0):
        logger.debug("set outputs")
        output = self.instr.outputs[index]
        for key in output_dict:
            try:
                self.set_outputs_wrapper(output, key, output_dict[key])
                tlogger.info("Programming the AFG output setting %s to %s " % (
                    key, output_dict[key]))
            except gateway_helpers.TimeoutError:
                logger.debug(
                    "Standard waveform outputs setting failed", exc_info=True)
                tlogger.info(
                    "Standard waveform outputs setting failed", exc_info=True)
        try:
            set_output_noise_enabled_wrapper()
            tlogger.info("Programming the output noise to enabled")
            if output.noise.enabled:
                try:
                    set_output_noise_percent_wrapper()
                    tlogger.info("Programming the output noise percentage to %s " %
                                 self.ce_dict['output_noise']['percent'])
                except gateway_helpers.TimeoutError:
                    logger.debug(
                        "Output noise percent setting failed", exc_info=True)
                    tlogger.info(
                        "Output noise percent setting failed", exc_info=True)
        except gateway_helpers.TimeoutError:
            logger.debug("Output noise setting failed", exc_info=True)
            tlogger.info("Output noise setting failed", exc_info=True)
        except Exception:
            logger.debug("failed to set output noise")
            logger.debug(traceback.format_exc())

    @timeout(5)
    def set_channels_settings_wrapper(self, ivi_channels, channel_idx, setting, value):
        self._setinstr(ivi_channels[channel_idx], setting, value)
        return

    def set_channels(self):
        """Sets the ivi channel data with values from the config

        ivi_channels refers to the ivi intrument.
        The method iterates over the channels in the config excerpt,
        aka the ce_dict, and assigns the channel data to the ivi
        channel object

        This does NOT set the Transformer 'channels' attribute as
        that refers to the channel data collected from the instrument
        rather than the data sent.
        """
        if not isinstance(self.ce_dict['channels'], list):
            logger.warning("set_channels() channels needs to be a list!")
            return
        logger.debug("set channels with ce_dict:%s" % self.ce_dict)
        if not self.ivi_channels:
            self.ivi_channels = self.instr.channels
        for channel in self.ce_dict['channels']:
            if not isinstance(channel, dict):
                logger.warning("Unexpected type for channel %s" % channel)
                continue
            enabled = channel['enabled']
            channel_idx = self.ch_idx_dict[channel['name']]
            logger.debug("%s enabled: %s" % (channel['name'], enabled))
            try:
                self.ivi_channels[channel_idx].enabled = enabled
                tlogger.info("Setting %s" % channel)
            except Exception as e:
                logger.debug("exception in setting channel enabled: %s" % e)
            except gateway_helpers.TimeoutError:
                logger.debug("Set channels enabled failed", exc_info=True)
                tlogger.info("Set channels enabled failed", exc_info=True)
            if enabled:
                for setting in self.channel_settings:
                    if setting not in channel:
                        continue
                    try:
                        self.set_channels_settings_wrapper(
                            self.instr.channels, channel_idx, setting, channel[setting])
                        #self._setinstr(self.instr.channels[channel_idx], setting, channel[setting])
                        tlogger.info("Programming the channel setting %s to %s " % (
                            setting, channel[setting]))
                    except gateway_helpers.TimeoutError:
                        logger.debug("Failed to write channel setting %s to %s " % (
                            setting, channel[setting]), exc_info=True)
                        tlogger.debug("Failed to write channel setting %s to %s " % (
                            setting, channel[setting]), exc_info=True)
                        msg = "Failed to write channel setting %s to %s " % (
                            setting, channel[setting])
                        self._log_activity(msg, level='warning')
                        raise WriteSettingsError
                    except Exception:
                        logger.debug("Failed to write channel setting %s to %s " % (
                            setting, channel[setting]), exc_info=True)
                        tlogger.debug("Failed to write channel setting %s to %s " % (
                            setting, channel[setting]), exc_info=True)
                        msg = "Failed to write channel setting %s to %s " % (
                            setting, channel[setting])
                        self._log_activity(msg, level='warning')
                        raise WriteSettingsError

    @timeout(5)
    def set_channels_enabled_wrapper(self, channel_idx):
        result = self.instr.channels[channel_idx].enabled
        return result

    def _set_enabled_list(self):
        self.enabled_list = []  # resets enabled list
        for ch in self.channel_names[:2]:
            if not self.check_instrument_ready():
                logger.warning("Instrument indicating not ready, ignoring")
            channel_idx = self.ch_idx_dict[ch]
            try:
                try:
                    wrapped_ch = self.set_channels_enabled_wrapper(channel_idx)
                    if not self.check_instrument_ready():
                        logger.warning("Instrument not ready, ignoring")
                except gateway_helpers.TimeoutError:
                    logger.debug("Set channels enabled failed", exc_info=True)
                    tlogger.info("Set channels enabled failed", exc_info=True)
                if wrapped_ch is True:
                    self.enabled_list.append(ch)
            except Exception:
                logger.debug("set enabled list %s", ch, exc_info=True)
                raise WriteSettingsError('enabled list')
        if self.capture_mode:
            for ch in self.enabled_list:
                channel = collections.defaultdict(int)
                channel['name'] = ch
                channel['enabled'] = True
                self._update_channels(self.ce_dict['channels'], channel)
        tlogger.info("Enabled list set to %s" % self.enabled_list)

    def _update_channels(self, channels, channel_data):
        """Updates the channels with the data in channel_data

        Checks for a matching channel in channels according to
        the name of the channel. If found, updates the channel.
        If not found, the channel_data is appended to channels.
        """
        new_channel_flag = True
        # the name key is required for channel data
        if 'name' not in channel_data:
            return
        for channel in channels:
            if 'name' in channel and channel['name'] == channel_data['name']:
                channel.update(channel_data)
                new_channel_flag = False
        # If it's a new channel, append the channel data
        if new_channel_flag:
            channels.append(channel_data)

    def check_commands_completed(self):
        self.logger.debug("check_commands_completed() asking *ESR")
        try:
            r = self.instr._ask("*ESR?")
            self.logger.debug("*ESR response: {}".format(r))
        except Exception as e:
            self.logger.debug("*ESR exc: {}".format(e))
        # r = self.instr._ask("allev?")
        # self.logger.info("allev? response: %s" % r)

    def check_instrument_ready(self):
        """Checks if instrument is ready to run a new command

        Assumes the instrument is 'busy'. Method asks the instrument
        up to 10 times if the instrument is busy. If the ask() returns
        '0' then the instrument is ready to do something else and this
        method will return True. If after 10 tries it still is not
        returning '0' or if there is some exception then this method
        returns False.
        """
        ready = False

        for i in range(20):
            self.timer.set_timeout(3)
            busy = ''
            try:
                busy = self.instr._ask('busy?')
                tlogger.info("Busy reading is %s" % busy)
            except Exception as e:
                tlogger.warning("Exception checking busy status %s" % e)
            self.timer.clear_timeout()
            if busy == '0':
                ready = True
                break
            if self.is_unit_test:
                tlogger.info("Unit testing, assuming instrument ready")
                return True
            time.sleep(0.5)
        tlogger.info("Instrument ready? %s" % ready)
        return ready

    def _handle_pods(self):
        """Handles pods for digital data

        Called by fetch_measurements. Inherited classes can override
        this method to handle pods, otherwise this will just return None
        """
        return None

    def fetch_measurements(self):
        """Fetches trace, metadata, screenshot, and measurements"""
        # if the config had frames, this should be skipped
        if "frames" in self.config:
            return
        logger.debug("fetching measurements")
        self.times['fetch_measurements_start'] = time.clock()
        # check to return early if instrument is not ready
        tlogger.info("pre set enabled list instrument check")
        self._set_enabled_list()
        self.time_step = 0.000001
        self.trace_dict['start_tse'] = int(dt2ms(datetime.datetime.now()))
        logger.debug("enabled_list: %s" % self.enabled_list)

        # check to return early if instrument is not ready
        if not self.check_instrument_ready():
            tlogger.warning("Instrument not ready, ignoring and moving on")

        # Fetch the waveform for each channel enabled
        tlogger.info("Fetching analog waveforms for all enabled channels")
        for ch in self.enabled_list:
            if ch in self._analog_channel_names:
                self._fetch_waveform(ch)

        # TODO: add dlogging
        self._handle_pods()

        # Write the dictionary of trace data to file
        tracefile = 'trace-tmp.json'
        msg = ("Writing the waveform to a file")
        tlogger.info((msg).rjust(len(msg) + 9))
        self._write_trace_dict(filename=tracefile)

        # intialize the metadata from channels after waveform fetch
        self.metadata = self._get_metadata(
            channels=self.channels,
            filename=tracefile,
        )
        tmp = self._get_metadata(
            channels=self.channels,
            filename=tracefile,
        )
        inst_settings = self._get_instrument_settings()
        # self.metadata.update(self.get_instrument_settings())
        self.metadata.update(tmp)
        self.metadata.update(inst_settings)

        # Make quick post for first feedback
        self._quick_post_results()

        # Grab a screenshot from the instrument
        try:
            self._grab_and_post_screenshot()
        except FetchScreenshotError:
            logger.warning("FetchScreenshotError! Continuing run")
            tlogger.error("Screenshot failed")
        else:
            msg = "Screenshot posted successfully"
            tlogger.info("Screenshot posted successfully")
        # Run measurements on each channel
        try:
            self._fetch_waveform_measurements()
        except FetchMeasurementError:
            raise
        self.times['fetch_measurements_end'] = time.clock()
        return self.trace_dict

    @timeout(1000)
    def fetch_waveform_wrapper(self, ivi_channel):
        result = list(ivi_channel.measurement.fetch_waveform())
        return result

    @timeout(5)
    def ch_data_wrapper(self, ivi_channel, attr_name):
        result = getattr(ivi_channel, attr_name)
        return result

    def _fetch_waveform(self, channel_name):
        """Gets the waveform data from the instrument

        This is the method that actually fetches the data from the
        ivi channel instance for the waveform and channel metadata
        for a given trace.

        This is the method that intializes the channel for the
        drivers channels list for storing the data collected
        for each channel enabled on the scope.
        """
        logger.debug("ScopeTransformer:_fetch_waveform ...")
        self.check_commands_completed()  # check if ready
        channel_idx = self.ch_idx_dict[channel_name]
        try:
            ivi_channel = self.instr.channels[channel_idx]
        except KeyError:
            logger.warning("KeyError in _fetch_waveform with {}"
                           .format(channel_name))
        except Exception as e:
            logger.warning("Unexpected error getting ivi channel {}: {}"
                           .format(channel_name, e))
            raise ReadSettingsError('channel error {}'.format(channel_name))
        try:
            msg = ("Fetching analog waveform for %s" % channel_name)
            tlogger.info((msg).rjust(len(msg) + 9))
            waveform = self.fetch_waveform_wrapper(ivi_channel)
        except gateway_helpers.TimeoutError:
            logger.debug("Fetch waveform failed (TimeoutError)")
            tlogger.info("Fetch waveform failed (TimeoutError)")
            msg = "Fetch waveform failed for %s " % channel_name
            self._log_activity(msg, level='warning')
            raise FetchWaveformError('TimeoutError on channel {}'.format(channel_name))
        except Exception as e:
            self.looger.error('generic scope channel {} error {}'.format(channel_name, e))
            self.logger.warning("failed to fetch waveform for: %s"
                                % channel_name, exc_info=True)
            tlogger.info("failed to fetch waveform for: %s" % channel_name)
            msg = "Fetch waveform failed for %s " % channel_name
            self._log_activity(msg, level='warning')
            raise FetchWaveformError('channel {} error {}'.format(channel_name, e))
        self.waveform_length = len(waveform)
        if self.waveform_length == 0:
            tlogger.error("No waveform data acquired (length 0)")
            # msg = "Capture Failed, No Waveform Captured. Confirm Setup and Try Again"
            # self._log_activity(msg, level='warning')
            raise FetchWaveformError
        logger.debug("waveform length for %s: %s" %
                     (channel_name, self.waveform_length))
        time_step = waveform[1][0] - waveform[0][0]
        msg = "Waveform acquired successfully for {}".format(channel_name)
        self._log_activity(msg)
        voltage_list = self.get_voltage_list(waveform)
        slice_list = self.get_slice_list(voltage_list)
        logger.debug("ScopeTransformer: line(slice list) = %d" %
                     len(slice_list))
        self.slice_dict[channel_name] = slice_list
        if slice_list:
            self.first_slice[channel_name] = slice_list[0]
        self.check_commands_completed()
        channel_data = {
            'name': channel_name,
            'y_values': voltage_list,
            'time_step': time_step,
            'start_time': waveform[0][0],
            'end_time': waveform[-1][0],
            'enabled': True,
        }
        msg = ("Successful waveform capture: length for channel %s is %s" %
               (channel_data['name'], len(channel_data['y_values'])))
        tlogger.info((msg).rjust(len(msg) + 9))
        # collect channel metadata for plotting
        ch_metadata_list = ['trigger_level', 'position', 'range', 'coupling',
                            'offset', 'scale']
        for attr_name in ch_metadata_list:
            if not hasattr(ivi_channel, attr_name):
                # skip channel attributes that are not available
                continue
            try:
                channel_data[attr_name] = self.ch_data_wrapper(
                    ivi_channel, attr_name)
                msg = ("Plotting metadata info: channel {} is {}"
                       .format(attr_name, channel_data[attr_name]))
                tlogger.info((msg).rjust(len(msg) + 9))
            except gateway_helpers.TimeoutError:
                logger.debug("Getting plot metadata failed", exc_info=True)
                tlogger.info("Getting plot metadata failed", exc_info=True)
                msg = "Failed to read plot metadata %s " % attr_name
                self._log_activity(msg, level='warning')
                raise ReadSettingsError
            except Exception:
                logger.debug("collecting channel plot metadata: {}: {}"
                             .format(attr_name, ivi_channel), exc_info=True)
                tlogger.info("Exception getting plotting metadata info for "
                             "channel attribute: {}".format(attr_name))
                msg = "Failed to read plot metadata %s " % attr_name
                self._log_activity(msg, level='warning')
                raise ReadSettingsError

        # index here is the ivi index number for the channel
        try:
            channel_data['index'] = self.ch_idx_dict[channel_name]
        except Exception:
            logger.debug("collecting channel plot metadata: name: %s",
                         ivi_channel, exc_info=True)

        # update current channels list
        self._update_channels(self.channels, channel_data)
        self.time_step = time_step  # migrate towards ch specific

    def _fetch_waveform_digital(self, channel_name):
        """Gets the waveform data from the instrument

        This is the method that actually fetches the data from the
        ivi channel instance for the waveform and channel metadata
        for a given trace.

        This is the method that intializes the channel for the
        drivers channels list for storing the data collected
        for each channel enabled on the scope.
        """
        self.check_commands_completed()  # check if ready
        try:
            waveform = self.instr.measurement.fetch_waveform_digital(
                channel_name)
        except Exception:
            self.logger.warning("failed to fetch digial waveform for: {}"
                                .format(channel_name), exc_info=True)
            return

        self.waveform_length = len(waveform)
        logger.debug("waveform length for {}: {}"
                     .format(channel_name, self.waveform_length))
        try:
            time_step = waveform[1][0] - waveform[0][0]
        except IndexError:
            logger.warning("IndexError reading timestep from digital "
                           "waveform: {};".format(waveform))
            return
        voltage_list = self.get_voltage_list(waveform)
        slice_list = self.get_slice_list(voltage_list)
        self.slice_dict[channel_name] = slice_list
        if slice_list:
            self.first_slice[channel_name] = slice_list[0]
        try:
            self.check_commands_completed()
        except Exception as e:
            logger.warning("Unexpected exception: {} when calling "
                           "check_commands_completed".format(e))
        channel_data = {
            'name': channel_name,
            'y_values': voltage_list,
            'time_step': time_step,
            'start_time': waveform[0][0],
            'end_time': waveform[-1][0],
            'enabled': True,
        }
        try:
            self._update_channels(self.channels, channel_data)
        except KeyError:
            logger.warning("KeyError when calling _update_channels()")
        except IndexError:
            logger.warning("IndexError when calling _update_channels()")

        self.time_step = time_step  # migrate towards ch specific time_step

    @timeout(20)
    def fetch_waveform_measurement_wrapper(self, measurement, ivi_name):
        return measurement.fetch_waveform_measurement(ivi_name)

    def _fetch_channel_ivi_measurements(self, channel):
        """Fetches ivi measurements for a given channel

        Summary:
            The ivi measurements about the waveform and NOT the
            waveform itself and NOT calculations GradientOne
            performs on the waveform.

        Parameters:
            channel: a dictionary containing channel data,
                most importantly channel['ivi'] that has the
                ivi channel object

        Raises:
            - gateway_helpers.TimeoutError
            - FetchMeasurementError

        Returns: None
        """
        if channel['name'] in self._digital_channel_names:
            self.meas_list_copy = copy.deepcopy(self.meas_list_digital)
        else:
            self.meas_list_copy = copy.deepcopy(self.meas_list)
        logger.info("initial len of meas list copy for channel %s %s" % (len(self.meas_list_copy), channel['name']))
        for meas in self.meas_list_copy:
            # Skip if simulated (meas_list should be empty anyway)
            measurement = channel['ivi'].measurement
            ivi_name = meas['ivi_name']
            val = None
            try:
                val = self.fetch_waveform_measurement_wrapper(
                    measurement=measurement,
                    ivi_name=ivi_name,
                )
            except gateway_helpers.TimeoutError:
                for i in self.meas_list_copy[:]:
                    if 'val' not in i:
                        self.meas_list_copy.remove(i)
                    if len(self.meas_list_copy) == 0:
                        channel['waveform_measurements_valid'] = False
                channel['waveform_measurements'] = self.meas_list_copy
                msg = ("Failed to read channel measurement {}"
                       .format(ivi_name))
                self._log_activity(msg, level='warning')
                raise
            except Exception:
                logger.debug("measurement exception %s" % ivi_name,
                             exc_info=True)
                msg = ("Failed to read channel measurement {}"
                       .format(ivi_name))
                self._log_activity(msg, level='warning')
                raise FetchMeasurementError(ivi_name)
            logger.debug("%s, %s" % (ivi_name, val))
            msg = ("%s, %s" % (ivi_name, val))
            tlogger.info((msg).rjust(len(msg) + 9))
            if val == 'measurement error':
                val = 'N/A'
                msg = ("Ivi returned 'measurement error' for channel "
                       "measurement {}, saving as N/A".format(ivi_name))
                self._log_activity(msg, level='warning')
            elif val > settings.MAX_VALID_MEAS_VAL:
                val = settings.MAX_VALID_MEAS_VAL
            else:
                pass
            meas['value'] = val
            self.check_commands_completed()

    # @timeout(60)
    def _fetch_waveform_measurements(self):
        """Fetches measurments about the waveform

        Note for emphasis: Measurements in this case refers to the
        ivi measurements about the waveform and NOT the waveform
        itself and NOT calculations GradientOne performs on the
        waveform.
        """
        self.check_commands_completed()
        logger.debug("fetching waveform measurements")
        tlogger.info("Fetching waveform measurements")
        if settings.SIMULATED:
            return
        if not self.ivi_channels:
            self.ivi_channels = self.instr.channels
        for channel in self.metadata['channels']:
            ch_idx = self.ch_idx_dict[channel['name']]
            ivi_channel = self.ivi_channels[ch_idx]
            channel['ivi'] = ivi_channel
            channel['waveform_measurements_valid'] = True  # starts off valid
            try:
                self._fetch_channel_ivi_measurements(channel)
            except gateway_helpers.TimeoutError:
                continue  # logging handled in _fetch_channel_ivi_measurements
            else:
                channel['waveform_measurements'] = self.meas_list_copy
                self._log_activity("Measurements acquired successfully for {}"
                                   .format(channel['name']))

    def fetch_screenshot(self):
        """Fetches a screenshot and sends it to the server

        This creates its own result and is only used for a simple
        verification. No waveform data is associated beyond just
        the image
        """
        self.logger.info("fetch_screenshot test")
        if settings.SIMULATED:
            return
        file_key = "screenshot-" + self.command['id'] + ".png"
        pngfile = self._send_fetch_screenshot_cmd(file_key)
        if self.is_unit_test:
            logger.info("skipping transmit_file() call in fetch_screenshot() "
                        "for pngfile with file_key: {}".format(file_key))
            return
        else:
            response = self.transmit_file(pngfile, file_key=file_key,
                                          category='fetch_screenshot',
                                          command_id=self.command['id'])
        result_id = ''
        try:
            result_id = json.loads(response.text)['result']['id']
        except TypeError:
            # likely due to nothing in response text
            logger.debug("TypeError in fetch_screenshot response")
        except ValueError:
            # likely due to invalid json in response
            logger.debug("ValueError in fetch_screenshot response")
        except KeyError:
            # valid json response, but missing result or id
            logger.debug("KeyError in fetch_screenshot response")
        except Exception as e:
            logger.debug("unexpected exception {}".format(e), exc_info=True)
        # update the command to complete so that the server knows
        # that the screenshot is ready
        url = BASE_URL + '/commands'
        data = {
            'id': self.command['id'],
            'status': 'complete',
            'results': [{'result_id': result_id}],
        }
        self.put(url, data)

        # The following are not required for a simple screenshot
        # but are used for a typical trace result that requires
        # all the metadata and full result object
        self.screenshot_blob_key = response.text
        screenshot_url = BASE_URL + '/download?file_key=' + file_key
        self.metadata['scope_screenshot_url'] = screenshot_url
        self.metadata['result_id'] = 'RESULT_ID_PLACEHOLDER'
        self.trace_dict['screenshot_blob_key'] = response.text
        self.trace_dict['scope_screenshot_url'] = screenshot_url

    @timeout(5)
    def _send_fetch_screenshot_wrapper(self):
        result = self.instr.display.fetch_screenshot()
        return result

    def _send_fetch_screenshot_cmd(self, file_key):
        """Sends fetch screenshot command to instrument

        This method calls ivi.display.fetch_screenshot function,
        however, some manufacturers like Keysight do not have
        this and will need to have this method overridden.
        """
        try:
            png = self._send_fetch_screenshot_wrapper()
            msg = "Screenshot acquired successfully"
            self._log_activity(msg)
        except gateway_helpers.TimeoutError:
            logger.debug("exception in _send_fetch_screenshot_cmd {}"
                         .format(file_key), exc_info=True)
            raise ReadSettingsError
        except Exception:
            logger.error("exception in _send_fetch_screenshot_cmd {}"
                         .format(file_key), exc_info=True)
            raise ReadSettingsError
        pngfile = os.path.join(TMPDIR, file_key)
        with open(pngfile, 'wb') as f:
            f.write(png)
        return pngfile

    @timeout(5)
    def get_trigger_wrapper(self, name):
        result = getattr(self.instr.trigger, name)
        return result

    def get_trigger(self):
        logger.debug("getting trigger")
        tlogger.info("Getting trigger data from the instrument")
        trigger_dict = {
            'type': '',
            'coupling': '',
            'source': '',
            'level': '',
            'holdoff': '',
            'edge_slope': '',
        }
        trigger_type = self.get_trigger_wrapper('type')
        if trigger_type == 'edge':
            trigger_dict['type'] = 'edge'
            msg = ("Trigger setting type is edge ")
            tlogger.info((msg).rjust(len(msg)+9))
            for name in trigger_dict:
                try:
                    if name == 'type':
                        pass
                    elif name =='edge_slope':
                        trigger_dict[name] = self.instr.trigger.edge.slope
                    else:
                        trigger_dict[name] = self.get_trigger_wrapper(name)
                except gateway_helpers.TimeoutError:
                    logger.debug("exception in reading trigger setting %s" % name,
                                 exc_info=True)
                    msg = "Failed to read trigger setting {}".format(name)
                    self._log_activity(msg, level='warning')
                    raise ReadSettingsError
                    break
                except Exception:
                    logger.error("exception in reading trigger setting %s" % name,
                                 exc_info=True)
                    msg = "Failed to read trigger setting {}".format(name)
                    self._log_activity(msg, level='warning')
                    raise ReadSettingsError
                msg = ("Trigger setting %s is %s " % (name, trigger_dict[name]))
                tlogger.info((msg).rjust(len(msg)+9))
        else:
            trigger_dict['type'] = 'other'
        return trigger_dict

    @timeout(5)
    def get_acquisition_wrapper(self, name):
        result = getattr(self.instr.acquisition, name)
        return result

    def get_acquisition(self):
        logger.debug("getting acquisition")
        if self.capture_mode:
            tlogger.info("38.  Getting acquisition data from the instrument")
        else:
            tlogger.info("23.  Getting acquisition data from the instrument")
        for key in self.acq_dict:
            try:
                self.acq_dict[key] = self.get_acquisition_wrapper(key)
                msg = ("Acquisition setting %s is %s " %
                       (key, self.acq_dict[key]))
                tlogger.info((msg).rjust(len(msg) + 9))
            except gateway_helpers.TimeoutError:
                logger.debug("exception in reading acquisition setting: %s" % key,
                             exc_info=True)
                msg = "Failed to read acquisition setting {}".format(key)
                self._log_activity(msg, level='warning')
                raise ReadSettingsError
            except Exception:
                logger.error("exception in reading acquisition setting: %s" % key,
                             exc_info=True)
                tlogger.error("exception in reading acquisition setting: %s" % key,
                              exc_info=True)
                msg = "Failed to read acquisition setting {}".format(key)
                self._log_activity(msg, level='warning')
                raise ReadSettingsError
        return self.acq_dict

    @timeout(5)
    def get_standard_waveform_wrapper(self, index):
        result = self.instr.outputs[index].standard_waveform
        return result

    @timeout(5)
    def get_standard_waveform_settings_wrapper(self, standard_waveform, key):
        result = getattr(standard_waveform, key)
        return result

    def get_standard_waveform(self, index=0):
        logger.debug("getting standard_waveform")
        try:
            standard_waveform = self.get_standard_waveform_wrapper(index)
        except gateway_helpers.TimeoutError:
            logger.debug("exception in timeout get std waveform",
                         exc_info=True)
        std_wave_dict = {
            'waveform': '',
            'frequency': '',
            'amplitude': '',
            'dc_offset': '',
            'duty_cycle_high': '',
            'start_phase': '',
            'pulse_width': '',
            'symmetry': '',
        }
        if standard_waveform:
            for key in std_wave_dict:
                try:
                    std_wave_dict[key] = self.get_standard_waveform_settings_wrapper(
                        standard_waveform, key)
                except gateway_helpers.TimeoutError:
                    logger.debug("exception in timeout get std waveform settings",
                                 exc_info=True)
        else:
            logger.debug("no standard_waveform object")
            logger.debug("outputs[0] dir: %s" % dir(self.instr.outputs[0]))
        return std_wave_dict

    @timeout(5)
    def get_outputs_wrapper(self, index):
        result = self.instr.outputs[index]
        return result

    @timeout(5)
    def get_output_settings_wrapper(self, outputs, key):
        result = getattr(outputs, key)
        return result

    def get_outputs(self, index=0):
        logger.debug("getting outputs")
        outputs = None
        try:
            outputs = self.get_outputs_wrapper(index)
        except Exception:
            logger.debug("getting outputs exception")
        except gateway_helpers.TimeoutError:
            logger.debug("exception in timeout get outputs",
                         exc_info=True)
        output_dict = {
            'impedance': '',
            'enabled': '',
        }
        if not outputs:
            return output_dict

        for key in output_dict:
            try:
                output_dict[key] = self.get_output_settings_wrapper(
                    outputs, key)
                logger.debug("output from instr: %s %s" %
                             (key, output_dict[key]))
            except gateway_helpers.TimeoutError:
                logger.debug("exception in timeout get output settings",
                             exc_info=True)
        standard_waveform_dict = self.get_standard_waveform()
        self.ce_dict['outputs_noise_percent'] = outputs.noise.percent
        return output_dict, standard_waveform_dict

    @timeout(10)
    def _channel_enabled_wrapper(self, ivi_channels, ch_idx):
        result = self.ivi_channels[ch_idx].enabled
        return result

    @timeout(5)
    def channel_range_wrapper(self, ivi_channels, ch_idx):
        result = self.ivi_channels[ch_idx].range
        return result

    @timeout(5)
    def channel_position_wrapper(self, ivi_channels, ch_idx):
        result = self.ivi_channels[ch_idx].position
        return result

    @timeout(5)
    def channel_coupling_wrapper(self, ivi_channels, ch_idx):
        result = self.ivi_channels[ch_idx].coupling
        return result

    @timeout(5)
    def channel_scale_wrapper(self, ivi_channels, ch_idx):
        result = self.ivi_channels[ch_idx].scale
        return result

    @timeout(5)
    def channel_input_impedance_wrapper(self, ivi_channels, ch_idx):
        result = self.ivi_channels[ch_idx].input_impedance
        return result

    @timeout(5)
    def channel_offset_wrapper(self, ivi_channels, ch_idx):
        result = self.ivi_channels[ch_idx].offset
        return result

    def _get_excerpt_channel_data(self):
        """updates config exerpt to match instrument reported channel enabled,
           offset, range, and coupling. Updates enabled list to match
           instrument reported enabled channels. Returns copy of updated
           config excerpt"""
        logger.debug("updating config_excerpt, requesting channels")
        if not self.ivi_channels:
            self.ivi_channels = self.instr.channels
        config_excerpt = copy.deepcopy(self.ce_dict)
        self.enabled_list = []
        channels = []
        tlogger.info("Getting channel data from the instrument")
        for channel in self.ce_dict['channels']:
            ch = channel['name']
            ch_dict = collections.defaultdict(str)
            logger.debug("requesting channel enabled data for %s" % ch)
            ch_idx = self.ch_idx_dict[ch]
            try:
                ch_dict['enabled'] = self._channel_enabled_wrapper(
                    self.ivi_channels, ch_idx)
            except gateway_helpers.TimeoutError:
                logger.debug("exception in timeout check channel enabled for %s" % ch,
                             exc_info=True)
                raise
            except Exception:
                logger.error("channel enablement exception %s" % ch,
                             exc_info=True)
                raise ReadSettingsError
            time.sleep(0.1)
            if ch_dict['enabled']:
                logger.debug("response %s enabled" % ch)
                ch_dict['name'] = self.ivi_channels[ch_idx].name
                if ch in self._analog_channel_names:
                    msg = ("Getting channel data for %s " % ch)
                    tlogger.info((msg).rjust(len(msg) + 9))
                    try:
                        ch_dict['range'] = self.channel_range_wrapper(
                            self.ivi_channels, ch_idx)
                    except gateway_helpers.TimeoutError:
                        logger.debug("exception in timeout channel range for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel range for %s" % ch,
                                      exc_info=True)
                        msg = "Failed to get channel range for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    except Exception:
                        logger.debug("exception in timeout channel range for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel range for %s" % ch,
                                      exc_info=True)
                        msg = "Failed to get channel range for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    time.sleep(0.1)
                    try:
                        ch_dict['scale'] = self.channel_scale_wrapper(
                            self.ivi_channels, ch_idx)
                    except gateway_helpers.TimeoutError:
                        logger.debug("exception in timeout channel scale for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel scale for %s" % ch,
                                      exc_info=True)
                        msg = "Failed to get channel scale for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    except Exception:
                        logger.debug("exception in timeout channel scale for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel scale for %s" % ch,
                                      exc_info=True)
                        msg = "Failed to get channel scale for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    time.sleep(0.1)
                    try:
                        if hasattr(self.ivi_channels[ch_idx], 'position'):
                            ch_dict['position'] = self.channel_position_wrapper(
                                self.ivi_channels, ch_idx)
                    except gateway_helpers.TimeoutError:
                        logger.debug("exception in timeout channel position for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel position for %s" % ch,
                                      exc_info=True)
                        msg = "Failed to get channel position for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    except Exception:
                        logger.debug("exception in timeout channel position for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel position for %s" % ch,
                                      exc_info=True)
                        msg = "Failed to get channel position for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    time.sleep(0.1)
                    try:
                        ch_dict['coupling'] = self.channel_coupling_wrapper(
                            self.ivi_channels, ch_idx)
                    except gateway_helpers.TimeoutError:
                        logger.debug("exception in timeout channel coupling for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel coupling for %s" % ch,
                                      exc_info=True)
                        msg = "Failed to get channel coupling for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    except Exception:
                        logger.debug("exception in timeout channel coupling for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel coupling for %s" % ch,
                                      exc_info=True)
                        msg = "Failed to get channel coupling for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    time.sleep(0.1)
                    try:
                        ch_dict['input_impedance'] = self.channel_input_impedance_wrapper(
                            self.ivi_channels, ch_idx)
                    except gateway_helpers.TimeoutError:
                        logger.debug("exception in timeout channel input impedance for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel input impedance for %s" % ch,
                                      exc_info=True)
                        msg = "Failed to get channel input impedance for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    except Exception:
                        logger.debug("exception in timeout channel input impedance for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel input impedance for %s" % ch,
                                      exc_info=True)
                        msg = "Failed to get channel input impedance for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    time.sleep(0.1)
                    try:
                        ch_dict['offset'] = self.channel_offset_wrapper(
                            self.ivi_channels, ch_idx)
                    except gateway_helpers.TimeoutError:
                        logger.debug("exception in timeout channel offset for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel offset for %s" % ch,
                                      exc_info=True)
                        msg = "Failed to get channel offset for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    except Exception:
                        logger.debug("exception in timeout channel offset for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel offset for %s" % ch,
                                      exc_info=True)
                        msg = "Failed to get channel offset for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    time.sleep(0.1)
                if ch not in self.enabled_list:
                    self.enabled_list.append(ch)
            else:
                logger.debug("response: %s NOT enabled" % ch)
                msg = ("%s NOT enabled" % ch)
                tlogger.info((msg).rjust(len(msg) + 9))
            self._update_channels(channels, ch_dict)
        config_excerpt['channels'] = channels
        # sync up excerpt list with driver list
        self.ce_dict['enabled_list'] = self.enabled_list
        config_excerpt['enabled_list'] = self.enabled_list
        tlogger.info("Enabled channel list is %s " %
                     config_excerpt['enabled_list'])
        return config_excerpt

    def _get_optional_features(self):
        """To be overridden for each instruments optional features"""
        pass

    def _load_optional_features(self):
        """To be overridden for each instruments optional features"""
        pass

    def get_config_excerpt(self):
        logger.debug("getting config_excerpt")
        config = self._get_base_config_excerpt()
        extras = self._get_config_excerpt_extras()
        if 'optional features' in self.command['info']:
            extras = self._get_optional_features(extras)
        config.update(extras)
        logger.info("get config excerpt is %s" % config)
        return config

    def _get_base_config_excerpt(self):
        """Get config excerpt fields common to all scopes"""
        try:
            config_excerpt = self._get_excerpt_channel_data()
        except Exception:
            logger.error('Error reading config excerpt', exc_info=True)
            tlogger.error("Error reading config excerpt", exc_info=True)
            raise base.ReadSettingsError(kind='channel_data')
        try:
            config_excerpt['trigger'] = self.get_trigger()
        except Exception:
            logger.warning("trigger error", exc_info=True)
            raise base.ReadSettingsError(kind='trigger')
        try:
            config_excerpt['acquisition'] = self.get_acquisition()
        except Exception:
            logger.warning("acquisition error", exc_info=True)
            raise base.ReadSettingsError(kind='acquisition')
        return config_excerpt

    def _get_config_excerpt_extras(self):
        """Get fields beyond the base config excerpt"""
        extras = {}
        extras['timebase'] = self.get_timebase()
        return extras

    def get_timebase(self):
        logger.debug("getting timebase")
        if self.capture_mode == True:
            tlogger.info("39.  Getting timebase data from the instrument")
        else:
            tlogger.info("24.  Getting timebase data from the instrument")
        timebase = collections.defaultdict(int)
        try:
            timebase['position'] = self.timebase_position_wrapper()
        except gateway_helpers.TimeoutError:
            logger.debug("get timebase position exception", exc_info=True)
            tlogger.debug("get timebase position exception", exc_info=True)
            msg = "Failed to read timebase setting:  position setting"
            self._log_activity(msg, level='warning')
            raise ReadSettingsError
        except Exception:
            logger.debug("get timebase position exception", exc_info=True)
            tlogger.debug("get timebase position exception", exc_info=True)
            msg = "Failed to read timebase setting:  position setting"
            self._log_activity(msg, level='warning')
            raise ReadSettingsError
        return timebase

    def get_probe_ids(self, total_channels=2):
        logger.debug("getting probe_ids")
        probe_ids = []
        if not self.ivi_channels:
            self.ivi_channels = self.instr.channels
        for i in range(total_channels):
            probe_ids.append(self.ivi_channels[i].probe_id)
        return probe_ids

    def get_voltage_list(self, waveform=[]):
        logger.debug("getting voltage_list")
        voltage_list = [round_sig(float(point[1])) for point in waveform]
        return voltage_list

    def get_voltage_digital_list(self, waveform=[]):
        logger.debug("getting voltage_list for digital waveforms")
        voltage_list = [point[1] for point in waveform]
        return voltage_list

    def get_slice_list(self, voltage_list=[]):
        """create list of slices sets class attribute"""
        logger.debug("getting slice_list")
        max_len = int(settings.MAX_LENGTH_FOR_BROWSER)
        if len(voltage_list) >= max_len:
            slice_list = [voltage_list[x:x + max_len]
                          for x in range(0, len(voltage_list), max_len)]
        else:
            slice_list = [voltage_list]
        return slice_list

    @timeout(5)
    def timebase_range_wrapper(self):
        result = self.instr.timebase.range
        return result

    @timeout(5)
    def timebase_position_wrapper(self):
        result = self.instr.timebase.position
        return result

    @timeout(5)
    def timebase_scale_wrapper(self):
        result = self.instr.timebase.scale
        return result

    def _get_instrument_settings(self):
        """Instrument settings that are channel independent

        Separate from the config excerpt
        """
        settings = {}
        try:
            settings['h_divs'] = self.get_horizontal_divisions()
            msg = ("Horizontal divisions are:  %s " % settings['h_divs'])
            tlogger.info((msg).rjust(len(msg) + 9))
        except Exception:
            logger.debug(
                "collecting channel independent settings: horizontal divisions", exc_info=True)
            tlogger.info("Exception while getting horizontal divisions")
        try:
            settings['v_divs'] = self.get_vertical_divisions()
            msg = ("Vertical divisions are:  %s " % settings['v_divs'])
            tlogger.info((msg).rjust(len(msg) + 9))
        except Exception:
            logger.debug(
                "collecting channel independent settings: vertical divisions", exc_info=True)
            tlogger.info("Exception while getting vertical divisions")
        try:
            settings['timebase_range'] = self.timebase_range_wrapper()
            msg = ("Timebase range is  %s " % settings['timebase_range'])
            tlogger.info((msg).rjust(len(msg) + 9))
        except gateway_helpers.TimeoutError:
            logger.debug(
                "Exception in collecting channel independent settings: timebase_range", exc_info=True)
            msg = "Failed to collect channel independent settings: timebase_range"
            self._log_activity(msg, level='warning')
            raise ReadSettingsError
        except Exception:
            logger.debug(
                "collecting channel independent settings: timebase_range", exc_info=True)
            tlogger.info("Exception while getting timebase range")
            msg = "Failed to collect channel independent settings: timebase_range"
            self._log_activity(msg, level='warning')
            raise ReadSettingsError
        try:
            settings['timebase_position'] = self.timebase_position_wrapper()
            msg = ("Timebase position is  %s " % settings['timebase_position'])
            tlogger.info((msg).rjust(len(msg) + 9))
        except gateway_helpers.TimeoutError:
            logger.debug(
                "Exception in collecting channel independent settings: timebase_position", exc_info=True)
            tlogger.info("Exception while getting timebase position")
            msg = "Failed to collect channel independent settings: timebase_position"
            self._log_activity(msg, level='warning')
            raise ReadSettingsError
        except Exception:
            logger.debug(
                "Exception in collecting channel independent settings: timebase_position", exc_info=True)
            tlogger.info("Exception while getting timebase position")
            msg = "Failed to collect channel independent settings: timebase_position"
            self._log_activity(msg, level='warning')
            raise ReadSettingsError
        try:
            settings['timebase_scale'] = self.timebase_scale_wrapper()
            msg = ("Timebase scale is  %s " % settings['timebase_scale'])
            tlogger.info((msg).rjust(len(msg) + 9))
        except gateway_helpers.TimeoutError:
            logger.debug(
                "Exception in collecting channel independent settings: timebase_scale", exc_info=True)
            tlogger.info("Exception while getting timebase scale")
            msg = "Failed to collect channel independent settings: timebase_scale"
            self._log_activity(msg, level='warning')
            raise ReadSettingsError
        except Exception:
            logger.debug(
                "Exception in collecting channel independent settings: timebase_scale", exc_info=True)
            tlogger.info("Exception while getting timebase scale")
            msg = "Failed to collect channel independent settings: timebase_scale"
            self._log_activity(msg, level='warning')
            raise ReadSettingsError
        return settings

    def _grab_and_post_screenshot(self):
        logger.debug("_grab_and_post_screenshot")
        file_key = "screenshot-" + self.metadata['result_id']
        try:
            self.timer.set_timeout(12)
            pngfile = self._send_fetch_screenshot_cmd(file_key)
            self.timer.clear_timeout()
            msg = "Fetched screenshot successfully"
            tlogger.info(msg)
        except gateway_helpers.TimeoutError:
            logger.debug("Timeout in  _grab_and_post_screenshot for {}"
                         .format(file_key), exc_info=True)
        except Exception:
            msg = "Screenshot unavailable"
            tlogger.error(msg)
            self._log_activity(msg, level='warning')
            raise FetchScreenshotError("screenshot unavailable")
        if self.is_unit_test:
            logger.info("unit test, _grab_and_post_screenshot skipping call "
                        "to transmit_file() w/ file_key: {}".format(file_key))
            blob_key = "dummy blob_key for {}".format(file_key)
        else:
            response = self.transmit_file(pngfile, file_key=file_key)
            blob_key = response.text
        self.screenshot_blob_key = blob_key
        self.trace_dict['screenshot_blob_key'] = blob_key
        screenshot_url = (BASE_URL + '/download?file_key=' + file_key)
        self.metadata['scope_screenshot_url'] = screenshot_url
        self.trace_dict['scope_screenshot_url'] = screenshot_url
        data = {'id': self.metadata['result_id'],
                'screenshot_url': screenshot_url}
        self.put(BASE_URL + '/results', data=json.dumps(data))

    # ToDo: Abstract this to ScopeClient
    def _post_summary_waveform(self):
        """Sends summary dataset for full waveform views

        If the length of y values is greater than the max for a
        browser, the list will be 'shrunk' or sampled to get a
        summary representation of the list of values. If the full
        list is under the max length then no shrinking or sampling
        is needed and the full list is posted.
        """
        logger.info("in post_summary_waveform")
        summary_channels = []
        for channel in self.channels:
            summary_channel = {}  # create new summary channel
            summary_channel.update(channel)  # copy the channel info
            max_length = int(settings.MAX_LENGTH_FOR_BROWSER)
            if len(summary_channel['y_values']) > max_length:
                summary_channel['y_values'] = self._shrink(summary_channel)
            summary_channels.append(summary_channel)
        summary_data = {}
        summary_data.update(self.metadata)
        summary_data['channels'] = summary_channels
        payload = {
            'data': summary_data,
        }
        json_data = json.dumps(payload)
        logger.info("posting end to end (decimated) waveform")
        url_d = BASE_URL + "/results/%s/summary" % self.metadata['result_id']
        self.post(url_d, data=json_data)

    # ToDo: Abstract this to ScopeClient
    def _shrink(self, summary_channel, mode='normal',
                max_length=settings.MAX_LENGTH_FOR_BROWSER):
        """Shinks a voltage list to a decimated waveform

        Decimated waveform needed for faster data transfer and to save
        browser memory when drawing the summary view.
        """
        logger.debug("shrinking summary channel")
        y_values = summary_channel['y_values']
        len_y_values = len(y_values)
        dec_factor = len_y_values / int(max_length)
        summary_channel['dec_factor'] = dec_factor
        og_time_step = summary_channel['time_step']
        summary_channel['og_time_step'] = og_time_step
        new_time_step = summary_channel['dec_factor'] * og_time_step
        summary_channel['time_step'] = new_time_step
        self.dec_time_step = new_time_step  # migrate out
        shrunk_list = [y_values[0]]
        offset = summary_channel['dec_factor']  # for sampling

        while offset < len_y_values:
            if mode == 'normal':
                shrunk_list.append(y_values[offset])
                offset += int(dec_factor)
            elif mode == 'average':
                offset += int(dec_factor)
                mean_value = self._mean(
                    y_values[offset - int(dec_factor): offset])
                shrunk_list.append(mean_value)
            elif mode == 'downsample':
                # use scipy.signal.downsample
                pass
            elif mode == 'voltage_peak_to_peak':
                dec_factor = dec_factor * 2
        logger.info("Shrunk list down to %s items" % len(shrunk_list))
        return shrunk_list

    def _mean(self, list_vals):
        if not list_vals:
            return 0.0
        tmp_sum = 0
        for val in list_vals:
            tmp_sum += val
        mean_val = float(tmp_sum) / len(list_vals)
        return mean_val

    # ToDo: Abstract this to ScopeClient
    def _quick_post_results(self, only_result_id=False):
        """Gives the quick feedback to the server for UI feedback

        Sends the first slice along with channel metadata needed
        to plot the data.

        Also calls _post_summary_waveform() for the overall data
        that is used to plot the summary waveform at the top of
        the waveform chart.

        only_result_id will skip the results upload and only get a result id.
        """
        if not only_result_id:
            self._set_divisions()
            if self.slice_dict:
                slice_list_len = len(self.slice_dict.itervalues().next())
            else:
                slice_list_len = 0
            first_y_values = self.first_slice.values()
            if len(first_y_values) == 0:
                slice_length = 0
            else:
                slice_length = len(first_y_values[0])
            slice_metadata = {
                'num_of_slices': slice_list_len,
                'slice_length': slice_length,
                'total_points': self.waveform_length,
            }
            msg = ("Slice metadata for the waveform: {}"
                   .format(slice_metadata))
            tlogger.info((msg).rjust(len(msg) + 9))
            self.metadata.update(slice_metadata)
        if self.capture_mode:
            config_name = str(self.command_id)
        else:
            config_name = self.config['name']
        if not config_name:
            logger.warning("No config_name for command {}, using id"
                           .format(self.command_id))
            config_name = str(self.command_id)
        self.metadata['screenshot_blob_key'] = self.screenshot_blob_key
        self.metadata['instrument_serial'] = self.instrument_serial
        # result_info['data'] = self.first_slice
        result = {
            'command_id': self.command['id'],
            'config_name': config_name,
            'instrument_type': self.command['info']['instrument_type'],
            'category': self.category,
            'tags': self.command['tags'],
            'device_under_test': self.device_under_test,
            'step_id': self.command['step_id'],
            'plan_id': self.command['plan_id'],
            'info': self.metadata,
        }
        r_url = BASE_URL + '/results'
        headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
        json_data = json.dumps({'result': result}, ensure_ascii=True)
        response = self.post(r_url, data=json_data, headers=headers)
        result_id = ''
        try:
            self.logger.info("_quick_post_results response.status_code: %s"
                             % response.status_code)
            result_id = json.loads(response.text)['result']['id']
            tlogger.info("Quick post of results was successful with "
                         "result_id: {}".format(result_id))
        except ValueError:
            logger.warning("ValueError in _quick_post_results")
        except KeyError:
            logger.warning("KeyError in _quick_post_results")
        except Exception as e:
            logger.warning("Unexpected error: {}".format(e), exc_info=True)
        self.metadata['result_id'] = result_id
        if os.path.exists(COMMAND_FILE):
            with open(COMMAND_FILE, "r") as f:
                command = json.loads(f.read())
            command["result_id"] = result_id
            with open(COMMAND_FILE, "w") as f:
                f.write(json.dumps(command))

        if not only_result_id:
            # now that the result id is acquired, save it to file w/ result id
            tracefile = 'full-trace-%s.json' % result_id
            self._write_trace_dict(filename=tracefile)
            url = BASE_URL + '/results/%s/slices/metadata' % result_id
            r = self.post(url, data=json.dumps(
                {'num_of_slices': slice_list_len}))
            logger.info("slices/metadata post response %s" % r.text)
            self._post_summary_waveform()
        c_url = BASE_URL + '/commands'
        command_data = {
            'id': self.command['id'],
            'status': 'partial results',
            'results': [{'result_id': result_id}],
        }
        response = self.put(c_url, data=json.dumps(command_data))

    def _set_divisions(self, h_divs=0, v_divs=0):
        if self.instr._horizontal_divisions:
            self._horizontal_divisions = self.instr._horizontal_divisions
        else:
            self._horizontal_divisions = 10
        if self.instr._vertical_divisions:
            self._vertical_divisions = self.instr._vertical_divisions
        else:
            self._vertical_divisions = 8
        if h_divs:
            self._horizontal_divisions = h_divs
        if v_divs:
            self._vertical_divisions = v_divs
        self.trace_dict['h_divs'] = self._horizontal_divisions
        self.trace_dict['v_divs'] = self._vertical_divisions

    def get_horizontal_divisions(self):
        if self._horizontal_divisions:
            return self._horizontal_divisions
        else:
            self._set_divisions()
            return self._horizontal_divisions

    def get_vertical_divisions(self):
        if self._vertical_divisions:
            return self._vertical_divisions
        else:
            self._set_divisions()
            return self._vertical_divisions

    def post_status_update(self, status):
        status_url = (self.BASE_URL + '/status/' +
                      COMPANYNAME + '/' +
                      settings.GATEWAY_ID)
        self.post(status_url, status)

    def handle_usb_error(self, e):
        if e.args == ('Operation timed out',):
            logger.debug("Found USBError: Operation timed out")
            self.config_scorecard['errors']['usb_timeouts'] += 1
        elif e.args == ('Resource busy',):
            logger.debug('Found USBError: Resource busy')
            self.post_status_update("Critical USBError")
            self.config_scorecard['errors']['usb_resource_busy'] += 1
        else:
            logger.debug('Unknown USBError')

    def update_scorecard_times(self):
        times = self.times
        stf = times['complete'] - times['init']
        lc = times['load_config_end'] - times['load_config_start']
        fm = times['fetch_measurements_end'] - \
            times['fetch_measurements_start']
        config_times = {
            'start_to_finish': stf,
            'load_config': lc,
            'fetch_measurements': fm,
        }
        self.config_scorecard['times'] = config_times

    def validate_config_excerpt(self, config):
        """Validates that the config

        Currently just checks that channels is in list format,
        converts dict format to list format, if it's neither
        then it just returns {}.
        """
        validated_channels = []
        if "frames" in config:
            return config
        if 'channels' not in config:
            logger.warning("config is missing 'channels'")
            return {}
        if isinstance(config['channels'], list):
            return self._validate_channels_list_config(config)
        if not isinstance(config['channels'], dict):
            logger.warning("unexpected type for config")
            return {}
        for ch_key in config['channels']:
            valid_channel = {}
            channel = config['channels'][ch_key]
            for field in channel:
                clean_field = field.replace('channel_', '')
                valid_channel[clean_field] = channel[field]
            valid_channel['name'] = ch_key
            validated_channels.append(valid_channel)
        config['channels'] = validated_channels
        self._validate_channels_list_config(config)
        return config

    def _validate_channels_list_config(self, config):
        for idx, channel in enumerate(config['channels']):
            if idx > len(self._analog_channel_names):
                msg = "config has more channels than known analog channels"
                logger.error(msg)
                break
            if 'name' not in channel:
                est_ch = self._analog_channel_names[idx]  # use ivi given name
                msg = "Missing field 'name' from channel. Using %s" % est_ch
                logger.warning(msg)
                channel['name'] = est_ch
            if channel['name'] not in self._analog_channel_names:
                logger.warning("Channel %s is not an analog channel"
                               % channel['name'])
                channel['name'] = self._analog_channel_names[idx]
                logger.info("Assigning analog channel name %s"
                            % channel['name'])
            if 'enabled' not in channel:
                logger.info("Assuming %s enabled" % channel['name'])
                channel['enabled'] = True
        return config

    def _read_csv_to_dict_of_lists(self, filename):
        dict_of_lists = defaultdict(list)
        for record in DictReader(open(filename)):
            for key, val in record.iteritems():
                dict_of_lists[key].append(val)
        return dict_of_lists

    def _get_metadata(self, results_dict={}, channels={}, filename=''):
        """Gets metadata from the args

        Removes the trace data from the channels leaving just metadata
        """
        metadata = {}
        metadata.update(results_dict)
        metadata['channels'] = []
        if results_dict != {} and 'channels' in results_dict:
            channels = results_dict['channels']
        for channel in channels:
            metadata['channels'].append(self._metadata_from_channel(channel))
        if filename == '':
            filename = 'full-trace-%s.json' % self.metadata['result_id']
        trace_file = os.path.join(TMPDIR, filename)
        if not os.path.exists(trace_file):
            logger.error("No full trace file!")
            metadata['error'] = "No trace data"
        return metadata

    def _metadata_from_channel(self, channel):
        """Strips y_values from channel, leaving only metadata"""
        channel_copy = {}
        channel_copy.update(channel)
        if 'y_values' in channel_copy:
            del channel_copy['y_values']
        return channel_copy

    def test(self):
        logger.info("channel names: {}".format(self.channel_names))
        dummy_config = {}
        self.validate_config_excerpt(dummy_config)
        self.get_config_excerpt()
        self.set_timebase({})
        self.get_timebase()
        self.get_probe_ids()
        self.get_voltage_list()
        self.get_voltage_digital_list()
        self.get_slice_list()
        self.get_trigger()
        self.get_acquisition()
        self.get_standard_waveform()
        self.get_outputs()
        self.fetch_measurements()
        self.fetch_screenshot()


if __name__ == "__main__":
    unit_test_cmd = {'info': {'instrument_type': 'scope'}, 'unit_test': True}
    dummy_instrument = DummyScope()
    driver = ScopeDriver(command=unit_test_cmd, instrument=dummy_instrument)
    driver.test()

# # Not all currently used but kept for reference:
#
# base_meas = [
#                  {
#                      'ivi_name': 'rise_time',
#                      'display_name': 'Rise Time',
#                      'units': 's',
#                  },
#                  {
#                      'ivi_name': 'fall_time',
#                      'display_name': 'Fall Time',
#                      'units': 's',
#                 },
#                 {
#                     'ivi_name': 'frequency',
#                     'display_name': 'Frequency',
#                     'units': 'Hz',
#                 },
#                 {
#                     'ivi_name': 'period',
#                     'display_name': 'Period',
#                     'units': 's',
#                 },
#                 {
#                     'ivi_name': 'voltage_rms',
#                     'display_name': 'Voltage RMS',
#                     'units': 'V',
#                 },
#                 {
#                     'ivi_name': 'voltage_peak_to_peak',
#                     'display_name': 'Voltage Peak to Peak',
#                     'units': 'V',
#                 },
#                 {
#                     'ivi_name': 'voltage_max',
#                     'display_name': 'Voltage Max',
#                     'units': 'V',
#                 },
#                 {
#                     'ivi_name': 'voltage_min',
#                     'display_name': 'Voltage Min',
#                     'units': 'V',
#                 },
#                 {
#                     'ivi_name': 'voltage_high',
#                     'display_name': 'Voltage High',
#                     'units': 'V',
#                 },
#                 {
#                     'ivi_name': 'voltage_low',
#                     'display_name': 'Voltage Low',
#                     'units': 'V',
#                 },
#                 {
#                     'ivi_name': 'voltage_average',
#                     'display_name': 'Voltage Average',
#                     'units': 'V',
#                 },
#                 {
#                     'ivi_name': 'width_negative',
#                     'display_name': 'Width Negative',
#                     'units': 's',
#                 },
#                 {
#                     'ivi_name': 'width_positive',
#                     'display_name': 'Width Positive',
#                     'units': 's',
#                 },
#                 {
#                     'ivi_name': 'duty_cycle_negative',
#                     'display_name': 'Duty Cycle Negative',
#                     'units': 's',
#                 },
#                 {
#                     'ivi_name': 'duty_cycle_positive',
#                     'display_name': 'Duty Cycle Positive',
#                     'units': 's',
#                 },
#                 {
#                     'ivi_name': 'amplitude',
#                     'display_name': 'Amplititude',
#                     'units': 'V',
#                 },
#                 {
#                      'ivi_name': 'voltage_cycle_rms',
#                      'display_name': 'Voltage Cycle RMS',
#                      'units': 'V',
#                 },
#         ]
