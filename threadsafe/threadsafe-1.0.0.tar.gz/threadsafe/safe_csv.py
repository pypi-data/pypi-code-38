import csv

from threading import Lock

class SafeDictWriter:
    def __init__(self, *args, **kwds):
        self._writer = csv.DictWriter(*args, **kwds)
        self._mutex = Lock()

    def writeheader(self):
        with self._mutex:
            self._writer.writeheader()

    def writerow(self, rowdict):
        with self._mutex:
            self._writer.writerow(rowdict)

    def writerows(self, rowdicts):
        with self._mutex:
            self._writer.writerows(rowdicts)
