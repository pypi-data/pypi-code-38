import collections
from tektronix_scope import TektronixScope
from gateway_helpers import logger


class TektronixMSO5204B(TektronixScope):

    def __init__(self, command, instrument=None):
        TektronixScope.__init__(self, command, instrument=None)
        self.acq_dict = {
            'type': '',
            'start_time': '',
            'number_of_averages': '',
            'number_of_envelopes': '',
            'sample_rate': '',
            'time_per_record': '',
            'record_length': '',
        }
        if 'horizontal' in self.ce_dict:
            data = self.ce_dict['horizontal']
            self.horiz_dict = collections.defaultdict(int, data)
        else:
            logger.warning("MSO5204B missing 'horizontal' in config")
            self.horiz_dict = collections.defaultdict(int)
        self._analog_channel_names = self.channel_names[:4]
        self._digital_channel_names = self.channel_names[4:]


    def fetch_raw_setup(self, last_try=False):
        raw_setup = super(RigolScope, self).fetch_raw_setup()
        return "PLACEHOLDER FOR SETUP"

    def load_raw_setup(self, try_count=0):
        logger.debug("passing on loading raw setup")
        pass

    def load_special_config_fields(self):
        self._set_timebase()

    def _set_acquisition(self, acq_dict):
        self._validate_acq_dict(acq_dict)
        try:
            if self.horiz_dict['sample_rate']:
                acq_dict['sample_rate'] = self._sample_rate_lookup(
                    self.horiz_dict['sample_rate'])
        except Exception as e:
            logger.debug(e, exc_info=True)

        for key in acq_dict:
            self.set_adders += 1

            # should these be removed from the input config on the server? TS
            if key == 'number_of_points_minimum':
                pass
            elif key == 'time_per_record':
                pass
            elif key == 'record_length':
                pass
            else:
                self._setinstr_with_tries(self.instr.acquisition, key,
                                          acq_dict[key], label='acquisition_',
                                          tries=3)

    def _get_config_excerpt_extras(self):
        extras = {}
        extras['timebase'] = self.get_timebase()
        return extras

    def get_timebase(self):
        timebase = collections.defaultdict(int)
        try:
            timebase['position'] = self.instr.timebase.position
        except Exception:
            logger.debug("get timebase position exception")
        try:
            timebase['scale'] = self.instr.timebase.scale
        except Exception:
            logger.debug("get timebase scaleexception")
        return timebase

    def _set_timebase(self):
        timebase_dict = collections.defaultdict(str)
        try:
            if self.horiz_dict['scale']:
                scale_string = self.horiz_dict['scale']
                timebase_dict['scale'] = self._scale_lookup(scale_string)
        except Exception as e:
            logger.debug(e, exc_info=True)
        for key in timebase_dict:
            self.set_adders += 1
            self._setinstr_with_tries(self.instr.timebase, key,
                                      timebase_dict[key], label='timebase_',
                                      tries=3)

    def _sample_rate_lookup(self, scale_string):
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

    def _scale_lookup(self, value):
        value = value[0]
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


if __name__ == "__main__":
    data = {'info': {'instrument_type': 'TektronixDPO3014'}}
    command = collections.defaultdict(str, data)
    tester = TektronixMSO5204B(command=command)
    tester.test()
