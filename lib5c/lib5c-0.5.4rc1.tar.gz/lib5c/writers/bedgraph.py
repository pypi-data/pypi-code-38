"""
Module for writing bedgraph files.
"""

from lib5c.util.system import check_outdir


def write_bedgraph(peaks, outfile, name='', desc=''):
    """
    Writes a set of peaks to a bedgraph file.

    Parameters
    ----------
    peaks : dict of lists of dicts
        The peaks that should be written. The keys are chromosome names. The
        values are lists of features for that chromosome. The features are
        represented as dicts with at least the following keys::

            {
                'chrom': str
                'start': int,
                'end'  : int,
                'value': number
            }

    outfile : str
        String reference to the file to write to.
    name : str
        String to write in the name field of the header line.
    desc : str
        String to write in the description field of the header line.
    """
    check_outdir(outfile)
    with open(outfile, 'wb') as handle:
        # write header line
        handle.write('track type=bedGraph name="%s" description="%s"\n' %
                     (name, desc))

        # write remaining lines
        for chrom in peaks:
            for peak in peaks[chrom]:
                handle.write('%s\t%i\t%i\t%g\n' %
                             (chrom, peak['start'], peak['end'], peak['value']))


# test client
def main():
    from lib5c.util.bedgraph import reduce_bedgraph
    from lib5c.parsers.primers import get_pixelmap
    pixelmap = get_pixelmap('test/bins.bed')
    peaks = reduce_bedgraph('test/bedgraph.bed', pixelmap)
    write_bedgraph(peaks, 'test/reduced_bedgraph.bed')


if __name__ == "__main__":
    main()
