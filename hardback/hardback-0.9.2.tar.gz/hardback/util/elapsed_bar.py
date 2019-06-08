import datetime
from progress.bar import ChargingBar


class ElapsedBar(ChargingBar):
    def __init__(self, msg='Working', *args, enable=True, **kwds):
        super().__init__(msg, *args, **kwds)
        self.__start_time = datetime.datetime.now()
        self.__index = 0
        self.__enable = enable

    def next_item(self, message):
        if not self.__enable:
            return

        self.__index += 1
        elapsed = datetime.datetime.now() - self.__start_time
        time_per_item = elapsed / self.__index
        remaining_items = 1 + (self.max - self.__index)
        remaining = time_per_item * remaining_items

        def fmt(t):
            return str(t).split('.', 1)[0]

        self.message = '%s %s elapsed, %s to go' % (
            message,
            fmt(elapsed),
            fmt(remaining),
        )

        self.next()
