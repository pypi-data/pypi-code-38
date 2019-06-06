"""
Module for writing .counts files.
"""

import numpy as np

from lib5c.util.primers import aggregate_primermap
from lib5c.util.system import check_outdir


def write_counts(counts, outfile, primermap, skip_zeros=False):
    """
    Writes a standard counts file.

    Parameters
    ----------
    counts : dict of 2d arrays
        The counts to be written. The keys are the region names. The values are
        the arrays of counts values for that region. These arrays should be
        square and symmetric.
    outfile : str
        String reference to the file to write counts to.
    primermap : dict of lists of dicts
        The keys of the outer dict are region names. The values are lists, where
        the ``i`` th entry represents the ``i`` th primer or bin in that region.
        Primers or bins are represented as dicts with the following structure::

            {
                'chrom' : str,
                'start' : int,
                'end'   : int,
                'name'  : str,
                'orientation': "3'" or "5'"
            }

        The strand key is optional and only makes sense when writing
        primer-primer interaction counts. If present, impossible primer-primer
        combinations will be omitted from the output. See
        ``lib5c.parsers.primers.get_primermap()`` or
        ``lib5c.parsers.primers.get_pixelmap()``.
    skip_zeros : bool
        Pass True to omit writing output lines for bin-bin pairs with zero, nan,
        or empty string value.
    """
    check_outdir(outfile)
    if outfile.endswith('.npz'):
        np.savez(outfile, **counts)
        return
    with open(outfile, 'wb') as handle:
        for region in counts:
            for i in range(len(counts[region])):
                for j in range(i+1):
                    # skip impossible primer-primer combinations
                    if ('orientation' in primermap[region][i].keys() and
                            'orientation' in primermap[region][j].keys() and
                            primermap[region][i]['orientation'] ==
                            primermap[region][j]['orientation']):
                        continue
                    value = counts[region][i, j]
                    # skip zeros
                    if skip_zeros and (not value or (isinstance(value, float)
                                                     and np.isnan(value))):
                        continue
                    handle.write('%s\t%s\t%s\n' % (primermap[region][i]['name'],
                                                   primermap[region][j]['name'],
                                                   value))


def write_cis_trans_counts(counts, outfile, primermap, omit_zeros=True):
    """
    Writes a counts file including both the cis and trans counts.

    Parameters
    ----------
    counts : 2d numpy array
        The square, symmetric array of counts to be written. This must be a
        single matrix that contains the cis contacts for all regions as well as
        the trans contacts between them. The rows of the matrix must correspond
        to genomic loci in order of increasing genomic coordinate.
    outfile : str
        String reference to the file to write counts to.
    primermap : dict of lists of dicts
        The keys of the outer dict are region names. The values are lists, where
        the ``i`` th entry represents the ``i`` th primer or bin in that region.
        Primers or bins are represented as dicts with the following structure::

            {
                'chrom' : str,
                'start' : int,
                'end'   : int,
                'name'  : str,
                'orientation': "3'" or "5'"
            }

        The strand key is optional and only makes sense when writing
        primer-primer interaction counts. If present, impossible primer-primer
        combinations will be omitted from the output. See
        ``lib5c.parsers.primers.get_primermap()`` or
        ``lib5c.parsers.primers.get_pixelmap()``.
    omit_zeros : bool
        If True, lines will not be written to the outfile if the counts for that
        line are zero.
    """
    check_outdir(outfile)
    aggregated_primermap = aggregate_primermap(primermap)
    with open(outfile, 'wb') as handle:
        for i in range(len(aggregated_primermap)):
            for j in range(i+1):
                # skip impossible primer-primer combinations
                if ('orientation' in aggregated_primermap[i].keys() and
                        'orientation' in aggregated_primermap[j].keys()):
                    if aggregated_primermap[i]['orientation'] == \
                            aggregated_primermap[j]['orientation']:
                        continue

                # skip zeros
                if omit_zeros and counts[i, j] == 0:
                    continue

                # write line
                handle.write('%s\t%s\t%s\n' % (aggregated_primermap[i]['name'],
                                               aggregated_primermap[j]['name'],
                                               counts[i, j]))


# test client
def main():
    from lib5c.parsers.primers import load_primermap
    from lib5c.parsers.counts import load_counts
    pixelmap = load_primermap('test/bins.bed')
    counts = load_counts('test/test.counts', pixelmap)
    # pvalues = load_counts('test/pvalues.counts')
    write_counts(counts, 'test/test_written.counts', pixelmap)

    primermap = load_primermap('test/primers.bed')
    counts = load_counts('test/test_raw.counts', primermap)
    write_counts(counts, 'test/test_raw_cis.counts', primermap)


if __name__ == "__main__":
    main()
