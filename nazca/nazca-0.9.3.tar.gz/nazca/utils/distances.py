# -*- coding:utf-8 -*-
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

import difflib
from functools import partial
from math import cos, sqrt, pi  # Needed for geographical distance

from six.moves import xrange

try:
    from dateutil import parser as dateparser
    DATEUTIL_ENABLED = True
except ImportError:
    DATEUTIL_ENABLED = False
from scipy import matrix, empty

from nazca.utils.normalize import tokenize


###############################################################################
# UTILITY FUNCTIONS ###########################################################
###############################################################################
def cdist(distance_callback, refset, targetset, matrix_normalized=False,
          ref_indexes=None, target_indexes=None):
    """ Compute the metric matrix, given two datasets and a metric

    Parameters
    ----------
    refset: a dataset (list of records)

    targetset: a dataset (list of records)

    Returns
    -------

    A distance matrix, of shape (len(refset), len(targetset))
    with the distance of each element in it.
    """
    ref_indexes = ref_indexes or xrange(len(refset))
    target_indexes = target_indexes or xrange(len(targetset))
    distmatrix = empty(
        (len(ref_indexes),
         len(target_indexes)),
        dtype='float32')
    for i, iref in enumerate(ref_indexes):
        for j, jref in enumerate(target_indexes):
            d = 1
            if refset[iref] and targetset[jref]:
                d = distance_callback(refset[iref], targetset[jref])
                if matrix_normalized:
                    d = 1 - (1.0 / (1.0 + d))
            distmatrix[i, j] = d
    return distmatrix


def _handlespaces(stra, strb, distance, tokenizer=None, **kwargs):
    """ Compute the matrix of distances between all tokens of stra and strb
        (with function ``distance``). Extra args are given to the distance
        function

        The distance returned is defined as the max of the min of each rows of
        each distance matrix, see the example above :

                 |  Victor |  Hugo                  Victor | Jean | Hugo
         Victor  |     0   |    5           Victor |  0    |  6   |  5
          Jean   |     6   |    4           Hugo   |  5    |  4   |  0
          Hugo   |     5   |    0

                 --> 4                                --> 0

        Return 4
    """

    if ' ' not in stra:
        stra += ' '
    if ' ' not in strb:
        strb += ' '

    toka = tokenize(stra, tokenizer)
    tokb = tokenize(strb, tokenizer)
    # If not same number of tokens, complete the smallest list with empty
    # strings
    if len(toka) != len(tokb):
        mint = toka if len(toka) < len(tokb) else tokb
        maxt = toka if len(toka) > len(tokb) else tokb
        mint.extend(['' for i in range(len(maxt) - len(mint))])

    listmatrix = []
    for i in xrange(len(toka)):
        listmatrix.append([distance(toka[i], tokb[j], **kwargs)
                           for j in xrange(len(tokb))])
    m = matrix(listmatrix)
    minlist = [m[i, :].min() for i in xrange(m.shape[0])]
    minlist.extend([m[:, i].min() for i in xrange(m.shape[1])])
    return max(minlist)


###############################################################################
# NUMERICAL DISTANCES #########################################################
###############################################################################
def euclidean(a, b):
    """ Simple euclidian distance
    """
    try:
        return abs(a - b)
    except TypeError:
        # a and b may be strings
        return abs(float(a) - float(b))


###############################################################################
# STRING DISTANCES ############################################################
###############################################################################
def exact_match(a, b):
    """ The simplest distance, defined as 0 if both values are equal, 1 elsewise.
    """
    return 0 if a == b else 1


def levenshtein(stra, strb, tokenizer=None):
    """ Compute the Levenshtein distance between stra and strb.

    The Levenshtein distance is defined as the minimal cost to transform stra
    into strb, where 3 operators are allowed :
        - Replace one character of stra into a character of strb
        - Add one character of strb into stra
        - Remove one character of strb

        If spaces are found in stra or strb, this method returns
            _handlespaces(stra, strb, levenshtein)
    """
    if ' ' in stra or ' ' in strb:
        return _handlespaces(stra, strb, levenshtein, tokenizer)

    lenb = len(strb)
    onerowago = None
    thisrow = list(range(1, lenb + 1)) + [0]
    for x in xrange(len(stra)):
        onerowago, thisrow = thisrow, [0] * lenb + [x + 1]
        for y in xrange(lenb):
            delcost = onerowago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = onerowago[y - 1] + (stra[x] != strb[y])
            thisrow[y] = min(delcost, addcost, subcost)
    return thisrow[lenb - 1]


def soundexcode(word, language='french'):
    """ Return the Soundex code of the word ``word``
        For more information about soundex code see wiki_

        ``language`` can be 'french' or 'english'

        .:: wiki_ : https://en.wikipedia.org/wiki/Soundex

        If spaces are found in stra or strb, this method returns
            _handlespaces(stra, strb), soundex, language=language)
    """

    vowels = 'AEHIOUWY'
    if language.lower() == 'french':
        consonnantscode = {'B': '1', 'P': '1',
                           'C': '2', 'K': '2', 'Q': '2',
                           'D': '3', 'T': '3',
                           'L': '4',
                           'M': '5', 'N': '5',
                           'R': '6',
                           'G': '7', 'J': '7',
                           'X': '8', 'Z': '8', 'S': '8',
                           'F': '9', 'V': '9'
                           }
    elif language.lower() == 'english':
        consonnantscode = {'B': '1', 'F': '1', 'P': '1', 'V': '1',
                           'C': '2', 'G': '2', 'J': '2', 'K': '2',
                           'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
                           'D': '3', 'T': '3',
                           'L': '4',
                           'M': '5', 'N': '5',
                           'R': '6'
                           }
    else:
        raise NotImplementedError('Soundex code is not supported (yet ?) for'
                                  'this language (%s). '
                                  'Supported languages are french and english' % language)
    word = word.strip().upper()
    code = word[0]
    # After this ``for`` code is
    # the first letter of ``word`` followed by all the consonnants of word,
    # where from consecutive consonnants, only the first is kept,
    # and from two identical consonnants separated by a W or a H, only the first
    # is kept too.
    for i in xrange(1, len(word)):
        if word[i] in vowels:
            continue
        if word[i - 1] not in vowels and \
           consonnantscode[word[i]] == consonnantscode.get(code[-1], ''):
            continue
        if i + 2 < len(word) and word[i + 1] in 'WH' and \
           consonnantscode[word[i]] == consonnantscode.get(word[i + 2], ''):
            continue
        code += word[i]
        if len(code) > 4:
            break

    # Replace according to the codes
    code = code[0] + ''.join([consonnantscode[c] for c in code[1:]])
    # First four letters, completed by zeros
    return code[:4] + '0' * (4 - len(code))


def soundex(stra, strb, language='french', tokenizer=None):
    """ Return the 1/0 distance between the soundex code of stra and strb.
        0 means they have the same code, 1 they don't
    """
    if ' ' in stra or ' ' in strb:
        return _handlespaces(stra, strb, soundex,
                             tokenizer=tokenizer, language=language)
    return 0 if (soundexcode(stra, language) ==
                 soundexcode(strb, language)) else 1


def jaccard(stra, strb, tokenizer=None):
    """ Return the jaccard distance between stra and strb, condering the tokens
        set of stra and strb. If no tokenizer is given, it use if
        alignement.normalize.tokenize's default one.

        J(A, B) = (A \cap B)/(A \cup B)
        d(A, B) = 1 - J(A, B)
    """
    seta = set(tokenize(stra, tokenizer))
    setb = set(tokenize(strb, tokenizer))
    return generic_jaccard(seta, setb)


def generic_jaccard(seta, setb):
    """ Return the jaccard distance between two sets A and B.

        J(A, B) = (A \cap B)/(A \cup B)
        d(A, B) = 1 - J(A, B)

        special case: if A and B are emtpy, return 1.
    """
    try:
        return 1.0 - 1.0 * len(seta.intersection(setb)) / len(seta.union(setb))
    except ZeroDivisionError:
        return 1.0



def difflib_match(stra, strb):
    """ Approximate matching.
    Extract of SequenceMatched documentation
    '[...] The basic algorithm predates, and is a little fancier than, an algorithm
    published in the late 1980's by Ratcliff and Obershelp under the
    hyperbolic name "gestalt pattern matching"[...]'

    A value smaller than 0.4 means that sequences are close matches (we take
    1 - difflib.SequenceMatched)
    """
    return 1.0 - difflib.SequenceMatcher(None, stra, strb).ratio()


###############################################################################
# TEMPORAL DISTANCES ##########################################################
###############################################################################
if DATEUTIL_ENABLED:
    class FrenchParserInfo(dateparser.parserinfo):
        """ Inherit of the dateutil.parser.parserinfo and translate the english
            dependant variables into french.
        """

        HMS = [(u'h', u'heure', u'heures'),
               (u'm', u'minute', u'minutes'),
               (u's', u'seconde', u'seconde'), ]
        JUMP = [u' ', u'.', u',', u';', u'-', u'/', u"'",
                u'a', u'le', u'et', u'er']
        MONTHS = [(u'Jan', u'Janvier'), (u'Fev', u'Fevrier'),
                  (u'Mar', u'Mars'), (u'Avr', u'Avril'), (u'Mai', u'Mai'),
                  (u'Jun', u'Juin'), (u'Jui', u'Juillet'),
                  (u'Aou', u'Aout'), (u'Sep', u'Septembre'),
                  (u'Oct', u'Octobre'), (u'Nov', u'Novembre'),
                  (u'Dec', u'Decembre')]
        PERTAIN = [u'de']
        WEEKDAYS = [(u'Lun', u'Lundi'),
                    (u'Mar', u'Mardi'),
                    (u'Mer', u'Mercredi'),
                    (u'Jeu', u'Jeudi'),
                    (u'Ven', u'Vendredi'),
                    (u'Sam', u'Samedi'),
                    (u'Dim', u'Dimanche')]

    def temporal(stra, strb, granularity=u'days', parserinfo=FrenchParserInfo,
                 dayfirst=True, yearfirst=False):
        """ Return the distance between two strings (read as dates).

            ``granularity`` can be either ``days`` or ``months`` or ``years``
            (be careful to the plural form !)
            ``language`` can be either french or english

            ``dayfirst`` and ``yearfirst`` are used in case of ambiguity, for
            instance 09/09/09, by default it assumes it's day/month/year

            Neither stra nor strb can have accent. Clean it before.
        """

        datea = dateparser.parse(stra, parserinfo=parserinfo(dayfirst,
                                                             yearfirst), fuzzy=True)
        dateb = dateparser.parse(strb, parserinfo=parserinfo(dayfirst,
                                                             yearfirst), fuzzy=True)
        diff = datea - dateb
        if granularity.lower() == 'years':
            return abs(diff.days / 365.25)
        if granularity.lower() == 'months':
            return abs(diff.days / 30.5)
        return abs(diff.days)


###############################################################################
# GEOGRAPHICAL DISTANCES ######################################################
###############################################################################
def geographical(pointa, pointb, in_radians=False, planet_radius=6371009,
                 units='m'):
    """ Return the geographical distance between two points.

        Both points must be tuples (latitude, longitude)

        - in_radians is True, if latitude and longitude are in radians, false
          otherwise
        - planetRadius is the planet's radius in meters. By default, it's the
          Earth'one.

        - `units` can be 'm' (meters) or 'km' (kilometers)
    """
    if units not in ('m', 'km'):
        raise ValueError("unsupported units, should be in m or km")
    pointa = (float(pointa[0]), float(pointa[1]))
    pointb = (float(pointb[0]), float(pointb[1]))

    difflat = pointa[0] - pointb[0]
    difflong = pointa[1] - pointb[1]
    meanlat = (pointa[0] + pointb[0]) / 2.0

    if not in_radians:
        difflat *= pi / 180.0
        difflong *= pi / 180.0
        meanlat *= pi / 180.0

    coef = 1. if units == 'm' else 0.001
    return coef * planet_radius * \
        sqrt(difflat**2 + (cos(meanlat) * difflong)**2)


###############################################################################
# BASE PROCESSING ########################################################
###############################################################################
class BaseProcessing(object):
    """ A processing object used to provide an abstraction over the different
    distance functions, and help building Nazca process. """

    def __init__(self, ref_attr_index=None, target_attr_index=None,
                 distance_callback=euclidean, weight=1, matrix_normalized=False):
        """ Initiate the BaseProcessing

        Parameters
        ----------

        ref_attr_index: index of the attribute of interest in a record
                        for the reference dataset
                        (i.e. attribute to be used for key computation)

        target_attr_index: index of the attribute of interest in a record
                           for the target dataset
                           (i.e. attribute to be used for key computation)

        distance_callback: distance callback. Default is euclidean distance.

        weight: weight of the processing in a global distance matrix

        matrix_normalized: Boolean. If matrix_normalized is True,
                           the distance between two points is changed to
                           a value between 0 (equal) and 1 (totaly different).
                           To avoid useless computation and scale
                           problems the following “normalization” is done:
                                d = 1 - 1/(1 + d(x, y))

        """
        self.ref_attr_index = ref_attr_index
        self.target_attr_index = target_attr_index
        self.distance_callback = distance_callback
        self.weight = weight
        self.matrix_normalized = matrix_normalized

    def build_record(self, record, index):
        """ Allow to have ref_attr_index and target_attr_index to be couple
        of index for (latitude, longitude) """
        if isinstance(index, tuple) and len(index) == 2:
            return (record[index[0]], record[index[1]])
        else:
            return (record[index] if index is not None else record)

    def distance(self, reference_record, target_record):
        """ Compute the distance between two records

        Parameters
        ----------
        reference_record: a record (tuple/list of values) of the reference dataset.

        target_record: a record (tuple/list of values) of the target dataset.

        """
        return self.distance_callback(self.build_record(reference_record, self.ref_attr_index),
                                      self.build_record(target_record, self.target_attr_index))

    def cdist(self, refset, targetset, ref_indexes=None, target_indexes=None):
        """ Compute the metric matrix, given two datasets and a metric

        Parameters
        ----------
        refset: a dataset (list of records)

        targetset: a dataset (list of records)

        Returns
        -------

        A distance matrix, of shape (len(refset), len(targetset))
        with the distance of each element in it.
        """
        return cdist(self.distance, refset, targetset,
                     matrix_normalized=self.matrix_normalized,
                     ref_indexes=ref_indexes, target_indexes=target_indexes)

    def pdist(self, dataset):
        """ Compute the upper triangular matrix in a way similar
        to scipy.spatial.metric

        Parameters
        ----------
        dataset: a dataset (list of records)

        Returns
        -------

        The values of the upper triangular distance matrix
        (of shape (len(dataset), len(dataset)) with the distance of each element in it.
        The values are sorted as row 1, row2, ...
        """
        values = []
        for i in xrange(len(dataset)):
            for j in xrange(i + 1, len(dataset)):
                d = 1
                if dataset[i] and dataset[j]:
                    d = self.distance(dataset[i], dataset[j])
                    if self.matrix_normalized:
                        d = 1 - (1.0 / (1.0 + d))
                values.append(d)
        return values


###############################################################################
# CONCRETE PROCESSINGS ###################################################
###############################################################################
class ExactMatchProcessing(BaseProcessing):
    """ A processing based on the exact match (1 if a==b, 0 elsewise)
    """

    def __init__(self, ref_attr_index=None, target_attr_index=None,
                 tokenizer=None, weight=1, matrix_normalized=False):
        super(ExactMatchProcessing, self).__init__(ref_attr_index,
                                                   target_attr_index,
                                                   exact_match,
                                                   weight, matrix_normalized)


class LevenshteinProcessing(BaseProcessing):
    """ A processing based on the levenshtein distance.
    """

    def __init__(self, ref_attr_index=None, target_attr_index=None,
                 tokenizer=None, weight=1, matrix_normalized=False):
        distance_callback = partial(levenshtein,
                                    tokenizer=tokenizer)
        super(LevenshteinProcessing, self).__init__(ref_attr_index,
                                                    target_attr_index,
                                                    distance_callback,
                                                    weight, matrix_normalized)


class GeographicalProcessing(BaseProcessing):
    """ A processing based on the geographical distance.
    """

    def __init__(self, ref_attr_index=None, target_attr_index=None,
                 in_radians=False, planet_radius=6371009, units='m', weight=1,
                 matrix_normalized=False):
        distance_callback = partial(geographical, in_radians=in_radians,
                                    planet_radius=planet_radius, units=units)
        super(GeographicalProcessing, self).__init__(ref_attr_index,
                                                     target_attr_index,
                                                     distance_callback,
                                                     weight, matrix_normalized)


class SoundexProcessing(BaseProcessing):
    """ A processing based on the soundex distance.
    """

    def __init__(self, ref_attr_index=None, target_attr_index=None,
                 tokenizer=None, weight=1, language='french', matrix_normalized=False):
        distance_callback = partial(
            soundex, language=language, tokenizer=tokenizer)
        super(SoundexProcessing, self).__init__(ref_attr_index,
                                                target_attr_index,
                                                distance_callback,
                                                weight, matrix_normalized)


class JaccardProcessing(BaseProcessing):
    """ A processing based on the jaccard distance.
    """

    def __init__(self, ref_attr_index=None, target_attr_index=None,
                 tokenizer=None, weight=1, matrix_normalized=False):
        distance_callback = partial(jaccard, tokenizer=tokenizer)
        super(JaccardProcessing, self).__init__(ref_attr_index,
                                                target_attr_index,
                                                distance_callback,
                                                weight, matrix_normalized)


class DifflibProcessing(BaseProcessing):
    """ A processing based on the difflib distance.
    """

    def __init__(self, ref_attr_index=None, target_attr_index=None,
                 weight=1, matrix_normalized=False):
        super(DifflibProcessing, self).__init__(ref_attr_index,
                                                target_attr_index,
                                                difflib_match,
                                                weight, matrix_normalized)


if DATEUTIL_ENABLED:
    class TemporalProcessing(BaseProcessing):
        """ A processing based on the temporal distance.
        """

        def __init__(self, ref_attr_index=None, target_attr_index=None,
                     granularity=u'days', parserinfo=FrenchParserInfo,
                     dayfirst=True, yearfirst=False,
                     weight=1, matrix_normalized=False):
            distance_callback = partial(temporal, granularity=granularity,
                                        parserinfo=parserinfo,
                                        dayfirst=dayfirst, yearfirst=yearfirst)
            super(TemporalProcessing, self).__init__(ref_attr_index,
                                                     target_attr_index,
                                                     distance_callback,
                                                     weight, matrix_normalized)
