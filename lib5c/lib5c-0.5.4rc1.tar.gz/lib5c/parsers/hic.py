"""
Module for parsing Hi-C data from the Rao et al. 2014 paper.
"""

import itertools
import warnings

import numpy as np

from lib5c.util.parallelization import parallelize_regions


@parallelize_regions
def load_range_from_contact_matrix(contact_matrix_file, grange, region_name='',
                                   norm_file=None):
    """
    Parses a chunk of contact information out of a Hi-C contact matrix file.

    The Hi-C contact matrix file format parsed by this function is the format
    used in the contact matrices uploaded to GEO for the Rao et al. 2014 paper.
    It is also the same format used by the Juicer tools dump command.

    Parameters
    ----------
    contact_matrix_file : str
        String reference to the Hi-C contact matrix file to parse.
    grange : Dict[str, Any]
        The genomic range to extract contact information for. This should be
        specified as a dict with the following structure::

            {
                'chrom': str,
                'start': int,
                'end': int
            }

    region_name : Optional[str]
        Name for this genomic region. If passed, it will be used to name the
        bins in the returned pixelmap.
    norm_file : Optional[str]
        String reference to a file containing a Hi-C bias vector corresponding
        to the ``contact_matrix_file``. If passed, the data will be normalized
        using this vector.

    Returns
    -------
    Tuple[np.ndarray, List[Dict[str, Any]]]
        The first element of the tuple is the extract counts matrix for the
        requested genomic range. The second element of the tuple is a pixelmap
        generated for this region describing the specific bins that were
        extracted.
    """
    # load normalization vector if provided
    norm_vector = []
    if norm_file is not None:
        with open(norm_file, 'r') as handle:
            for line in handle:
                norm_vector.append(float(line.strip()))

    with open(contact_matrix_file, 'r') as handle:
        # guess resolution based on first two lines
        lines = list(itertools.islice(handle, 2))
        resolution = abs(int(lines[1].split('\t')[0]) -
                         int(lines[0].split('\t')[0]))
        if resolution == 0:
            resolution = abs(int(lines[1].split('\t')[1]) -
                             int(lines[0].split('\t')[1]))

        # warn if rounding genomic range to resolution
        if grange['start'] % resolution:
            warnings.warn('rounding %s to next lowest bin' % grange['start'])
            grange['start'] = (grange['start'] / resolution) * resolution
        if grange['end'] % resolution:
            warnings.warn('rounding %s to next largest bin' % grange['end'])
            grange['end'] = (grange['end'] / resolution + 1) * resolution

        # compute coordinate transformation
        size = (grange['end'] - grange['start']) / resolution

        # initialize array
        array = np.zeros([size, size])

        # reset file position following islice call
        handle.seek(0)

        # parse
        for line in handle:
            pieces = line.strip().split('\t')
            left = int(pieces[0])
            right = int(pieces[1])
            if (grange['start'] <= left < grange['end']) and \
                    (grange['start'] <= right < grange['end']):
                value = float(pieces[2])
                if norm_vector:
                    factor = (norm_vector[left / resolution] *
                              norm_vector[right / resolution])
                    if np.isfinite(factor) and factor > 0:
                        value /= factor
                array[(left - grange['start']) / resolution,
                      (right - grange['start']) / resolution] = value
                array[(right - grange['start']) / resolution,
                      (left - grange['start']) / resolution] = value

    # make regional pixelmap
    regional_pixelmap = [{'name' : '%s_BIN_%03d' %
                                   (region_name,
                                    (i - grange['start']) / resolution),
                          'chrom': grange['chrom'],
                          'start': i,
                          'end'  : i + resolution}
                         for i in range(grange['start'],
                                        grange['end'],
                                        resolution)]

    return array, regional_pixelmap
