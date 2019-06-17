import tektronix_parent_path
from base import ReadSettingsError, WriteSettingsError, FetchScreenshotError
from base import FetchWaveformError, FetchMeasurementError
from base import t_diagnostic_logger as tlogger
from gateway_helpers import timeout
import collections
from gateway_helpers import dt2ms, round_sig, logger
import time


tektronix_parent_path.insert()

from scope_driver import ScopeDriver


class TektronixScope(ScopeDriver):

    def __init__(self, *args, **kwargs):
        super(TektronixScope, self).__init__(*args, **kwargs)
        self.channel_settings = ['scale', 'offset', 'position', 'coupling']

        self.pod1_list = []
        self.pod2_list = []
        self._horizontal_divisions = 10
        self._vertical_divisions = 8
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
                {
                    'ivi_name': 'duty_cycle_negative',
                    'display_name': 'Duty Cycle Negative',
                    'units': 's',
                },
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

    def _get_config_excerpt_extras(self):
        """Get fields beyond the base config excerpt"""
        extras = {}
        extras['horizontal'] = self.get_timebase()
        return extras


    def get_timebase(self):
        timebase = collections.defaultdict(int)
        logger.debug("getting timebase")
        try:
            timebase['position'] = self.timebase_position_wrapper()
            tlogger.info("Timebase position is %s " % (timebase['position']))
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
            timebase['scale'] = self.timebase_scale_wrapper()
            tlogger.info("Timebase scale is %s " % (timebase['scale']))
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
            self.instr.acquisition.number_of_points_minimum = 1000
            time.sleep(0.5)
            return True
        else:
            logger.warning('No Channels Enabled')
            return False