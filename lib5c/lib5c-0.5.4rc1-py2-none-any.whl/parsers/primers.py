"""
Module for parsing .bed files containing 5C primer and bin information.
"""

from lib5c.parsers.util import parse_field
from lib5c.parsers.primer_names import default_bin_parser, \
    guess_primer_name_parser


def load_primermap(bedfile, name_parser=None, strand_index=5,
                   region_index=None, column_names=None):
    """
    Parameters
    ----------
    bedfile : str
        String reference to a primer bedfile to use to generate the primermap.
    name_parser : Optional[Callable[[str], Dict[str, Any]]]
        Function that takes in the primer name column of the bedfile (the fourth
        column) and returns a dict containing key-value pairs to be added to the
        dict that represents that primer. At a minimum, this dict must have the
        following structure::

            {
                'region': string
            }

        If the dict includes any keys that are already typically included in the
        primer dict, the values returned by this function will overwrite the
        usual values. If None is passed, an appropriate name parser will be
        guessed based on the primer/bin names.
    strand_index : Optional[int]
        If an int is passed, the column with that index will be used to
        determine strand information for the primer. If ``None`` is passed, the
        algorithm will try to guess which column contains this information. If
        this fails, strand information will not be included in the primer dict.
        Acceptable strings to indicate primer strand are 'F'/'R', 'FOR'/'REV',
        and '+'/'-'. Primers on the + strand will be assumed to be oriented in
        the 3' direction, and primers on the - strand will be assumed to be
        oriented in the 5' direction, unless an 'orientation' key is provided in
        the dict returned by ``name_parser``.
    region_index : Optional[int]
        If an int is passed, the column with that index will be used to
        determine the region the primer is in. This makes specifying
        ``region_parser`` optional and overrides the region it returns.
    column_names : Optional[List[str]]
        Pass a list of strings equal to the number of columns in the bedfile,
        describing the columns. The first four elements will be ignored. Special
        values include 'strand', which will set ``strand_index``, and 'region',
        which will override ``region_index``. All other values will end up as
        keys in the primer dicts. If this is not passed, this function will look
        for a header line in the primerfile, and if one is not found, a default
        header will be assumed.

    Returns
    -------
    Dict[str, List[Dict[str, Any]]]
        The keys of the outer dict are region names. The values are lists, where
        the :math:`i` th entry represents the :math:`i` th primer in that
        region. Primers are represented as dicts with the following structure::

            {
                'region'     : str
                'chrom'      : str,
                'start'      : int,
                'end'        : int,
                'name'       : str,
                'strand'     : '+' or '-',
                'orientation': "3'" or "5'"
            }

        though strand and orientation may not be present, and additional keys
        may be present if returned by ``name_parser``, passed in
        ``column_names``, or if a header line is present.

    Notes
    -----
    A primermap is a mapping from primers (specified by a region name and primer
    index) to the genomic range covered by those primers.
    """
    # acceptable strand identifiers
    plus_strand_identifiers = ['F', 'FOR', '+']
    minus_strand_identifiers = ['R', 'REV', '-']

    # dict to store the primermap
    primermap = {}

    # parse column_names
    if column_names is not None:
        try:
            strand_index = column_names.index('strand')
        except ValueError:
            pass
        try:
            region_index = column_names.index('region')
        except ValueError:
            pass

    # parse bedfile
    with open(bedfile, 'r') as handle:
        # parse the bedfile
        for line in handle:
            # skip comments, unless they contain bedtools nuc information
            if line.startswith('#') or line.startswith('track'):
                if column_names is None and not line.startswith('#track'):
                    pieces = line.strip().strip('#').split('\t')
                    if len(pieces) > 4:
                        column_names = pieces
                        try:
                            strand_index = column_names.index('strand')
                        except ValueError:
                            pass
                        try:
                            region_index = column_names.index('region')
                        except ValueError:
                            pass
                continue

            # split bedfile line
            feature_columns = line.strip().split('\t')

            # parse bed feature information
            chrom = feature_columns[0]
            start = int(feature_columns[1])
            end = int(feature_columns[2])
            name = feature_columns[3]

            # guess name_parser if not passed
            if name_parser is None:
                name_parser = guess_primer_name_parser(name)

            # if we failed to guess the name_parser, fall back to chromosomes
            if name_parser is None and region_index is None:
                region_index = 0

            # try parsing region using region_index
            region = None
            if region_index is not None and region_index < len(feature_columns):
                region = feature_columns[region_index]

            # try parsing strand using strand_index
            # or looping through all columns as a fallback
            strand = None
            if strand_index is not None and strand_index < len(feature_columns):
                strand_string = feature_columns[strand_index]
                if strand_string in plus_strand_identifiers:
                    strand = '+'
                elif strand_string in minus_strand_identifiers:
                    strand = '-'
            else:
                for feature_column in feature_columns:
                    if feature_column in plus_strand_identifiers:
                        strand = '+'
                    elif feature_column in minus_strand_identifiers:
                        strand = '-'

            # assemble the dict describing this primer
            # always-present, required fields
            primer_dict = {'chrom': chrom,
                           'start': start,
                           'end'  : end,
                           'name' : name}

            # if region_index or strand_index already succeeded, add them now
            if region is not None:
                primer_dict['region'] = region
            if strand is not None:
                primer_dict['strand'] = strand

            # add additional fields from name_parser to primer_dict
            if name_parser is not None:
                name_fields = name_parser(name)
                primer_dict.update(name_fields)

            # add arbitrary fields from column_names or parsed from header
            if column_names is not None and len(column_names) > 4:
                for i in range(4, len(column_names)):
                    primer_dict[column_names[i]] = parse_field(
                        feature_columns[i])

            # if 'strand' exists but 'orientation' doesn't, fill it in
            if 'strand' in primer_dict and 'orientation' not in primer_dict:
                primer_dict['orientation'] = "3'"\
                    if primer_dict['strand'] == '+' else "5'"

            # if we haven't figured out the region by now raise an error
            if 'region' not in primer_dict:
                raise ValueError(
                    'region could not be identfied (must pass one of '
                    'name_parser, region_index, or column_names with "region" '
                    'column)')

            # if this is a new region, make a new list for it
            if primer_dict['region'] not in primermap:
                primermap[primer_dict['region']] = []

            # add this primer to the primermap
            primermap[primer_dict['region']].append(primer_dict)

    for region in primermap.keys():
        # sort primers within each region
        primermap[region].sort(key=lambda x: x['start'])

        # post-check: if the primermap has 1bp gaps, we assume that the bedfile
        # is formatted incorrectly and that we should extend the end coordinate
        # by 1
        has_gaps = False
        for i in range(len(primermap[region])):
            if i == len(primermap[region]) - 1:
                break
            gap = primermap[region][i+1]['start'] - primermap[region][i]['end']
            if gap == 0:
                break
            if gap == 1:
                has_gaps = True
                break
        if has_gaps:
            for primer in primermap[region]:
                primer['end'] += 1

    return primermap


def get_pixelmap_legacy(bedfile, name_parser=default_bin_parser):
    """
    Parameters
    ----------
    bedfile : str
        String reference to a binned primer bedfile to use to generate the
        pixelmap.
    name_parser : Optional[Callable[[str], Dict[str, Any]]]
        Function that takes in the bin name column of the bedfile (the fourth
        column) and returns a dict containing key-value pairs to be added to the
        dict that represents that bin. At a minimum, this dict must have the
        following structure::

            {
                'region': str
            }

        If the dict includes any keys that are already typically included in the
        bin dict, the values returned by this function will overwrite the usual
        values.

    Returns
    -------
    Dict[str, List[Dict[str, Any]]]
        The keys of the outer dict are region names. The values are lists, where
        the :math:`i` th entry represents the :math:`i` th bin in that region.
        Bins are represented as dicts with the following structure::

            {
                'chrom': str,
                'start': int,
                'end'  : int,
                'name' : str
            }

        Additional keys may be present if returned by ``name_parser``.

    Notes
    -----
    A pixelmap is a mapping from bins (specified by a region name and bin or
    primer index) to the genomic range covered by those bins.
    """

    # dict to store the pixelmap
    pixelmap = {}

    # parse bedfile
    with open(bedfile, 'r') as handle:
        # parse the bedfile
        for line in handle:
            # skip comments
            if line.startswith('#'):
                continue

            # split line on tab
            pieces = line.strip().split('\t')

            # parse genomic coordinate information
            chrom = pieces[0]
            start = int(pieces[1])
            end = int(pieces[2])

            # parse bin name
            name_fields = name_parser(pieces[3])
            region = name_fields['region']

            # if this is a new region, make a new list for it
            if region not in pixelmap:
                pixelmap[region] = []

            # assemble the dict describing this primer
            # always-present fields
            bin_dict = {'chrom': chrom,
                        'start': start,
                        'end'  : end,
                        'name' : pieces[3]}

            # add additional fields from parse_name
            bin_dict.update(name_fields)

            # add this region to the map
            pixelmap[region].append(bin_dict)

    # sort bins within each region
    for region in pixelmap.keys():
        pixelmap[region].sort(key=lambda x: x['start'])

    return pixelmap


# test client
def main():
    print(load_primermap('test/bins.bed')['Nestin'][0])
    print(load_primermap('test/primers.bed')['Nestin'][0])
    print(load_primermap('test/primers_nuc.bed')['Nestin'][0])


if __name__ == "__main__":
    main()
