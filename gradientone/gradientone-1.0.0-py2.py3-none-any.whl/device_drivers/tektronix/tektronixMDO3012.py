from tektronix_scope import TektronixScope


class TektronixMDO3012(TektronixScope):

    def __init__(self, command, instrument=None):
        TektronixScope.__init__(self, command, instrument)
        self._analog_channel_names = self.channel_names[:2]
        self._digital_channel_names = self.channel_names[2:]
        self._vertical_divisions = 8
        self._horizontal_divisions = 10

    def _set_divisions(self, v_divs=8, h_divs=10):
        self._vertical_divisions = v_divs
        self._horizontal_divisions = h_divs

    def test(self):
        print("TektronixMDO3012 analog channel_names: {}".format(
              self._analog_channel_names))


if __name__ == "__main__":
    import collections
    data = {'info': {'instrument_type': 'TektronixMDO3012'}}
    command = collections.defaultdict(str, data)
    tester = TektronixMDO3012(command=command)
    tester.test()
