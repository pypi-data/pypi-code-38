from tektronix_scope import TektronixScope


class TektronixMDO4104(TektronixScope):

    def __init__(self, *args, **kwargs):
        super(TektronixMDO4104, self).__init__(*args, **kwargs)


if __name__ == "__main__":
    import collections
    data = {'info': {'instrument_type': 'TektronixMDO4104'}}
    command = collections.defaultdict(str, data)
    tester = TektronixMDO4104(command=command)
    tester.test()
