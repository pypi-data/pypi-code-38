import collections
import copy
import os
import sys
import time
import gateway_helpers
import json
import keysight_parent_path
keysight_parent_path.insert()

from scope_driver import ScopeDriver, logger, settings
from base import InstrumentInstructionError
from base import t_diagnostic_logger as tlogger
from base import ReadSettingsError, WriteSettingsError, FetchScreenshotError
from base import FetchWaveformError, FetchMeasurementError

TMPDIR = settings.TMPDIR
BASE_URL = settings.BASE_URL


class KeysightScope(ScopeDriver):

    def __init__(self, command, instrument=None):
        ScopeDriver.__init__(self, command, instrument)
        self._analog_channel_names = self.channel_names[:4]
        self._digital_channel_names = self.channel_names[4:]
        # This is handled in the ScopeDriver __init__
        # Keeping here for reference
        # self.ch_idx_dict = {
        #     'channel1': 0,
        #     'channel2': 1,
        #     'channel3': 2,
        #     'channel4': 3,
        #     'digital0': 4,
        #     'digital1': 5,
        #     'digital2': 6,
        #     'digital3': 7,
        #     'digital4': 8,
        #     'digital5': 9,
        #     'digital6': 10,
        #     'digital7': 11,
        #     'digital8': 12,
        #     'digital9': 13,
        #     'digital10': 14,
        #     'digital11': 15,
        #     'digital12': 16,
        #     'digital13': 17,
        #     'digital14': 18,
        #     'digital15': 19
        # }
        self._pod_list = [
            'pod1',
            'pod2',
            'podall',
        ]
        self._bus_list = [
            'sbus1',
            'sbus2',
            'sbus3',
            'sbus4',
        ]
        self._sbus_serial_dict = {
            'sbus1': 'Serial1',
            'sbus2': 'Serial2',
            'sbus3': 'Serial3',
            'sbus4': 'Serial4',
        }
        self.channel_settings = ['range', 'offset']
        self.acq_dict = {
            'sample_rate_auto': '',
            'analog_sample_rate_auto': '',
            'analog_sample_rate': '',
            'analog_memory_depth_auto': '',
            'number_of_points_minimum_auto': '',
            'number_of_points_minimum': '',
            'type': '',
            'start_time': '',
            'averaging_enabled': '',
            'number_of_averages': '',
        }

        # make this support other scopes
        self.pod1_list = ['digital0', 'digital1', 'digital2', 'digital3', 'digital4', 'digital5', 'digital6', 'digital7']
        self.pod2_list = ['digital8', 'digital9', 'digital10', 'digital11', 'digital12', 'digital13', 'digital14', 'digital15']

        if 'horizontal' in self.ce_dict:
            data = self.ce_dict['horizontal']
            self.horiz_dict = collections.defaultdict(int, data)
        else:
            logger.warning("MSO9XXA missing 'horizontal' in config")
            self.horiz_dict = collections.defaultdict(int)
        base_meas = [
            {
                'ivi_name': 'rise_time',
                'display_name': 'Rise Time',
                'units': 's',
            },
            {
                'ivi_name': 'fall_time',
                'display_name': 'Fall Time',
                'units': 's',
            },
            {
                'ivi_name': 'frequency',
                'display_name': 'Frequency',
                'units': 'Hz',
            },
            {
                'ivi_name': 'period',
                'display_name': 'Period',
                'units': 's',
            },
            # {
            #     'ivi_name': 'voltage_rms',
            #     'display_name': 'Voltage RMS',
            #     'units': 'V',
            # },
            {
                'ivi_name': 'voltage_peak_to_peak',
                'display_name': 'Voltage Peak to Peak',
                'units': 'V',
            },
            {
                'ivi_name': 'voltage_max',
                'display_name': 'Voltage Max',
                'units': 'V',
            },
            {
                'ivi_name': 'voltage_min',
                'display_name': 'Voltage Min',
                'units': 'V',
            },
            {
                'ivi_name': 'voltage_high',
                'display_name': 'Voltage High',
                'units': 'V',
            },
            {
                'ivi_name': 'voltage_low',
                'display_name': 'Voltage Low',
                'units': 'V',
            },
            # {
            #     'ivi_name': 'voltage_average',
            #     'display_name': 'Voltage Average',
            #     'units': 'V',
            # },
            {
                'ivi_name': 'width_negative',
                'display_name': 'Width Negative',
                'units': 's',
            },
            {
                'ivi_name': 'width_positive',
                'display_name': 'Width Positive',
                'units': 's',
            },
            # {
            #     'ivi_name': 'duty_cycle_negative',
            #     'display_name': 'Duty Cycle Negative',
            #     'units': 's',
            # },
            # {
            #     'ivi_name': 'duty_cycle_positive',
            #     'display_name': 'Duty Cycle Positive',
            #     'units': 's',
            # },
            {
                'ivi_name': 'amplitude',
                'display_name': 'Amplititude',
                'units': 'V',
            },
            # {
            #      'ivi_name': 'voltage_cycle_rms',
            #      'display_name': 'Voltage Cycle RMS',
            #      'units': 'V',
            # },
        ]
        self.meas_list = []
        self.meas_list.extend(base_meas)

    def check_instrument_ready(self):
        """Simply returns True since the Keysight has no busy? check"""
        return True

    def _get_config_excerpt_extras(self):
        """Get fields beyond the base config excerpt"""
        extras = {}
        extras['horizontal'] = self.get_timebase()
        extras['digital_channels'] = self.get_digital_channels()
        extras['digital_threshold'] = self.get_digital_threshold()
        return extras

    def load_special_config_fields(self):
        self._set_timebase()
        if 'digital_channels' in self.ce_dict:
            self._set_digital_channels(self.ce_dict['digital_channels'])
        if 'digital_threshold' in self.ce_dict:
            self._set_digital_thresholds(self.ce_dict['digital_threshold'])

    def _set_enabled_list(self):
        self.enabled_list = []  # resets enabled list
        if settings.SIMULATED:
            self.enabled_list = ['ch1']
            return
        if self.command['name'] == 'Config':
            for ch in self._analog_channel_names:
                channel_idx = self.ch_idx_dict[ch]
                if self.instr.channels[channel_idx].enabled:
                    self.enabled_list.append(ch)
            if self.ce_dict['digital_channels']['enable_dig_0_7_channel']:
                for ch in self._digital_channel_names[:8]:
                    self.enabled_list.append(ch)
            if self.ce_dict['digital_channels']['enable_dig_8_15_channel']:
                for ch in self._digital_channel_names[8:16]:
                    self.enabled_list.append(ch)
        if self.capture_mode:
            for ch in self.channel_names:
                channel_idx = self.ch_idx_dict[ch]
                if self.instr.channels[channel_idx].enabled:
                    self.enabled_list.append(ch)
            for ch in self.enabled_list:
                channel = collections.defaultdict(int)
                channel['name'] = ch
                channel['enabled'] = True
                self._update_channels(self.ce_dict['channels'], channel)

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
        for channel in self.ce_dict['channels']:
            ch = channel['name']
            ch_dict = collections.defaultdict(str)
            logger.debug("requesting channel enabled data for %s" % ch)
            ch_idx = self.ch_idx_dict[ch]
            ch_dict['enabled'] = self.ivi_channels[ch_idx].enabled
            time.sleep(0.1)
            if ch_dict['enabled']:
                logger.debug("response %s enabled" % ch)
                ch_dict['name'] = self.ivi_channels[ch_idx].name
                if ch in self._analog_channel_names:
                    ch_dict['offset'] = self.ivi_channels[ch_idx].offset
                    time.sleep(0.1)
                    ch_dict['scale'] = self.ivi_channels[ch_idx].scale
                    time.sleep(0.1)
                    ch_dict['range'] = self.ivi_channels[ch_idx].range
                    time.sleep(0.1)
                    # if hasattr(self.ivi_channels[ch_idx], 'position'):
                    #     ch_dict['position'] = self.ivi_channels[ch_idx].position
                    # time.sleep(0.1)
                    # ch_dict['coupling'] = self.ivi_channels[ch_idx].coupling
                    # print 'coupling is ', ch_dict['coupling']
                    # time.sleep(0.1)
                    # cii = self.ivi_channels[ch_idx].input_impedance
                    # time.sleep(0.1)
                    # ch_dict['input_impedance'] = cii
                    # print 'input_impedance is ', ch_dict['input_impedance']
                if ch not in self.enabled_list:
                    self.enabled_list.append(ch)
            else:
                logger.debug("response: %s NOT enabled" % ch)
            self._update_channels(channels, ch_dict)
        config_excerpt['channels'] = channels
        # sync up excerpt list with driver list
        self.ce_dict['enabled_list'] = self.enabled_list
        config_excerpt['enabled_list'] = self.enabled_list
        return config_excerpt

    def get_trigger(self):
        logger.debug("getting trigger in keysight driver")
        trigger_dict = {}
        trigger_dict = {
            'type': '',
            'coupling': '',
            'source': '',
        }
        for name in trigger_dict:
            trigger_dict[name] = getattr(self.instr.trigger, name).lower()
        if trigger_dict['type'] == 'edge':
            self.ce_dict['trigger_edge_slope'] = self.instr.trigger.edge.slope
        trigger_dict['source'] = self.instr._ask(":trigger:edge:source?")
        trigger_dict['level'] = self.instr._ask(":trigger:level? %s" % trigger_dict['source'])
        return trigger_dict

    def get_protocol_decode(self):
        print "getting some decode in the function"
        logger.debug("getting protocol decode info")
        options = self.instr._ask("*OPT?").split(',')
        if 'LSS' not in options:
            logger.info("Instrument option not enabled")
            return None
        if sys.platform != 'win32':
            logger.info("Platform not windows")
            return None
        enabled_bus_list = []
        for bus in self._bus_list:
            bus_info = {}
            if self.instr._ask("%s:DISPLAY?" % (":" + bus)) == '1':
                bus_info['enabled'] = bus
                bus_info['mode'] = self.instr._ask("%s:MODE?" % (":" + bus))
                filename = "decode_" + bus + "_" + self.metadata['result_id'] + ".csv"
                decodefile = os.path.join(TMPDIR, filename)
                path = os.path.abspath(decodefile)
                ivi_cmd_builder_a = ':DISK:SAVE:LISTING ' + self._sbus_serial_dict[bus]
                ivi_cmd_builder_b = ', "' + path + '"'
                ivi_cmd_builder_c = ', CSV'
                ivi_cmd = ivi_cmd_builder_a + ivi_cmd_builder_b + ivi_cmd_builder_c
                self.instr._write(ivi_cmd)
                decode = self._read_csv_to_dict_of_lists(path)
                bus_info['decode'] = decode
                enabled_bus_list.append(bus_info)
                self.remove_file(decodefile)
                print 'got some decode'
        if not enabled_bus_list:
            return None
        else:
            return enabled_bus_list[0]

    def _grab_and_post_screenshot(self):
        logger.debug("_grab_and_post_screenshot")
        file_key = "screenshot-" + self.metadata['result_id'] + ".png"
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

    def _send_fetch_screenshot_cmd(self, file_key):
        """Sends instrument specific command

        Overrides parent method due to support Keysight screenshots
        """
        pngfile = os.path.join(TMPDIR, file_key)
        ivi_cmd_builder_a = ':DISK:SAVE:IMAGe'
        ivi_cmd_builder_b = ' "%s", PNG, SCR' % os.path.abspath(pngfile)
        ivi_cmd = ivi_cmd_builder_a + ivi_cmd_builder_b
        self.instr._write(ivi_cmd)
        time.sleep(1)
        return pngfile

    def get_timebase(self):
        horizontal = collections.defaultdict(int)
        try:
            horizontal['start_time'] = self.instr.timebase.position
        except Exception:
            logger.debug("get timebase position exception")
        try:
            horizontal['scale'] = self.instr.timebase.scale
        except Exception:
            logger.debug("get timebase scale exception")
        # try:
        #     horizontal['reference'] = self.instr.timebase.reference
        # except Exception:
        #     logger.debug("get timebase reference exception")
        return horizontal

    def _set_timebase(self):
        # TODO add reference
        try:
            if self.horiz_dict['start_time']:
                self.horiz_dict['position'] = self.horiz_dict['start_time']
                del self.horiz_dict['start_time']
        except Exception as e:
            logger.debug(e, exc_info=True)
        for key in self.horiz_dict:
            self.set_adders += 1
            self._setinstr_with_tries(self.instr.timebase, key,
                                      self.horiz_dict[key], label='timebase_',
                                      tries=3)

    def _set_digital_channels(self, digital_chan_dict):
        try:
            if digital_chan_dict['enable_dig_0_7_channel']:
                self.instr._write(":POD1:DISPLAY 1")
            else:
                self.instr._write(":POD1:DISPLAY 0")
        except Exception as e:
            logger.debug(e, exc_info=True)
        try:
            if digital_chan_dict['enable_dig_8_15_channel']:
                self.instr._write(":POD2:DISPLAY 1")
            else:
                self.instr._write(":POD2:DISPLAY 0")
        except Exception as e:
            logger.debug(e, exc_info=True)

    def get_digital_channels(self):
        digital_channels = {}
        value = self.instr._ask(":POD1:DISPLAY?")
        if value == "1" or value == 1:
            digital_channels['enable_dig_0_7_channel'] = True
        else:
            digital_channels['enable_dig_0_7_channel'] = False
        value = self.instr._ask(":POD2:DISPLAY?")
        if value == "1" or value == 1:
            digital_channels['enable_dig_8_15_channel'] = True
        else:
            digital_channels['enable_dig_8_15_channel'] = False
        return digital_channels

    def _set_digital_thresholds(self, digital_threshold_dict):
        try:
            if digital_threshold_dict['digital_threshold_d0_d7']:
                    self.instr._write(":POD1:THRESHOLD %s" % digital_threshold_dict['digital_threshold_d0_d7'])
        except Exception as e:
            logger.debug(e, exc_info=True)
        try:
            if digital_threshold_dict['digital_threshold_d8_d15']:
                    self.instr._write(":POD2:THRESHOLD %s" % digital_threshold_dict['digital_threshold_d8_d15'])
        except Exception as e:
            logger.debug(e, exc_info=True)

    def get_digital_threshold(self):
        digital_threshold = {}
        digital_threshold['digital_threshold_d0_d7'] = float(self.instr._ask(":POD1:THRESHOLD?"))
        digital_threshold['digital_threshold_d8_d15'] = float(self.instr._ask(":POD2:THRESHOLD?"))
        return digital_threshold

    def _scale_lookup(self, value):
        # value = value[0]
        scale_table = {"1ks": 1000,
                       "500s": 500,
                       "200s": 200,
                       "100s": 100,
                       "50s": 50,
                       "20s": 20,
                       "10s": 10,
                       "5s": 5,
                       "2s": 2,
                       "1s": 1,
                       "500ms": 0.5,
                       "200ms": 0.2,
                       "100ms": 0.1,
                       "50ms": 0.05,
                       "20ms": 0.02,
                       "10ms": 0.01,
                       "5ms": 0.005,
                       "2ms": 0.002,
                       "1ms": 0.001,
                       "500us": 5e-4,
                       "200us": 2e-4,
                       "100us": 1e-4,
                       "50us": 5e-5,
                       "20us": 2e-5,
                       "10us": 1e-5,
                       "5us": 5e-6,
                       "2us": 2e-6,
                       "1us": 1e-6,
                       "500ns": 5e-7,
                       "200ns": 2e-7,
                       "100ns": 1e-7,
                       "50ns": 5e-8,
                       "20ns": 2e-8,
                       "10ns": 1e-8,
                       "5ns": 5e-9,
                       "2.5ns": 2.5e-9,
                       "1ns": 1e-9,
                       "500ps": 5e-10,
                       "250ps": 2.5e-10}
        scale = scale_table[value]
        return scale

    def _get_instrument_settings(self):
        """Instrument settings that are channel independent

        Separate from the config excerpt
        """
        settings = {}
        settings['h_divs'] = self.get_horizontal_divisions()
        settings['v_divs'] = self.get_vertical_divisions()
        settings['timebase_range'] = self.instr.timebase.range
        settings['timebase_position'] = self.instr.timebase.position
        settings['timebase_scale'] = self.instr.timebase.scale
        temp_value = self.instr.timebase.reference
        if temp_value == 'center':
            settings['timebase_reference'] = '50'
        elif temp_value == 'right':
            settings['timebase_reference'] = '100'
        elif temp_value == 'left':
            settings['timebase_reference'] = '0'
        else:
            settings['timebase_reference'] = temp_value
        return settings

    def _handle_pods(self):
        """Handles pods for digital data

        Called by fetch_measurements. Overrides parent method.
        """
        pod_tmp = []
        for ch in self.enabled_list:
            if ch in self.pod1_list:
                pod_tmp.append('pod1')
            elif ch in self.pod2_list:
                pod_tmp.append('pod2')

        pod_tmp = set(pod_tmp)
        if 'pod1' in pod_tmp and 'pod2' in pod_tmp:
            pod_final = ['podall']
        else:
            pod_final = list(pod_tmp)
        for item in pod_final:
            logger.info("Fetching digital waveform for %s" % item)
            self._fetch_waveform_digital(pod_final[0])

    def _fetch_waveform(self, channel_name):
        """Gets the waveform data from the instrument

        This is the method that actually fetches the data from the
        ivi channel instance for the waveform and channel metadata
        for a given trace.

        This is the method that intializes the channel for the
        drivers channels list for storing the data collected
        for each channel enabled on the scope.
        """
        logger.debug("TransformerMSO90XXA:_fetch_waveform ...")
        self.check_commands_completed()  # check if ready
        try:
            channel_idx = self.ch_idx_dict[channel_name]
            ivi_channel = self.instr.channels[channel_idx]
            waveform = list(ivi_channel.measurement.fetch_waveform())
        except Exception:
            self.logger.warning("failed to fetch waveform for: %s"
                                % channel_name, exc_info=True)
        self.waveform_length = len(waveform)
        logger.debug("waveform length for %s: %s" %
                     (channel_name, self.waveform_length))
        time_step = waveform[1][0] - waveform[0][0]
        voltage_list = self.get_voltage_list(waveform)
        slice_list = self.get_slice_list(voltage_list)
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

        # collect channel metadata for plotting
        # if hasattr(ivi_channel, 'trigger_level'):
        #     channel_data['trigger_level'] = ivi_channel.trigger_level
        try:
            channel_data['range'] = ivi_channel.range
            # channel_data['coupling'] = ivi_channel.coupling
            channel_data['offset'] = ivi_channel.offset
            channel_data['scale'] = ivi_channel.scale
            # index here is the ivi index number for the channel
            channel_data['index'] = self.ch_idx_dict[channel_name]
        except Exception as e:
            logger.warning(e, exc_info=True)
        # if hasattr(ivi_channel, 'position'):
        #     try:
        #         channel_data['position'] = ivi_channel.position
        #     except Exception as e:
        #         logger.warning(e, exc_info=True)
        # update current channels list
        self._update_channels(self.channels, channel_data)
        self.time_step = time_step  # migrate towards ch specific

    def _fetch_waveform_measurements(self):
        """Fetches measurments about the waveform

        Note for emphasis: Measurements in this case refers to the
        ivi measurements about the waveform and NOT the waveform
        itself and NOT calculations GradientOne performs on the
        waveform.
        """
        self.check_commands_completed()
        logger.debug("fetching waveform measurements")
        if not self.ivi_channels:
            self.ivi_channels = self.instr.channels
        for channel in self.metadata['channels']:
            ch_idx = self.ch_idx_dict[channel['name']]
            ivi_channel = self.ivi_channels[ch_idx]
            channel['waveform_measurements_valid'] = True  # starts off valid
            for meas in self.meas_list:
                # Skip if simulated (meas_list should be empty anyway)
                if settings.SIMULATED:
                    continue
                instrument = ivi_channel.measurement
                ivi_name = meas['ivi_name']
                try:
                    val = instrument.fetch_waveform_measurement(ivi_name)
                except Exception:
                    logger.debug("measurement exception %s" % ivi_name,
                                 exc_info=True)
                    raise InstrumentInstructionError
                logger.debug("%s, %s", ivi_name, val)
                meas['value'] = val
                self.check_commands_completed()
            for i in self.meas_list:
                if i['value'] == 'measurement error':
                    i['value'] == 'N/A'
                elif i['value'] > settings.MAX_VALID_MEAS_VAL:
                    channel['waveform_measurements_valid'] = False
                    i['value'] = settings.MAX_VALID_MEAS_VAL
                else:
                    pass
            channel['waveform_measurements'] = self.meas_list
        protocol_decode = self.get_protocol_decode()
        if protocol_decode is not None:
            self.metadata['protocol_decode'] = protocol_decode

    def _set_acquisition(self, acq_dict):
        self._validate_acq_dict(acq_dict)
        for key in acq_dict:
            self.set_adders += 1

            # should these be removed from the input config on the server? TS
            if key == 'analog_memory_depth_auto':
                if acq_dict['analog_memory_depth_auto']:
                    self.instr._write(":ACQuire:POINts:AUTO 1")
                else:
                    self.instr._write(":ACQuire:POINts:AUTO 0")
                pass
            elif key == 'analog_sample_rate_auto':
                if acq_dict['analog_sample_rate_auto']:
                    self.instr._write(":ACQuire:SRATe:ANALog:AUTO 1")
                else:
                    self.instr._write(":ACQuire:SRATe:ANALog:AUTO 0")
                pass
            elif key == 'sample_rate_auto':
                pass
            elif key == 'time_per_record':
                pass
            elif key == 'record_length':
                pass
            elif key == 'number_of_points_minimum_auto':
                pass
            else:
                self._setinstr_with_tries(self.instr.acquisition, key,
                                          acq_dict[key], label='acquisition_',
                                          tries=3)

    def get_acquisition(self):
        logger.debug("getting acquisition")
        for key in self.acq_dict:
            if key == 'number_of_points_minimum_auto':
                value = self.instr._ask(":ACQuire:POINts:AUTO?")
                if value == "1":
                    self.acq_dict['number_of_points_minimum_auto'] = "Auto"
                    self.acq_dict['analog_memory_depth_auto'] = True
                elif value == "0":
                    self.acq_dict['number_of_points_minimum_auto'] = "Manual"
                    self.acq_dict['analog_memory_depth_auto'] = False
                pass
            elif key == 'analog_memory_depth_auto':
                pass
            elif key == 'sample_rate_auto':
                value = self.instr._ask(":acquire:srate:analog:auto?")
                if value == "1":
                    self.acq_dict['sample_rate_auto'] = "Auto"
                    self.acq_dict['analog_sample_rate_auto'] = True
                elif value == "0":
                    self.acq_dict['sample_rate_auto'] = "Manual"
                    self.acq_dict['analog_sample_rate_auto'] = False
                pass
            elif key == 'analog_sample_rate_auto':
                pass
            elif key == 'time_per_record':
                pass
            elif key == 'record_length':
                pass
            elif key == 'averaging_enabled':
                value = getattr(self.instr.acquisition, key)
                if value == "1" or value == 1:
                    self.acq_dict[key] = True
                if value == "0" or value == 0:
                    self.acq_dict[key] = False
            else:
                self.acq_dict[key] = getattr(self.instr.acquisition, key)
        return self.acq_dict

    def _validate_acq_dict(self, acq_dict):
        if 'record_length' in acq_dict:
            del acq_dict['record_length']
        logger.debug("setting acquisition: " + str(acq_dict))
        try:
            if acq_dict['analog_memory_depth_auto']:
                del acq_dict['number_of_points_minimum']
        except Exception as e:
            logger.debug(e, exc_info=True)
        try:
            if acq_dict['averaging_enabled']:
                acq_dict['averaging_enabled'] = 1
            if not acq_dict['averaging_enabled']:
                acq_dict['averaging_enabled'] = 0
        except Exception as e:
            logger.debug(e, exc_info=True)
        try:
            if acq_dict['analog_sample_rate']:
                acq_dict['analog_sample_rate'] = float(acq_dict['analog_sample_rate'])
        except Exception as e:
            logger.debug(e, exc_info=True)
        try:
            if acq_dict['analog_sample_rate_auto']:
                del acq_dict['analog_sample_rate']
        except Exception as e:
            logger.debug(e, exc_info=True)

    def _sample_rate_lookup(self, scale_string):
        # mothballed
        sample_rate_table = {"400GS/s": 400e9,
                             "200GS/s": 200e9,
                             "80GS/s": 80e9,
                             "40GS/s": 40e9,
                             "20GS/s": 20e9,
                             "10GS/s": 10e9,
                             "5GS/s": 5e9,
                             "2.5GS/s": 2.5e9,
                             "1GS/s": 1e9,
                             "500MS/s": 500e6,
                             "200MS/s": 200e6,
                             "100MS/s": 100e6,
                             "50MS/s": 50e6,
                             "40MS/s": 40e6,
                             "20MS/s": 20e6,
                             "10MS/s": 10e6,
                             "5MS/s": 5e6,
                             "2MS/s": 2e6,
                             "1MS/s": 1e6,
                             "500Ks/s": 500000,
                             "200Ks/s": 200000,
                             "100Ks/s": 100000,
                             "50Ks/s": 50000,
                             "20Ks/s": 20000,
                             "10Ks/s": 10000,
                             "5kS/s": 5000,
                             "2kS/s": 2000,
                             "1kS/s": 1000,
                             "500S/s": 500,
                             "200S/s": 200,
                             "100S/s": 100,
                             "50S/s": 50,
                             "20S/s": 20,
                             "10S/s": 10,
                             "5S/s": 5}
        sample_rate = str(sample_rate_table[scale_string])
        return sample_rate

    def fetch_raw_setup(self, last_try=False):
        logger.debug("fetching raw_setup")
        raw_setup = "todo fix size issue with post"
        return raw_setup