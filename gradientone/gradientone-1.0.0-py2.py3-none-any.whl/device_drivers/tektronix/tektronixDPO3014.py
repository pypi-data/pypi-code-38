from tektronix_scope import TektronixScope


class TektronixDPO3014(TektronixScope):

    def __init__(self, *args, **kwargs):
        super(TektronixDPO3014, self).__init__(*args, **kwargs)
        self._analog_channel_names = self.channel_names[:4]


if __name__ == "__main__":
    import collections
    data = {'info': {'instrument_type': 'TektronixDPO3014'}}
    command = collections.defaultdict(str, data)
    tester = TektronixDPO3014(command=command)
    tester.test()
