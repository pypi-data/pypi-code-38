"""
Module for writing WashU Epigenome Browser-style interaction data files.
"""

from lib5c.util.system import check_outdir


def write_wustl(counts, outfile, pixelmap):
    """
    Writes a WashU Epigenome Browser-style interaction data file.

    Parameters
    ----------
    counts : dict of 2d arrays
        The counts to be written. The keys are the region names. The values are
        the arrays of counts values for that region. These arrays should be
        square and symmetric.
    outfile : str
        String reference to the file to write counts to.
    pixelmap : dict of lists of dicts
        The keys of the outer dict are region names. The values are lists, where
        the ``i`` th entry represents the ``i`` th bin in that region. Bins are
        represented as dicts with the following structure::

            {
                'chrom': str,
                'start': int,
                'end'  : int,
                'name' : str
            }

        See ``lib5c.parsers.get_pixelmap()``.
    """
    check_outdir(outfile)
    with open(outfile, 'wb') as handle:
        interaction_id = 1
        for region in counts:
            for i in range(len(counts[region])):
                left_bin = pixelmap[region][i]
                for j in range(len(counts[region])):
                    direction = '+'
                    if i == j:
                        continue
                    elif i > j:
                        direction = '-'
                    right_bin = pixelmap[region][j]
                    handle.write('%s\t%i\t%i\t%s:%i-%i,%s\t%i\t%s\n' %
                                 (left_bin['chrom'],
                                  left_bin['start'],
                                  left_bin['end'],
                                  right_bin['chrom'],
                                  right_bin['start'],
                                  right_bin['end'],
                                  counts[region][i, j],
                                  interaction_id,
                                  direction))
                    interaction_id += 1


# test client
def main():
    from lib5c.parsers.counts import load_counts
    from lib5c.parsers.primers import load_primermap
    pixelmap = load_primermap('test/bins.bed')
    counts = load_counts('test/test.counts')
    write_wustl(counts, 'test/wustl.txt', pixelmap)


if __name__ == "__main__":
    main()
