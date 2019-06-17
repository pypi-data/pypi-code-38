from keysight_scope import KeysightScope


class KeysightMSO9064A(KeysightScope):

    def __init__(self, setup, instrument):
        super(KeysightMSO9064A, self).__init__(setup, instrument)
        self._vertical_divisions = 8
        self._horizontal_divisions = 10

    def _set_divisions(self, h_divs=10, v_divs=8):
        super(KeysightScope, self)._set_divisions(h_divs=h_divs, v_divs=v_divs)
