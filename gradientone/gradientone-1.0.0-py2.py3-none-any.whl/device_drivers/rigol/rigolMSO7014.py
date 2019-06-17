from rigol_scope import RigolScope


class RigolMSO7014(RigolScope):

    def __init__(self, command, instrument=None):
        super(RigolMSO7014, self).__init__(command, instrument)
        self._vertical_divisions = 8
        self._horizontal_divisions = 10

    def _set_divisions(self, h_divs=10, v_divs=8):
        super(RigolScope, self)._set_divisions(h_divs=h_divs, v_divs=v_divs)

    def test(self):
        print("vertical divisions {}, horizontal divisions {}".format(
            self._vertical_divisions, self._horizontal_divisions))


if __name__ == "__main__":
    import collections
    data = {'info': {'instrument_type': 'RigolMSO7014'}}
    command = collections.defaultdict(str, data)
    tester = RigolMSO7014(command=command)
    tester.test()
