from tektronix_scope import TektronixScope


class TektronixMSO2024(TektronixScope):

    """overrides get_config_excerpt to skip outputs"""

    def __init__(self, *args, **kwargs):
        super(TektronixMSO2024, self).__init__(*args, **kwargs)
        self._analog_channel_names = self.channel_names[:4]
        self._digital_channel_names = self.channel_names[4:]
        self._vertical_divisions = 8
        self._horizontal_divisions = 10

    def _get_config_excerpt_extras(self):
        return {}

    def check_instrument_ready(self):
        """Simply return True, MSO2024 has no ask('busy?')"""
        return True

    def _set_divisions(self, v_divs=8, h_divs=10):
        self._vertical_divisions = v_divs
        self._horizontal_divisions = h_divs

    def _alt_get_acquisition(self):
        """Alternative to convert acq to valid values

           Use this if ivi starts returning weird values for
           acquisition again
        """
        for key in self.acq_dict:
            value = getattr(self.instr.acquisition, key)
            if key == 'time_per_record':
                value = self._convert_special_acq(value)
            self.acq_dict[key] = value
        return self.acq_dict

    def _convert_special_acq(self, value):
        if value < 100000:
            return value
        elif value < 500000:
            value = 100000
        elif value < 5000000:
            value = 1000000
        elif value < 50000000:
            value = 10000000
        else:
            return value
