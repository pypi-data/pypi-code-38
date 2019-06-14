# -*- coding: utf-8 -*-

import sys
from time import time
from datetime import timedelta

__author__ = "Daniel Scheffler"


class Timer(object):
    def __init__(self, timeout=None, use_as_callback=False):
        self.starttime = time()
        self.endtime = self.starttime + timeout if timeout else None
        self.use_as_cb = use_as_callback

    @property
    def timed_out(self):
        if self.endtime:
            if time() > self.endtime:
                if self.use_as_cb:
                    raise KeyboardInterrupt
                else:
                    return True
            else:
                if self.use_as_cb:
                    pass
                else:
                    return False
        else:
            return False

    @property
    def elapsed(self):
        return str(timedelta(seconds=time() - self.starttime)).split('.')[0]
        # return '%.2f sek' %(time()-self.starttime)

    def __call__(self, percent01, message, user_data):
        """This allows that Timer instances are callable and thus can be used as callback function,
        e.g. for GDAL.

        :param percent01:   this is not used but expected when used as GDAL callback
        :param message:     this is not used but expected when used as GDAL callback
        :param user_data:   this is not used but expected when used as GDAL callback
        :return:
        """
        return self.timed_out


class ProgressBar(object):
    def __init__(self, prefix='', suffix='Complete', decimals=1, barLength=50, show_elapsed=True,
                 timeout=None, use_as_callback=False, out=sys.stderr):
        """Call an instance of this class in a loop to create terminal progress bar. This class can also be used as
        callback function, e.g. for GDAL. Just pass an instance of ProgressBar to the respective callback keyword.

        :param prefix:         prefix string (Str)
        :param suffix:         suffix string (Str)
        :param decimals:       positive number of decimals in percent complete (Int)
        :param barLength:      character length of bar (Int)
        :param show_elapsed:   displays the elapsed time right after the progress bar (bool)
        :param timeout:        breaks the process after a given time in seconds (float)

        http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
        """
        self.prefix = prefix
        self.suffix = suffix
        self.decimals = decimals
        self.barLength = barLength
        self.show_elapsed = show_elapsed
        self.Timer = Timer(timeout=timeout)
        self.use_as_cb = use_as_callback
        self.out = out

    def print_progress(self, percent):
        """Based on http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console

        :param percent: <float> a number between 0 and 100
        :return:
        """
        if self.Timer.timed_out:
            self.out.flush()
            if self.use_as_cb:
                raise KeyboardInterrupt

        formatStr = "{0:." + str(self.decimals) + "f}"
        percents = formatStr.format(percent)
        filledLength = int(round(self.barLength * percent / 100))
        # bar         = '█' * filledLength + '-' * (barLength - filledLength) # this is not compatible to shell console
        bar = '=' * filledLength + '-' * (self.barLength - filledLength)

        # reset the cursor to the beginning of the line and allows to write over what was previously on the line
        self.out.write('\r')

        # [%s/%s] numberDone
        suffix = self.suffix if not self.show_elapsed else '%s  => %s' % (self.suffix, self.Timer.elapsed)
        self.out.write('%s |%s| %s%s %s' % (self.prefix, bar, percents, '%', suffix))

        if percent >= 100.:
            self.out.write('\n')

        self.out.flush()

    def __call__(self, percent01, message, user_data):
        """This allows that ProgressBar instances are callable and thus can be used as callback function,
        e.g. for GDAL.

        :param percent01:   a float number between 0 and 1
        :param message:     this is not used but expected when used as GDAL callback
        :param user_data:   this is not used but expected when used as GDAL callback
        :return:
        """
        self.print_progress(percent01 * 100)


def tqdm_hook(t):
    """
    Wraps tqdm instance. Don't forget to close() or __exit__()
    the tqdm instance once you're done with it (easiest using `with` syntax).

    Example
    -------

    > with tqdm(...) as t:
    ...  reporthook = my_hook(t)
    ...  urllib.urlretrieve(..., reporthook=reporthook)

    http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    """
    last_b = [0]

    def inner(b=1, bsize=1, tsize=None):
        """
        b  : int, optional
            Number of blocks just transferred [default: 1].
        bsize  : int, optional
            Size of each block (in tqdm units) [default: 1].
        tsize  : int, optional
            Total size (in tqdm units). If [default: None] remains unchanged.
        """
        if tsize is not None:
            t.total = tsize
        t.update((b - last_b[0]) * bsize)
        last_b[0] = b

    return inner


def printPercentage(i, i_total):
    """Prints a percentage counter from within a loop.

    Example:
    for i in range(100+1):
        time.sleep(0.1)
        printPercentage(i)

    :param i:
    :param i_total:
    :return:

    http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    """
    sys.stdout.write(('=' * i) + ('' * (i_total - i)) + ("\r [ %d" % i + "% ] "))
    sys.stdout.flush()
