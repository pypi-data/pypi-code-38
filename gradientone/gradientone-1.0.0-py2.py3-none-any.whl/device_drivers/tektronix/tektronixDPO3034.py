from tektronix_scope import TektronixScope


class TektronixDPO3034(TektronixScope):

    def __init__(self, *args, **kwargs):
        super(TektronixDPO3034, self).__init__(*args, **kwargs)
        self._analog_channel_names = self.channel_names[:2]


if __name__ == "__main__":
    import collections
    data = {'info': {'instrument_type': 'TektronixDPO3034'}}
    command = collections.defaultdict(str, data)
    tester = TektronixDPO3034(command=command)
    tester.test()
