"""
Module for writing primermaps and pixelmaps to bedfiles.
"""

from lib5c.util.system import check_outdir


def write_primermap(primermap, outfile, extra_column_names=None):
    """
    Write a primermap to a primer bedfile.

    Parameters
    ----------
    primermap : Dict[str, List[Dict[str, Any]]]
        The primermap to write. See ``lib5c.parsers.primers.load_primermap()``.
    outfile : str
        String reference to the file to write to.
    extra_column_names : Optional[List[str]]
        Names of additional columns to include in the bedfile.
    """
    check_outdir(outfile)

    # check if the object to be written has strand information
    has_orientation = True \
        if 'orientation' in primermap[primermap.keys()[0]][0] else False

    with open(outfile, 'w') as handle:
        handle.write('#chrom\tstart\tend\tname')
        if has_orientation:
            handle.write('\torientation')
        if extra_column_names is not None:
            for column_name in extra_column_names:
                handle.write('\t%s' % column_name)
        handle.write('\n')
        for region in primermap.keys():
            for i in range(len(primermap[region])):
                handle.write('%s\t%i\t%i\t%s'
                             % (primermap[region][i]['chrom'],
                                primermap[region][i]['start'],
                                primermap[region][i]['end'],
                                primermap[region][i]['name']))
                if has_orientation:
                    handle.write('\t%s' % primermap[region][i]['orientation'])
                if extra_column_names is not None:
                    for column_name in extra_column_names:
                        handle.write('\t%s' % primermap[region][i][column_name])
                handle.write('\n')


def write_pixelmap_legacy(pixelmap, outfile):
    """
    Write a pixelmap to a bin bedfile.

    Parameters
    ----------
    pixelmap : Dict[str, List[Dict[str, Any]]]
        The pixelmap to write. See ``lib5c.parsers.primers.get_pixelmap()``.
    outfile : str
        String reference to the file to write to.
    """
    check_outdir(outfile)
    try:
        # if we have lib5c.core we can just construct a LocusMap
        from lib5c.core.loci import LocusMap
        lm = LocusMap.from_list_of_dict([pixelmap[region][i]
                                         for region in pixelmap.keys()
                                         for i in range(len(pixelmap[region]))])
        lm.to_bedfile(outfile)
    except ImportError:
        # fallback writer
        with open(outfile, 'w') as handle:
            for region in pixelmap.keys():
                for i in range(len(pixelmap[region])):
                    handle.write('%s\t%i\t%i\t%s\n'
                                 % (pixelmap[region][i]['chrom'],
                                    pixelmap[region][i]['start'],
                                    pixelmap[region][i]['end'],
                                    pixelmap[region][i]['name']))
