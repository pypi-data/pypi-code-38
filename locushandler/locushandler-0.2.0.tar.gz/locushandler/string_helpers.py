"""Helper methods for string_parser"""

import re
from locushandler.params import DIVS

# \( and \) are the literal opening & closing parentheses
# period . matches with any non-newline characters
# *? is a quantifier, meaning the match will happen between 0 & infinity times
# but as few times as possible, so "(DR) verb noun (IO)" will have 2 matches "(DR)" and "(IO)"
# without the ?, the greedy match would return 1 match: "(DR) verb noun (IO)" because that whole
# string is between 2 parentheses
DR_IO_PATTERN = (r"\(.*?\)")


def work_or_resource(locus_field):
    '''
    Return 'work' or 'resource' based on
    pattern of locus_field
    :param locus_field: (string)
    :return: (string) 'resource' or 'work'
    '''
    # remove terms in parentheses, if any
    locus_field = remove_dr_io(locus_field)

    # split on space
    splitted = locus_field.split()

    # After dr & io removed, work loci has
    # even number of terms, and resource loci
    # has odd number of terms
    if len(splitted) == 3:
        # %2 == 1 so odd
        return 'resource'
    elif len(splitted) == 2:
        return 'work'
    else:
        raise KeyError


def dediv_noun(locus_noun):
    '''
    Parse nouns containing Div
    Div --> (V,V,V)
    CDiv --> (C,V,V)
    C2Div --> (C,2,V)
    :param locus_noun: (string)
    :return: locus_noun with Divs removed (tuple)
    '''
    assert isinstance(locus_noun,
                      str), f'Expect locus_noun: {locus_noun} to be a string'

    if locus_noun.lower() in DIVS:
        return ('V', 'V', 'V')
    elif locus_noun[1:].lower() in DIVS:
        return (locus_noun[0], 'V', 'V')
    elif locus_noun[2:].lower() in DIVS:
        return (locus_noun[0], locus_noun[1], 'V')
    else:
        return (locus_noun[0], locus_noun[1], locus_noun[2:])


def remove_dr_io(work_locus):
    '''
    Given string of work locus,
    remove everything between parentheses
    strip leading & trailing spaces
    :param work_locus: (string)
    :return: work_locus with dr & io removed (string)
    '''
    assert isinstance(
        work_locus, str), f'Expect work_locus: {work_locus} to be a string'

    # replace all regex matches with empty string
    work_locus = re.sub(DR_IO_PATTERN, '', work_locus)

    return work_locus.strip()


def extract_dr_io(work_locus):
    '''
    Given string of Locus field, find all pairs of
    leading (DR) and ending (IO) parentheses
    and extract content between each pair.

    return tuple (DR, IO), tuple element = '' empty string
    if not found.
    :param work_locus: (string)
    :return: parsed tuple of (DR, IO) (tuple of strings)
    '''
    assert isinstance(
        work_locus, str), f'Expect work_locus: {work_locus} to be a string'

    matches_found = re.findall(DR_IO_PATTERN, work_locus)
    if len(matches_found) == 1:
        match = matches_found[0]
        if work_locus.find(match) == 0:
            # if pattern is matched at the beginning of work locus
            # then the match is a DR

            # remember to strip leading & trailing parentheses!
            return (match.strip('()'), '')
        else:
            return ('', match.strip('()'))
    elif len(matches_found) == 2:
        return (matches_found[0].strip('()'), matches_found[1].strip('()'))
    else:
        return ('', '')


def parse_granularity(granularity):
    '''
    Parsing compound granularity into
    verb & noun granularity
    :param granularity: from GRANULARITY
    :return: granularity parsed into verb & noun granularity
    (tuple of strings)
    '''
    try:
        if granularity == 'full':
            return ('36', '6x4x3')
        else:
            # the verb part always comes before the first x
            # specify maxsplit = 1 to split only on 1st occurrence of x
            verb_granularity, noun_granularity = granularity.split('x', 1)

            return (verb_granularity, noun_granularity)
    except ValueError:
        print('Make sure the granularity input has the format \'<act>x<obj>\'')
        raise
