import time
import datetime
import usb
import collections
import copy
import gateway_helpers
import rigol_parent_path
rigol_parent_path.insert()
import settings
from base import InstrumentInstructionError, ReadSettingsError
from gateway_helpers import dt2ms, round_sig, logger
from scope_driver import ScopeDriver
from base import t_diagnostic_logger as tlogger
from gateway_helpers import timeout
from base import FetchWaveformError, FetchMeasurementError, WriteSettingsError

DEFAULT_RIGOL_CONFIG = {
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
        "name": "chan1"
    }, {
        "range": 1,
        "offset": 0,
        "enabled": False,
        "coupling": "dc",
        "name": "chan2"
    }, {
        "range": 1,
        "offset": 0,
        "enabled": False,
        "coupling": "dc",
        "name": "chan3"
    }, {
        "range": 1,
        "offset": 0,
        "enabled": False,
        "coupling": "dc",
        "name": "chan4"
    }],
    "trigger_edge_slope": "positive",
    "trigger": {
        "source": "chan1",
        "type": "edge",
        "coupling": "dc",
        "level": 0.288
    },
    "acquisition": {
        "number_of_points_minimum": 1000,
        "start_time": -4.999999999999996e-06,
        "number_of_envelopes": 0,
        "time_per_record": 9.999999999999999e-06,
        "type": "average",
        "number_of_averages": 512
    },
}


class RigolScope(ScopeDriver):

    def __init__(self, setup, instrument):
        ScopeDriver.__init__(self, setup, instrument)
        self.enabled_list = ['chan1']  # by default, only ch1 enabled
        self.channel_names = [c.name for c in self.ivi_channels]
        self._analog_channel_names = self.channel_names[:4]
        self._digital_channel_names = self.channel_names[4:]
        self.ch_idx_dict = {
            'chan1': 0,
            'chan2': 1,
            'chan3': 2,
            'chan4': 3,
            'd0': 4,
            'd1': 5,
            'd2': 6,
            'd3': 7,
            'd4': 8,
            'd5': 9,
            'd6': 10,
            'd7': 11,
            'd8': 12,
            'd9': 13,
            'd10': 14,
            'd11': 15,
            'd12': 16,
            'd13': 17,
            'd14': 18,
            'd15': 19
        }
        self.acq_dict = {
            # 'analog_sample_rate': '',
            'number_of_points_minimum': '',
            'type': '',
            'number_of_averages': '',
            'record_length': '',
        }

        self.channel_settings = ['offset', 'scale', 'coupling']
        self._pod_list = [
            'pod1',
            'pod2',
            'podall',
        ]
        self.mem_depth_lookups = {1: 12000, 2: 6000, 3: 3000, 4: 3000}
        self.pod1_list = ['d0', 'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7']
        self.pod2_list = ['d8', 'd9', 'd10', 'd11', 'd12', 'd13', 'd14', 'd15']
        self.pod_all = self.pod1_list + self.pod2_list
        base_meas = [
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
                {
                    'ivi_name': 'voltage_rms',
                    'display_name': 'Voltage RMS',
                    'units': 'V',
                },
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
                {
                    'ivi_name': 'voltage_average',
                    'display_name': 'Voltage Average',
                    'units': 'V',
                },
                # {
                #     'ivi_name': 'width_negative',
                #     'display_name': 'Width Negative',
                #     'units': 's',
                # },
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
                {
                    'ivi_name': 'duty_cycle_positive',
                    'display_name': 'Duty Cycle Positive',
                    'units': 's',
                },
                {
                    'ivi_name': 'amplitude',
                    'display_name': 'Amplititude',
                    'units': 'V',
                },
                {
                     'ivi_name': 'voltage_cycle_rms',
                     'display_name': 'Voltage Cycle RMS',
                     'units': 'V',
                },
            ]
        self.meas_list = []
        self.meas_list.extend(base_meas)

        base_meas_digital = [
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
            ]
        self.meas_list_digital = []
        self.meas_list_digital.extend(base_meas_digital)
        self.c = False


    def load_special_fields(self):
        if 'timebase' in self.ce_dict:
            self.set_timebase(self.ce_dict['timebase'])
        if 'horizontal' in self.ce_dict:
            self.set_timebase(self.ce_dict['horizontal'])

    def _get_config_excerpt_extras(self):
        """Get fields beyond the base config excerpt"""
        logger.debug("getting rigol scope config extras")
        extras = {}
        extras['horizontal'] = self.get_timebase()
        return extras

    def get_acquisition(self):
        logger.debug("getting acquisition")
        tlogger.info("Getting acquisition data from the instrument")
        for key in self.acq_dict:
            try:
                if key == 'record_length':
                    self.acq_dict[key] = self.waveform_length
                else:
                    self.acq_dict[key] = self.get_acquisition_wrapper(key)
                    msg = ("Acquisition setting %s is %s " % (key, self.acq_dict[key]))
                    tlogger.info((msg).rjust(len(msg)+9))
            except gateway_helpers.TimeoutError:
                logger.debug("exception in reading acquisition setting: %s" % key,
                             exc_info=True)
                msg =  "Failed to read acquisition setting {}".format(key)
                self._log_activity(msg, level='warning')
                raise ReadSettingsError
            except Exception:
                logger.error("exception in reading acquisition setting: %s" % key,
                             exc_info=True)
                tlogger.error("exception in reading acquisition setting: %s" % key,
                             exc_info=True)
                msg =  "Failed to read acquisition setting {}".format(key)
                self._log_activity(msg, level='warning')
                raise ReadSettingsError
        return self.acq_dict

    def _set_acquisition(self, acq_dict):
        self._validate_acq_dict(acq_dict)
        for key in acq_dict:
            self.set_adders += 1
            if key == 'analog_sample_rate':
                pass
            else:
                try:
                    self.set_acquisition_wrapper(self.instr.acquisition, key, acq_dict[key])
                    tlogger.info("Programming the acquisition setting %s to %s " % (key, acq_dict[key]))
                except gateway_helpers.TimeoutError:
                    logger.error("Failed to write acquisition setting %s to %s " % (key, acq_dict[key]), exc_info = True)
                    tlogger.error("Failed to write acquisition setting %s to %s " % (key, acq_dict[key]), exc_info = True)
                    msg =  "Failed to write acquisition setting %s to %s " % (key, acq_dict[key])
                    self._log_activity(msg, level='warning')
                    raise WriteSettingsError
                except Exception:
                    logger.error("Failed to write acquisition setting %s to %s " % (key, acq_dict[key]), exc_info = True)
                    tlogger.info("Failed to write acquisition setting %s to %s " % (key, acq_dict[key]), exc_info = True)
                    msg =  "Failed to write acquisition setting %s to %s " % (key, acq_dict[key])
                    self._log_activity(msg, level='warning')
                    raise WriteSettingsError

    def check_any_channel_enabled(self):
        """Checks if any channel is enabled. If none, return False"""
        channels_enabled = []
        logger.info("checking channels enabled in rigol scope driver")
        tlogger.info("checking channels enabled in rigol scope driver")
        for channel in self.instr.channels[0:4]:
            if channel.enabled:
                channels_enabled.append(channel.name)
        # if bool(int(self.instr._ask(":LA:STAte?"))):
        #     for channel in self.instr.channels[4:]:
        #         try:
        #             if channel.enabled:
        #                 channels_enabled.append(channel.name)
        #         except Exception:
        #             logger.debug("check any digital channel enabled", exc_info=True)
        logger.info("check_any_channel_enabled() channels_enabled: {}"
                    .format(channels_enabled))
        if channels_enabled:
            tlogger.info("Capture command does not load a config. Check channel enabled is: %s" % channels_enabled)
            return True
        else:
            logger.warning('No Channels Enabled')
            tlogger.info("Capture command does not load a config. No channels enabled.")
            return False

    def get_timebase(self):
        logger.debug("getting timebase")
        tlogger.info("Getting timebase data from the instrument")
        timebase = collections.defaultdict(int)
        try:
            timebase['position'] = self.timebase_position_wrapper()
            msg = ("Timebase position is %s " % (timebase['position']))
            tlogger.info((msg).rjust(len(msg)+9))
        except gateway_helpers.TimeoutError:
            logger.debug("get timebase position exception", exc_info=True)
            tlogger.debug("get timebase position exception", exc_info=True)
            msg =  "Failed to read timebase setting:  position setting"
            self._log_activity(msg, level='warning')
            raise ReadSettingsError
        except Exception:
            logger.debug("get timebase position exception", exc_info=True)
            tlogger.debug("get timebase position exception", exc_info=True)
            msg =  "Failed to read timebase setting:  position setting"
            self._log_activity(msg, level='warning')
            raise ReadSettingsError
        try:
            timebase['scale'] = self.instr.timebase.scale
            msg = ("Timebase scale is %s " % (timebase['scale']))
            tlogger.info((msg).rjust(len(msg)+9))
        except gateway_helpers.TimeoutError:
            logger.debug("get timebase scale exception", exc_info=True)
            tlogger.debug("get timebase scale exception", exc_info=True)
            msg =  "Failed to read timebase setting:  scale setting"
            self._log_activity(msg, level='warning')
            raise ReadSettingsError
        except Exception:
            logger.debug("get timebase scale exception", exc_info=True)
            tlogger.debug("get timebase scale exception", exc_info=True)
            msg =  "Failed to read timebase setting:  scale setting"
            self._log_activity(msg, level='warning')
            raise ReadSettingsError
        return timebase

    def fetch_raw_setup(self, last_try=False):
        try:
            raw_setup = super(RigolScope, self).fetch_raw_setup(last_try=True)
        except gateway_helpers.TimeoutError:
            msg = "Failed to read raw setup due to a timeout error"
            self._log_activity(msg, level='warning')
            tlogger.error(msg)
            return None
        except Exception:
            self.logger.warning("fetch setup failed", exc_info=True)
            tlogger.info("Fetch setup failed")
            if last_try:
                msg = "Failed to read raw setup due to an unknown error"
                self._log_activity(msg, level='warning')
                tlogger.error(msg)
                raise ReadSettingsError
                return None
            else:
                raw_setup = super(RigolScope, self).fetch_raw_setup(last_try=True)
        if raw_setup is None:
            return None
        else:
            return raw_setup.encode('hex')

    def load_raw_setup(self, try_count=0):
        logger.debug("loading raw setup")
        hex_config = self.config['info']['raw_setup'].decode('hex')
        try:
            self.system_load_setup_wrapper(hex_config)
        except gateway_helpers.TimeoutError:
            logger.debug("Load setup failed", exc_info=True)
            tlogger.info("Load setup failed")
            msg = "Loading setup timed out"
            self._log_activity(msg, level='warning')
        except Exception:
            self.logger.warning("failed loading raw setup", exc_info=True)
            if try_count > 3:
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

    def _setinstr_with_tries(self, ivi_obj, key, value, label='', tries=3):
        for attempt in range(tries):
            try:
                if key == 'number_of_points_minimum':
                    self.instr._write(":run")
                    time.sleep(1)
                    setattr(ivi_obj, key, value)
                    self.instr._write(":stop")
                else:
                    setattr(ivi_obj, key, value)
                self.config_scorecard['success'].append(label + key)
                return
            except usb.core.USBError as e:
                logger.debug("USB Error in setting instrument", exc_info=True)
                self.handle_usb_error(e)
            except Exception:
                logger.debug("failed to set instrument: %s %s" %
                             (key, value), exc_info=True)
                self.exception_count += 1
                time.sleep(0.1)
        self.config_scorecard['failure'].append(label + key)
        raise WriteSettingsError

    def _fetch_waveform(self, channel_name):
        try:
            self.instr._write(":WAVeform:MODE RAW")
            msg = ("Setting the Rigol waveform mode to :MODE RAW")
            tlogger.info((msg).rjust(len(msg)+9))
        except Exception:
            logger("exception in setting waveform mode raw", exc_info=True)
            tlogger.info("exception in setting waveform mode raw", exc_info=True)
        try:
            super(RigolScope, self)._fetch_waveform(channel_name)
        except gateway_helpers.TimeoutError as e:
            self.logger.error("TimeoutError {} while fetching waveform from Rigol".format(e))
            logger.debug("Fetch waveform failed", exc_info=True)
            tlogger.info("Fetch waveform failed", exc_info=True)
            msg =  "Fetch waveform failed for %s " % channel_name
            self._log_activity(msg, level='warning')
            raise FetchWaveformError('channel error {}'.format(channel_name))
        except Exception as e:
            self.logger.error("Non-specific except {} . Encountered while fetching waveform from Rigol".format(e))
            self.logger.warning("failed to fetch waveform for: %s"
                                % channel_name, exc_info=True)
            tlogger.info("failed to fetch waveform for: %s" % channel_name)
            msg =  "Fetch waveform failed for %s " % channel_name
            self._log_activity(msg, level='warning')
            raise FetchWaveformError('channel error {}'.format(channel_name))
        trigger_level = 0
        try:
            trigger_level = self.instr.trigger.level
            self.metadata['trigger_level'] = trigger_level
            msg = ("Trigger level for waveform fetch is %s" % trigger_level)
            tlogger.info((msg).rjust(len(msg)+9))
        except Exception:
            logger("exception in getting trigger_level", exc_info=True)
            tlogger.info("exception in getting trigger_level", exc_info=True)
        for channel in self.channels:
            try:
                channel['trigger_level'] = trigger_level
            except Exception:
                logger("exception in getting trigger_level", exc_info=True)
        return self.metadata

    def check_instrument_ready(self):
        """Simply returns True since the Rigol has no busy? check"""
        time.sleep(1)

    def load_quickset(self):
        """loads autoset/autoscale command to scope, then executes channel check"""
        tlogger.info("Loading quickset config")
        self.set_autoscale()
        time.sleep(5)
        channels_enabled = []
        for ch in self.channel_names:
            if self.instr.channels[self.ch_idx_dict[ch]].enabled:
                channels_enabled.append(ch)
        if channels_enabled:
            num_of_channels_enabled = len(channels_enabled)
            points_setting = self.mem_depth_lookups[num_of_channels_enabled]
            self.instr.acquisition.number_of_points_minimum = points_setting
            time.sleep(0.5)
            return True
        else:
            logger.warning('No Channels Enabled')
            return False

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
        tlogger.info("ce-dict channels is %s" % self.ce_dict['channels'])
        for channel in self.ce_dict['channels'][:4]:
            ch = channel['name']
            ch_dict = collections.defaultdict(str)
            logger.debug("requesting channel enabled data for %s" % ch)
            ch_idx = self.ch_idx_dict[ch]
            try:
                ch_dict['enabled'] = self._channel_enabled_wrapper(self.ivi_channels, ch_idx)
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
                    tlogger.info((msg).rjust(len(msg)+9))
                    try:
                        ch_dict['range'] = self.channel_range_wrapper(self.ivi_channels, ch_idx)
                    except gateway_helpers.TimeoutError:
                        logger.debug("exception in timeout channel range for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel range for %s" % ch,
                                     exc_info=True)
                        msg =  "Failed to get channel range for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    except Exception:
                        logger.debug("exception in timeout channel range for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel range for %s" % ch,
                                     exc_info=True)
                        msg =  "Failed to get channel range for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    time.sleep(0.1)
                    try:
                        ch_dict['coupling'] = self.channel_coupling_wrapper(self.ivi_channels, ch_idx)
                    except gateway_helpers.TimeoutError:
                        logger.debug("exception in timeout channel coupling for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel coupling for %s" % ch,
                                     exc_info=True)
                        msg =  "Failed to get channel coupling for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    except Exception:
                        logger.debug("exception in timeout channel coupling for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel coupling for %s" % ch,
                                     exc_info=True)
                        msg =  "Failed to get channel coupling for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    time.sleep(0.1)
                    try:
                        ch_dict['scale'] = self.channel_scale_wrapper(self.ivi_channels, ch_idx)
                    except gateway_helpers.TimeoutError:
                        logger.debug("exception in timeout channel scale for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel scale for %s" % ch,
                                     exc_info=True)
                        msg =  "Failed to get channel scale for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    except Exception:
                        logger.debug("exception in timeout channel scale for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel scale for %s" % ch,
                                     exc_info=True)
                        msg =  "Failed to get channel scale for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    time.sleep(0.1)
                    try:
                        ch_dict['offset'] = self.channel_offset_wrapper(self.ivi_channels, ch_idx)
                    except gateway_helpers.TimeoutError:
                        logger.debug("exception in timeout channel offset for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel offset for %s" % ch,
                                     exc_info=True)
                        msg =  "Failed to get channel offset for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    except Exception:
                        logger.debug("exception in timeout channel offset for %s" % ch,
                                     exc_info=True)
                        tlogger.debug("exception in timeout channel offset for %s" % ch,
                                     exc_info=True)
                        msg =  "Failed to get channel offset for %s " % ch
                        self._log_activity(msg, level='warning')
                        raise ReadSettingsError
                    time.sleep(0.1)
                if ch not in self.enabled_list:
                    self.enabled_list.append(ch)
            else:
                logger.debug("response: %s NOT enabled" % ch)
                msg = ("%s NOT enabled" % ch)
                tlogger.info((msg).rjust(len(msg)+9))
            self._update_channels(channels, ch_dict)
        # if bool(int(self.instr._ask(":LA:STAte?"))):
        #     print 'in the digital section'
        #     for channel in self.ce_dict['channels'][4:]:
        #         ch = channel['name']
        #         ch_dict = collections.defaultdict(str)
        #         logger.debug("requesting channel enabled data for %s" % ch)
        #         ch_idx = self.ch_idx_dict[ch]
        #         try:
        #             ch_dict['enabled'] = self.ivi_channels[ch_idx].enabled
        #         except Exception:
        #             logger.debug("get excerpt channel: channel enabled", exc_info=True)
        #         time.sleep(0.1)
        #         if ch_dict['enabled']:
        #             logger.debug("response %s enabled" % ch)
        #             try:
        #                 ch_dict['name'] = self.ivi_channels[ch_idx].name
        #             except Exception:
        #                 logger.debug("get excerpt channel: channel name", exc_info=True)
        #             if ch in self._digital_channel_names:
        #                 try:
        #                     ch_dict['range'] = self.ivi_channels[ch_idx].range
        #                 except Exception:
        #                     logger.debug("get excerpt channel: range", exc_info=True)
        #                 time.sleep(0.1)
        #                 try:
        #                     ch_dict['coupling'] = self.ivi_channels[ch_idx].coupling
        #                 except Exception:
        #                     logger.debug("get excerpt channel: coupling", exc_info=True)
        #                 time.sleep(0.1)
        #                 try:
        #                     ch_dict['scale'] = self.ivi_channels[ch_idx].scale
        #                 except Exception:
        #                     logger.debug("get excerpt channel: scale", exc_info=True)
        #                 time.sleep(0.1)
        #                 try:
        #                     ch_dict['offset'] = self.ivi_channels[ch_idx].offset
        #                 except Exception:
        #                     logger.debug("get excerpt channel: offsest", exc_info=True)
        #                 time.sleep(0.1)
        #             if ch not in self.enabled_list:
        #                 self.enabled_list.append(ch)
        #         else:
        #             logger.debug("response: %s NOT enabled" % ch)
        config_excerpt['channels'] = channels
        # sync up excerpt list with driver list
        self.ce_dict['enabled_list'] = self.enabled_list
        config_excerpt['enabled_list'] = self.enabled_list
        #tlogger.info("Enabled channel list is %s " % config_excerpt['enabled_list'])
        return config_excerpt

    def _set_enabled_list(self):
        self.enabled_list = []  # resets enabled list
        if settings.SIMULATED:
            self.enabled_list = ['chan1']
            return
        tlogger.info("self.channels names is %s" % self.channel_names)
        for ch in self.channel_names[:4]:
            channel_idx = self.ch_idx_dict[ch]
            try:
                if self.instr.channels[channel_idx].enabled:
                    self.enabled_list.append(ch)
            except Exception:
                logger.debug("set enabled list %s", ch, exc_info=True)
        if self.capture_mode:
            for ch in self.enabled_list:
                channel = collections.defaultdict(int)
                channel['name'] = ch
                channel['enabled'] = True
                self._update_channels(self.ce_dict['channels'], channel)

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
            pod_final = self.pod_all
        elif 'pod1' in pod_tmp:
            pod_final = self.pod1_list
        else:
            pod_final = self.pod2_list
        for item in pod_final:
            logger.info("Fetching digital waveform for %s" % item)
            self._fetch_waveform_digital(item)

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

        if len(self.enabled_list) < 3:
            time.sleep(1)
        else:
            time.sleep(3)

        # Fetch the waveform for each channel enabled
        tlogger.info("Fetching analog waveforms for all enabled channels")
        for ch in self.enabled_list:
            if ch in self._analog_channel_names:
                self._fetch_waveform(ch)
        for ch in self.enabled_list:
            if ch in self._digital_channel_names:
                    self._fetch_waveform_digital(ch)



        # TODO: add dlogging
        # tlogger.info("Assigning PODs for waveforms")
        # self._handle_pods()

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


    def get_digital_list(self, waveform=[]):
        logger.debug("getting voltage_list ")
        voltage_list = [int((point[1])) for point in waveform]
        return voltage_list

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
            self.instr._write(":WAVeform:MODE NORMAL")
        except Exception as e:
            self.logger.warning(e, exc_info=True)
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
            waveform = list(ivi_channel.measurement.fetch_waveform())
        except Exception as e:
            self.logger.warning("failed to fetch digital waveform for: {} error: {}"
                                .format(channel_name,e), exc_info=True)
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
        voltage_list = self.get_digital_list(waveform)
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

    def _set_digital_channels(self, digital_chan_dict, digital_chan_enable):
        try:
            if digital_chan_enable == True:
                self.instr._write(":LA:STAte 1")
            else:
                self.instr._write(":LA:STAte 0")
        except Exception as e:
            logger.debug(e, exc_info=True)
        for channel in digital_chan_dict:
            logger.info("digital channel %s" % channel)
            try:
                self.instr._write(":LA:DIGital:DISPlay %s, %s" % (channel, int(digital_chan_dict[channel]['enabled'])))
            except Exception:
                logger.debug("Setting digital channels ", exc_info=True)


    def get_digital_channels(self):
        digital_channels = {}
        digital_channels_enable = ""
        if bool(int(self.instr._ask(":LA:STAte?"))):
            digital_channels_enable = True
            for channel in self.instr.channels._indicies[2:]:
                try:
                    value = bool(int(self.instr._ask(":LA:Digital:Display? %s" % channel)))
                    digital_channels[channel.upper()]={"enabled":value}
                except Exception:
                    logger.debug("check any digital channel enabled", exc_info=True)
        else:
            digital_channels_enable = False
        logger.info("digital channels: {}"
                    .format(digital_channels))
        return digital_channels, digital_channels_enable

    def _set_digital_thresholds(self, digital_threshold_dict):
        try:
            if digital_threshold_dict['digital_threshold_d0_d7']:
                self.instr._write(":LA:POD1:THRESHOLD %s" % digital_threshold_dict['digital_threshold_d0_d7'])
        except Exception as e:
            logger.debug(e, exc_info=True)
        try:
            if digital_threshold_dict['digital_threshold_d8_d15']:
                self.instr._write(":LA:POD2:THRESHOLD %s" % digital_threshold_dict['digital_threshold_d8_d15'])
        except Exception as e:
            logger.debug(e, exc_info=True)

    def get_digital_threshold(self):
        digital_threshold = {}
        digital_threshold['digital_threshold_d0_d7'] = float(self.instr._ask(":LA:POD1:THRESHOLD?"))
        digital_threshold['digital_threshold_d8_d15'] = float(self.instr._ask(":LA:POD2:THRESHOLD?"))
        return digital_threshold

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

    def get_outputs(self, index=0):
        logger.debug("getting outputs")
        outputs = None
        output_list = []
        for i in self.instr._output_name:
            index = self.instr._output_name.index(i)
            try:
                outputs = self.get_outputs_wrapper(index)
            except Exception:
                logger.debug("getting outputs exception")
            except gateway_helpers.TimeoutError:
                logger.debug("exception in timeout get outputs",
                             exc_info=True)
            tmp_output_dict = {
                'impedance': '',
                'enabled': '',
                'name': '',
            }
            # if not outputs:
            #     return tmp_output_dict

            for key in tmp_output_dict:
                try:
                    tmp_output_dict[key] = self.get_output_settings_wrapper(
                        outputs, key)
                    logger.debug("output from instr: %s %s" %
                                 (key, tmp_output_dict[key]))
                except gateway_helpers.TimeoutError:
                    logger.debug("exception in timeout get output settings",
                                 exc_info=True)
            output_list.append(tmp_output_dict)
        standard_waveform_list = []
        for i in self.instr._output_name:
            index = self.instr._output_name.index(i)
            standard_waveform_dict = self.get_standard_waveform(index)
            standard_waveform_dict['name'] = i
            standard_waveform_list.append(standard_waveform_dict)
        return output_list, standard_waveform_list

    def set_outputs(self, output_dict):
        index = self.instr._output_name.index(output_dict['name'])
        output = self.instr.outputs[index]
        for key in output_dict:
            if key == '$$hashKey' or key == 'name':
                continue
            try:
                self.set_outputs_wrapper(output, key, output_dict[key])
                tlogger.info("Programming the AFG output setting %s to %s " % (
                    key, output_dict[key]))
            except gateway_helpers.TimeoutError:
                logger.debug(
                    "Standard waveform outputs setting failed", exc_info=True)
                tlogger.info(
                    "Standard waveform outputs setting failed", exc_info=True)

    def set_standard_waveform(self, output_dict, waveform_dict):
        logger.debug("set standard_waveform")
        index = self.instr._output_name.index(output_dict['name'])
        try:
            standard_waveform = self.standard_waveform_wrapper(index)
        except gateway_helpers.TimeoutError:
            logger.debug("Standard waveform failed", exc_info=True)
            tlogger.info("Standard waveform failed", exc_info=True)
        if not standard_waveform:
            logger.debug("no standard_waveform to set")
            return False

        for key in waveform_dict:
            if key == 'name':
                continue
            try:
                self.set_standard_waveform_wrapper(
                    standard_waveform, key, waveform_dict[key])
                tlogger.info("Programming the standard waveform setting %s to %s " % (
                    key, waveform_dict[key]))
            except gateway_helpers.TimeoutError:
                logger.debug("Standard waveform setting failed", exc_info=True)
                tlogger.info("Standard waveform setting failed", exc_info=True)
        return True

    def set_autoscale(self):
        """issues autoscale command"""
        try:
            self.instr._write(":system:autoscale ON")
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
