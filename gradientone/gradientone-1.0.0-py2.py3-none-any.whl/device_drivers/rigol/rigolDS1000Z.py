from rigol_scope import RigolScope
from gateway_helpers import logger
from base import t_diagnostic_logger as tlogger
import settings
import collections
import copy
import time


class RigolDS1000Z(RigolScope):

    def __init__(self, command, instrument=None):
        super(RigolDS1000Z, self).__init__(command, instrument)
        self._vertical_divisions = 8
        self._horizontal_divisions = 12
        self.channel_names = [c.name for c in self.ivi_channels]
        self._analog_channel_names = self.channel_names[:4]

    def _set_divisions(self, h_divs=12, v_divs=8):
        super(RigolScope, self)._set_divisions(h_divs=h_divs, v_divs=v_divs)

    def load_special_fields(self):
        if 'timebase' in self.ce_dict:
            self.set_timebase(self.ce_dict['timebase'])
        if 'horizontal' in self.ce_dict:
            self.set_timebase(self.ce_dict['horizontal'])


    def _get_config_excerpt_extras(self):
        """Get fields beyond the base config excerpt"""
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
                
if __name__ == "__main__":
    import collections
    data = {'info': {'instrument_type': 'RigolDS1000Z'}}
    command = collections.defaultdict(str, data)
    tester = RigolDS1000Z(command=command)
    tester.test()
