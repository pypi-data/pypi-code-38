"""
Module providing helper functions for working with primer naming conventions,
necessary for parsing certain primerfiles.
"""


def guess_primer_name_parser(name):
    """
    Guesses the appropriate primer or bin name parser to use by looping through
    a list of possible parsers and testing if they work on a given primer name.

    Parameters
    ----------
    name : str
        The name of a primer to use for testing.

    Returns
    -------
    function
        The parser thought to be appropriate for this kind of primer name.
    """
    parsers = [dblalt_primer_parser, default_primer_parser, default_bin_parser]
    for parser in parsers:
        try:
            parser(name)
            return parser
        except (ValueError, IndexError):
            pass


def default_primer_parser(name):
    """
    The default primer name parser.

    Parameters
    ---------
    name : str
        The name of the primer found in the appropriate column of the primer
        bedfile.

    Returns
    -------
    dict
        This dict has the following structure::

            {
                'region': str,
                'number': int,
                'name': str
            }

        These fields are parsed from the primer name.

    Notes
    -----
    You can write other name parsers to accommodate different primer naming
    conventions.
    """
    pieces = name.split('_')
    region = pieces[2]
    number = int(pieces[4].split(':')[0])
    if pieces[3] == 'FOR':
        orientation = "3'"
        strand = '+'
    elif pieces[3] == 'REV':
        orientation = "5'"
        strand = '-'
    else:
        raise ValueError('default primer name scheme violation')
    corrected_name = name.split(':')[0]
    return {'region'     : region,
            'number'     : number,
            'orientation': orientation,
            'strand'     : strand,
            'name'       : corrected_name}


def dblalt_primer_parser(name):
    """
    The double alternating primer name parser.

    Parameters
    ---------
    name : str
        The name of the primer found in the appropriate column of the primer
        bedfile.

    Returns
    -------
    dict
        This dict has the following structure::

            {
                'region': str,
                'number': int,
                'orientation': "3'" or "5'",
                'name': str
            }

        These fields are parsed from the primer name.

    Notes
    -----
    You can write other name parsers to accommodate different primer naming
    conventions.
    """
    pieces = name.split('_')
    region = pieces[2].split('-')[0]
    if len(pieces[4].split(':')[0].split('|')) == 1:
        raise ValueError('dblalt primer name scheme violation')
    number = int(pieces[4].split(':')[0].split('|')[0])
    if pieces[3].split('-')[0] in ['FOR', 'LFOR']:
        orientation = "3'"
        strand = '+'
    elif pieces[3].split('-')[0] in ['REV', 'LREV']:
        orientation = "5'"
        strand = '-'
    else:
        raise ValueError('dblalt primer name scheme violation')
    corrected_name = name.split(':')[0]+':'+name.split(':')[1]

    return {'region'     : region,
            'number'     : number,
            'orientation': orientation,
            'strand'     : strand,
            'name'       : corrected_name}


def default_bin_parser(name):
    """
    The default bin name parser.

    Parameters
    ---------
    name : str
        The name of the bin found in the appropriate column of the bin bedfile.

    Returns
    -------
    dict
        This dict has the following structure::

            {
                'region': str,
                'index': int
            }

        These fields are parsed from the bin name.

    Notes
    -----
    You can write other name parsers to accommodate different bin naming
    conventions.
    """
    pieces = name.split('_')
    region = pieces[0]
    if pieces[1] != 'BIN':
        raise ValueError('default bin name scheme violation')
    index = int(pieces[2])
    return {'region': region,
            'index': index}
