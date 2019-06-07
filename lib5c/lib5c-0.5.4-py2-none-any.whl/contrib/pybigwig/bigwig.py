"""
Module for interfacing with the external ``pyBigWig`` Python package, which
enables reading and searching genomic features from ``.bigwig`` files.
"""

import numpy as np


def bigwig_avail():
    """
    Utility function for checking if ``pyBigWig`` is installed.

    Returns
    -------
    bool
        True if ``pyBigWig`` is installed, otherwise False.
    """
    try:
        import pyBigWig  # noqa: F401
        return True
    except ImportError:
        return False


class BigWig(object):
    """
    Wrapper class around pyBigWig, mostly to expose our own `query()` function.

    Attributes
    ----------
    bw : pyBigWig object
        The underlying pyBigWig object.
    """
    def __init__(self, filename):
        if not bigwig_avail():
            raise ImportError('failed to import pyBigWig - is it installed?')
        import pyBigWig
        self.bw = pyBigWig.open(filename)

    def query(self, grange, stat='max', num_bins=None, exact=True):
        """
        Signature rework/wrapper around pyBigWig's `stats()` and `intervals()`.

        Parameters
        ----------
        grange : Dict[str, Any]
            The genomic range to query. Should have at least the following
            structure::

                {
                    'chrom': str,
                    'start': int,
                    'end': int
                }

        num_bins : Optional[int]
            Pass an integer to split `grange` into `num_bins` bins of equal
            width, and return a summary statistic for each bin. Pass None to
            return all bigwig features in `grange` without binning.
        stat : str
            The summary statistic to use if `num_bins` is not None.
        exact : bool
            Pass True to ignore bigwig zoom levels when computing summary
            statistics and return the exact answer instead.

        Returns
        -------
        List[Dict[str, Any]]
            A list of bed features with 'value' keys representing the results of
            the query.
        """
        if num_bins is not None:
            values = self.bw.stats(grange['chrom'], grange['start'],
                                   grange['end'], type=stat, nBins=num_bins,
                                   exact=exact)
            bin_width = (grange['end'] - grange['start']) / float(num_bins)
            features = [{'chrom': grange['chrom'],
                         'start': grange['start'] + int(i*bin_width),
                         'end': grange['start'] + int((i+1)*bin_width),
                         'value': values[i] if values[i] is not None
                         else np.nan}
                        for i in range(len(values))]
        else:
            intervals = self.bw.intervals(grange['chrom'], grange['start'],
                                          grange['end'])
            features = [{'chrom': grange['chrom'],
                         'start': interval[0],
                         'end': interval[1],
                         'value': interval[2]}
                        for interval in intervals]
        return features
