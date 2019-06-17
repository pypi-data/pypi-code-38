from rigol_scope import RigolScope


class RigolDS1054Z(RigolScope):

    def __init__(self, command, instrument=None):
        super(RigolDS1054Z, self).__init__(command, instrument)
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


if __name__ == "__main__":
    import collections
    data = {'info': {'instrument_type': 'RigolDS1054Z'}}
    command = collections.defaultdict(str, data)
    tester = RigolDS1054Z(command=command)
    tester.test()
