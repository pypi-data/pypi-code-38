from rigol_scope import RigolScope
import gateway_helpers
from gateway_helpers import dt2ms, round_sig, logger
from base import t_diagnostic_logger as tlogger
from base import ReadSettingsError, WriteSettingsError, FetchScreenshotError
from base import FetchWaveformError, FetchMeasurementError
from gateway_helpers import timeout
import settings
import collections
import copy
import time


class RigolDS2000A(RigolScope):

    def __init__(self, command, instrument=None):
        super(RigolDS2000A, self).__init__(command, instrument)
        self._vertical_divisions = 8
        self._horizontal_divisions = 14
        self._analog_channel_names = self.channel_names[:2]
        logger.debug("DS2000A driver instantiated")

    def _set_divisions(self, h_divs=14, v_divs=8):
        super(RigolDS2000A, self)._set_divisions(h_divs=h_divs, v_divs=v_divs)

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

    def test(self):
        print("vertical divisions {}, horizontal divisions {}".format(
            self._vertical_divisions, self._horizontal_divisions))

    def _get_optional_features(self, extras):
        """To be overridden for each instruments optional features"""
        if 'waveform_generator' in self.command['info']['optional features']:
            extras['outputs'], extras['standard_waveform'] = self.get_outputs()
        return extras

    def _load_optional_features(self):
        """To be overridden for each instruments optional features"""
        if 'waveform_generator' in self.command['info']['optional features']:
            try:
                any_afg_enabled = []
                for i in self.ce_dict['outputs']:
                    if i['enabled']:
                        any_afg_enabled.append(i['name'])
                tlogger.info("Checking if any AFG is enabled")
            except KeyError:
                logger.debug("afg_enabled KeyError, setting False")
                any_afg_enabled = False
            try:
                for i in self.ce_dict['outputs']:
                    del i['impedance']
                    self.set_outputs(i)
            except:
                logger.warning("AFG Enabled, but exception setting output",
                                exc_info=True)
            if any_afg_enabled:
                logger.debug("afg_enabled is: %s" % str(any_afg_enabled))
                try:
                    for i in self.ce_dict['outputs']:
                        self.set_outputs(i)
                    for i in self.ce_dict['standard_waveform']:
                        output_dict_index = self.ce_dict['standard_waveform'].index(i)
                        logger.debug("output_dict_index %s " % str(output_dict_index))
                        self.set_standard_waveform(self.ce_dict['outputs'][output_dict_index], i)
                except:
                    logger.warning("AFG Enabled, but exception setting output",
                                    exc_info=True)
            else: 
                logger.debug("No AFG enabled")

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
        for channel in self.ce_dict['channels'][:2]:
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

if __name__ == "__main__":
    import collections
    data = {'info': {'instrument_type': 'RigolDS2000A'}}
    command = collections.defaultdict(str, data)
    tester = RigolDS2000A(command=command)
    tester.test()
