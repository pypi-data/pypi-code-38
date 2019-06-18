#!/usr/bin/env python


# Standard imports

import copy
import os
from math import log2
import pandas as pd
import re


def make_globals(_storage_path='ISCN_storage.h5'):
    """Makes the two global variables _cyto_bands and _template.

    These global variables are tables used to align band locations written in
    standard band nomenclature such as 1p11 or 6q21 to their respective
    chromosomal locations (in basepairs). These variables are constant and
    never modified over the course of any function of this program.

    _cyto_bands is the DataFrame titled ' cytoband_locations' in storage file
    and consists of all standard bands as well as a few special cases that
    appear in some databases such as 'qter/pter' and p10/q10 which represent
    the terminal ends of chromosomes and the centromeres respectively.

    _template is the DataFrame titled 'cytogenic_template' in storage file and
    consists of only standard cytogenic band locations.

    Keyword Args:

        _storage_path (string): default: 'ISCN_storage.h5'.

            The path to the storage file containing two DataFrames labelled
            as described above.

            One reason you might change this is if you want to only analyze
            certain locations (say everything but the Y chromosome) you could
            createa new storage with the cytoband_locations and
            cytogenic_template containing only the chromosomes you want to
            analyze so that aberrations on the removed locations won't be
            included in the final output.

    Returns:
        None
    """
    original_path = os.getcwd()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    global _cyto_bands
    _cyto_bands = pd.read_hdf(_storage_path, 'cytoband_locations')
    global _template
    _template = pd.read_hdf(_storage_path, 'cytogenic_template')
    os.chdir(original_path)


make_globals()


def swap_bands(dname):
    """ Swaps bands so the start band always comes before the end band.

    If the end is larger than the start, swap them. Otherwise just return
    the parameter dname as inputted.

    Args:
        dname (pandas.Series): A pandas.Series or 1 row pandas.DataFrame
        object containing the cytogenic band locations labeled as 'Start' and
        'End' (Case sensitive).

    Returns:
        dname with the bands swapped if 'Start' is greater than 'End' else
        returns dname.
    """
    if dname['Start'] > dname['End']:
        dname['Start'], dname['End'] = dname['End'], dname['Start']
    return dname


def find_start(band, chromosome):
    """Returns the loci of the beginning of a band on a chromosome
    
    Cytogenic bands have two locations, a start and an end. This function
    finds the start location by comparing to the _cyto_bands DataFrame.
    
    Args:
        band (string): A two digit chromosomal band such as q11.
        chromosome (string): The chromosome that the band is on.

    Returns:
        int: The basepair location of the specified band start. -1 if no match
        is found. At the end of each patient analyzed all the negative
        band locations are removed.
    """
    base = _cyto_bands.loc[(_cyto_bands['Chromosome'] == chromosome) & (
                           _cyto_bands['band'] == band)].Start.values
    if base.size > 0:
        return int(base)
    else:
        # Later all the negative values get culled
        return -1 


def find_end(band, chromosome):
    """Returns the loci of the beginning of a band on a chromosome
    
    Cytogenic bands have two locations, a start and an end. This function
    finds the end location by comparing to the _cyto_bands DataFrame.

    Args:
        band (string): A two digit chromosomal band such as q11
        chromosome (string): the chromosome that the band is on.

    Returns:
        int: The basepair location of the specified band end. -1 if no match
        is found. At the end of each patient analyzed all the negative
        band locations are removed.
    """
    base = _cyto_bands.loc[(_cyto_bands['Chromosome'] == chromosome) & (
                           _cyto_bands['band'] == band)].End.values
    if base.size > 0:
        return int(base)
    else:
        return -1


def find_span(band, chromosome, includes_centromere=False, endBand='ter'):
    """Finds the span between two cytoband locations.
    By default, this function will find the span between a given cytogenic
    band and the terminal point of the arm its on (inclusive). Some aberrations,
    specifically isochromosomes contain additions or losses of spans across
    the centromere. In these cases the span is found between a band location
    and the end of the opposite terminal. Locations are found using find_start
    and find_end
    Parameters:
        band (string): A two digit chromosomal band such as p21
        chromosome (string): The chromosome that the band is on.
    Keyword Argumentss:
        includes_centromere (bool): default: False. True if finding span
            across a centromere. False if finding span from a location to
            its terminal end.
        endBand (string): default: 'ter'. The location of the band to find
            the span to from band
    Returns:
        two values, one for the start band and one for the ending band
    """
    if endBand == 'ter' and '10' in band:
        includes_centromere = True
    if includes_centromere:
        if len(band) == 0:
            return -1, -1
        elif band[0] == 'q':
            # start is always 0
            return 0, find_start(band, chromosome)
        else:
            return find_start(band, chromosome), find_end(
                endBand, chromosome)
    else:
        if len(band) == 0:
            return -1, -1
        elif band[0] == 'p':
            # end is always 0
            return 0, find_end(band, chromosome)
        else:
            return find_start(band, chromosome), find_end(
                endBand, chromosome)


class PolyclonalISCN(object):
    """
    Object that describes the full ISCN of a patient in the Mitelman database.
    Attributes:
    errors: a list containing error objects that contain all the errors in
            the database.
    patients: list of Patient objects, each representing a clone
    clones: list of ISCNs
    Methods:
    get_clones(self): splits a polyclonal ISCN into a list of clones. called by
    by __init__
    merge_patients(self, how): merges clones together to make a consensus
    karyotype. how (string)= way it is done. three options.
    first_only - only takes first clones
    merge - merges all clones into a consensus deletions take priority over
    gains and amplifications
    seperate - seperates each clone into individual patients
    """
    def __init__(self, ISCN):
        self.ISCN = ISCN
        Aberration.short_forms = {}
        self.get_clones()
        self.patients = []
    def get_clones(self):
        clones = []
        for clone in self.ISCN.rstrip('\n').split('/'):
            clones.append(MonoclonalISCN(clone))
        self.clones = clones
    def merge_patients(self, how):
        # If only one clone results are unchanged
        if len(self.patients) == 0:
            return pd.DataFrame()
        elif len(self.patients) == 1 or how == 'first_only':
            return self.patients[0]
        elif how == 'seperate':
            # seperates each clone into patients
            result = self.patients[0][['Chromosome','Start','End']]
            for patient in self.patients:
                result = pd.concat([result, patient.iloc[:,3]], axis=1)
            return result
        else: # merge
            # merges all clones - taking the values from every clone
            result = self.patients[0][['Chromosome','Start','End']]
            clones = pd.DataFrame()
            original_name = self.patients[0].iloc[:,3].name
            for clone in self.patients:
                if len(clone.columns) < 4:
                    continue
                clones = pd.concat([clones, clone.iloc[:,3]], axis=1)
            max_abs = lambda x : max(x, key=abs)
            clones = clones.apply(max_abs, axis=1)
            clones.name = original_name.split('.')[0]
            return pd.concat([result, clones], axis=1)

class MonoclonalISCN(object):
    """
    An object that describes the properties of a single monoclonal ISCN.
    Methods: MonoclonalISCN.classify()
    Attributes: hasDer, ISCN, has_idem, ploidity
    """

    def __init__(self, ISCN):
        self.hasDer   = False
        self.ISCN     = ISCN
        self.has_idem = False
        self.ploidity = 2
        self.classify()
        self.errors = []
        try:
            Aberration.short_forms
        except AttributeError:
            Aberration.short_forms = {}
 
    def classify(self):
        """
        Determines what type of chromosomal abnormality an Aberration is and
        appends it to the karyotype dictionary list abs. If the abnormality
        is a derivative collects it in a different location (ders)
        """
        self.aberrs = []
        self.ders   = []
        self.idems  = []
        self.sex    = '?'
        self.allAberrs = self.ISCN.rstrip('\n').split(',')
        self.idem_multiplier = 0
        self.ploidity_list    = []
        if len(self.allAberrs) < 2:
            return  # Catches blank lines
        if re.search('^[0-9]+\-?[0-9]*$', self.allAberrs[0]):
            # Rounds to nearest multiple of 23
            self.ploidity = int(
                23 * round(float(self.allAberrs[0].split('-')[0]) / 23)) // 23
        if 'idem' in self.allAberrs[1]:
            self.idem_multiplier = 1
            self.has_idem = True
            self.sex      = MonoclonalISCN.idem_sex
            has_multiplier = self.allAberrs[1].find('x')
            if has_multiplier > 0:
                self.idem_multiplier = int(self.allAberrs[1]
                                           [has_multiplier + 1])
        for ab in self.allAberrs[1:]:
            # sex chromosomes - if they exist
            ab = ab.replace('?','')
            if re.search('^[XY]+$', ab):
                self.sex = ab
            elif 'der' in ab:  # 17,248 in mm database
                self.hasDer = True
                self.ders.append(Derivative(ab))
            # Regex for '+[chromosome],'
            elif re.search('^\+[XY0-9]{1,2}(\[[0-9]*\])?$', ab):  # Gains
                self.aberrs.append(Gain(ab))
            # Regex for '-[chromosome],'
            elif re.search('^\-[XY0-9]{1,2}(\[[0-9]*\])?$', ab):  # Losses
                self.aberrs.append(Loss(ab))
            elif 'mar' in ab or re.search('^\+?r$', ab):  # marker chromosomes
                pass  # ignores certain unidentifyable chromosomes 
            elif 'del' in ab:  # 24,486 in mmd
                self.aberrs.append(Deletion(ab))
            elif 'add' in ab:  # 14,153 in mmd
                self.aberrs.append(Additio(ab))
            elif re.search('\+?i[^a-z]', ab) or 'idic' in ab:
                self.aberrs.append(Isochromosome(ab))
            elif re.search('du?p|tr?p|qd?p', ab):  # 2,741 amps in db
                self.aberrs.append(Amplification(ab))
            elif 't(' in ab:  # ignores nonquantitative translocations for now
                self.aberrs.append(NonQuantitative(ab))
            elif 'ins' in ab:
                self.aberrs.append(Insertion(ab))
            elif 'inv' in ab or 'hsr' in ab:
                self.aberrs.append(NonQuantitative(ab))
            elif 'dic' in ab:
                self.aberrs.append(Dicentric(ab))
            elif 'trc' in ab:
                self.aberrs.append(Tricentric(ab))
            elif re.search('^\+?r', ab):
                self.aberrs.append(Ring(ab))
            elif 'inc' in ab or ab == '':
                pass
            elif 'fis' in ab:
                self.aberrs.append(Fission(ab))
            # The below statement catches a broad category of
            # well-defined but meaningless objects
            elif 'c' in ab or ab == '' or 'inc' in ab or 'dmin' in ab or\
                 'r' in ab or 'Y' in ab or 'tas' in ab:
                pass
        if self.has_idem:  # idem = all the aberrations of the previous clone
            self.idems += MonoclonalISCN.last_aberrs
            self.idems += MonoclonalISCN.last_ders
            self.sex    = MonoclonalISCN.idem_sex
        # Removes FullLoss and FullGains from last_aberrs allowing 
                # ploidity tobe recalculated
        self.aberrs = [x for x in self.aberrs if type(x)
                            != FullLoss and type(x) != FullGain]
        MonoclonalISCN.last_aberrs = self.aberrs
        MonoclonalISCN.last_ders   = self.ders
        MonoclonalISCN.idem_sex    = self.sex
        # Ploidity can't really be 0, but sometimes rounding error due to many
        # deep losses making the number of chromosomes closer to 0 than to 23
        if self.ploidity == 1 or self.ploidity == 0:
            self.ploidity_list.append(FullLoss(self.ploidity, self.sex))
        # Triploid and tetraploid patients
        elif self.ploidity > 2:
            self.ploidity_list.append(FullGain(self.ploidity, self.sex))
    def update_errors(self):
        """
        Adds the ISCN to the error dictionaries
        """
        for error in self.errors:
            error.full_ISCN = self.ISCN

class Derivative(object):
    """
    An object that describes the properties of a derivative chromosome
    """

    def __init__(self, derISCN):
        self.multiplier = 1
        self.dicentric = False
        if derISCN[0] == '+':
            self.is_gain = True
        else:
            self.is_gain = False
        if derISCN[0] == '-':
            self.is_loss = True
        else:
            self.is_loss = False
        match_chromosome = re.search('der\(([XY0-9]{1,2})\)', derISCN)
        if match_chromosome:
            self.chromosome = match_chromosome.group(1)
        # Finds chromosomes like der(1;2)(p10;q10)
        elif re.search('der\(([XY0-9]{1,2});([XY0-9]{1,2})\)', derISCN):
            match_chromosome = re.search('der\(([XY0-9]{1,2})' +
                                         ';([XY0-9]{1,2})\)', derISCN)
            self.chromosome = match_chromosome.group(1)
            dicentric_match = re.search('der\(([XY0-9]{1,2});([XY0-9]{1,2}' + 
                                        ')\)\([pq0-9]+;[pq0-9]+\)', derISCN)
            if dicentric_match:
                self.dicentric = True
        else:
            self.chromosome = 'undefined'
        self.ISCN = derISCN
        self.is_iso = False
        self.classify()
        self.bands = [aberr.bands for aberr in self.aberrs]
        self.errors = []
        if len(self.bands) > 0:
            self.bands = self.bands[0]

    def classify(self):
        self.aberrs = []
        if self.is_gain:
            self.aberrs.append(Gain(self.ISCN, chromosome=self.chromosome))
        # Regex splits derivative aberrations
        for match in re.finditer('[a-z]{1,4}[\(\);0-9p\-qXY]*', self.ISCN):
            ab = match.group(0)
            if 'der' in ab and self.dicentric:
                self.aberrs.append(Dicentric(ab, chromosome=self.chromosome,
                                             dergain=self.is_gain,
                                             derloss=self.is_loss))
            elif 't(' in ab:
                self.aberrs.append(
                    DerTranslocation(
                        ab,
                        chromosome=self.chromosome,
                        dergain=self.is_gain,
                        derloss=self.is_loss))
                if self.is_iso:
                    self.aberrs.append(
                        DerTranslocation(
                            ab,
                            chromosome=self.chromosome,
                            dergain=self.is_gain,
                            derloss=self.is_loss))
            elif re.search('du?p|tr?p|qd?p', ab):
                self.aberrs.append(
                    Amplification(
                        ab,
                        chromosome=self.chromosome,
                        dergain=self.is_gain,
                        derloss=self.is_loss))
                if self.is_iso:
                    self.aberrs.append(
                        Amplification(
                            ab,
                            chromosome=self.chromosome,
                            dergain=self.is_gain,
                            derloss=self.is_loss))
            elif 'add' in ab:
                self.aberrs.append(
                    Additio(
                        ab, chromosome=self.chromosome,
                        dergain=self.is_gain,
                        derloss=self.is_loss))
                if self.is_iso:
                    self.aberrs.append(
                        Additio(
                            ab,
                            chromosome=self.chromosome,
                            dergain=self.is_gain,
                            derloss=self.is_loss))
            elif 'del' in ab:
                self.aberrs.append(
                    Deletion(
                        ab,
                        chromosome=self.chromosome,
                        dergain=self.is_gain,
                        derloss=self.is_loss))
                if self.is_iso:
                    self.aberrs.append(
                        Deletion(
                            ab,
                            chromosome=self.chromosome,
                            dergain=self.is_gain,
                            derloss=self.is_loss))
            elif 'ins' in ab and self.is_gain:
                self.aberrs.append(
                    Insertion(
                        ab,
                        chromosome=self.chromosome,
                        dergain=self.is_gain,
                        derloss=self.is_loss))
                if self.is_iso:
                    self.aberrs.append(
                        Insertion(
                            ab,
                            chromosome=self.chromosome,
                            dergain=True,
                            derloss=self.is_loss))
            elif ab[0] == 'r':
                self.aberrs.append(
                    Ring(
                        ab,
                        chromosome=self.chromosome,
                        dergain=self.is_gain,
                        derloss=self.is_loss))
            elif 'x' in ab:
                self.multiplier = ab[1]
            elif 'ider' in ab:
                self.aberrs.append(
                    Isochromosome(
                        ab,
                        chromosome=self.chromosome,
                        dergain=self.is_gain,
                        derloss=self.is_loss))
                self.is_iso = True
            elif re.search('^i[^a-z]', ab or idic in ab):
                self.aberrs.append(
                    Isochromosome(
                        ab,
                        chromosome=self.chromosome,
                        dergain=self.is_gain,
                        derloss=self.is_loss))
            elif 'inv' in ab or 'ins' in ab:
                self.aberrs.append(NonQuantitative(ab))
            elif 'inc' in ab or 'tas' in ab or 'der' in ab:
                pass
            elif 'hsr' in ab:
                self.aberrs.append(NonQuantitative(ab))
            elif 'dic' in ab:
                self.aberrs.append(
                    Dicentric(
                        ab,
                        chromosome=self.chromosome,
                        dergain=self.is_gain,
                        derloss=self.is_loss))
            elif 'trc' in ab:
                self.aberrs.append(
                    Tricentric(
                        ab,
                        chromosome=self.chromosome,
                        dergain=self.is_gain,
                        derloss=self.is_loss))
            else:
                pass
                # print('undefined object:' + match.group(0))
            if self.is_loss:
                self.aberrs.append(Loss(' ', chromosome=self.chromosome))

class Aberration:
    """
    An object that describes the properties of a single Aberration.
    Only quantitative Aberrations can be turned into this form for now.
    """

    def __init__(self, abISCN, chromosome='undefined',
                 dergain=False, derloss=False):
        self.ISCN = abISCN
        self.chromosome = chromosome
        self.multiplier = 1
        if dergain:
            self.is_dergain = True
        else:
            self.is_dergain = False
        if self.ISCN[0] == '+':
            self.is_gain = True
        else:
            self.is_gain = False
        if derloss:
            self.is_derloss = True
        else:
            self.is_derloss = False
        if abISCN[0] == '-':
            self.is_loss = True
        else:
            self.is_loss = False
        try:
            Aberration.short_forms
        except AttributeError:
            Aberration.short_forms = {}
            self.short_forms = Aberration.short_forms
        self.bands = self.get_bands()
        self.errors, self.bands = self.analyze_band_errors(self.bands)
        self.short_forms = Aberration.short_forms

    def get_bands(self):
        pass


    def analyze_band_errors(self, d_list):
        """
        Takes a list of dictionaries and returns all the negative one values.
        Also removes them from the list.
        Args:
            d_list: A list of dictionaries containing the parsed ISCN data. Data
                that contains a -1 value in the band start or end represents a
                banding mismatch. These values are removed and added to a list of
                errors objects.
            aberration: The ISCN aberration that caused the error
        """
        if len(d_list) == 0:
            return [], d_list
        errors = []
        for dict in d_list:
            if dict['Start'] == -1 or dict['End'] == -1:
                errors.append(Error_ISCN(self.ISCN))
        # Add classification to errors
        for error in errors:
            error.error_type = 'Unknown Cytogenic Band'
        # Remove errors
        d_list = [d for d in d_list if d['Start'] != -1 and d['End'] != -1]
        return errors, d_list

    def expand(self):
        """
        Looks up short form ISCNs in a dictionary of recently contracted ISCNs
        this dictionary gets reset every PolyclonalISCN initialization.
        If an ISCN cannot be matched using regex, the program will check
        if the ISCN exists in the dictionary of contracted ISCNs.
        Example:
        add(6) cannot be matched with regex as it is missing the required
        breakpoints. If add(6) is a key in the dictionary, then it returns a
        the dictionary associated with the parsed long form ISCN (In this case
        returning the dictionary associated with something such as
        add(6)(q21)). Otherwise will return an empty dictionary.
        """
        long_dl = []
        ISCN = self.ISCN.lstrip('+-')
        if ISCN in self.short_forms:
            long_ISCN = self.short_forms[ISCN][0]
            long_dl = self.short_forms[ISCN][1]
        else:
            long_ISCN = ISCN
        return long_ISCN, long_dl


    def contract(self):
        """
        Takes a long form ISCN for an aberration and creates a short form ISCN
        to be matched with later for expand.
        Example:
        A long ISCN such as add(6)(q21) will be contracted to add(6) and
        stored in a dictionary format for future lookup by expand()
        """
        d = ')'
        contracted = self.ISCN.split(d)[0].lstrip('+-') + d
        return contracted


    def get_quantitative(self, dl):
        """
        Gets gains for gained chromosomes and losses for lost chromosomes.
        Lost chromosomes are specified on aberrations to represent the
        negation of an aberration that is specified by an idem statement.
        Returns a list of dictionaries containing the losses or gains
        of chromosomes.
        +add(6)(q21) represent a gain of every region in chromosome 6 in
        addition to the normal deletion of the section of the q arm.
        -add(6)(q21) describes a loss of the chromosome described in the
        above aberration. This is exclusively used this way if it is a
        loss that was previously described and included using idem.
        """
        if self.is_gain:
            match = re.search('\((\d*);*(\d*);*(\d*)\)', self.ISCN)
            if match:
                for n in [match.group(1), match.group(2), match.group(3)]:
                    if n != '':
                        dl.append({'Chromosome': 'hs' + n,
                                   'Start': 0,
                                   'End': find_end('ter', n),
                                   'Value': 1})
        if self.is_loss or self.is_derloss:
            if len(dl) > 0:
                for dictionary in [dl[0]]:
                    dictionary['Value'] = dictionary['Value'] * -1
            if self.is_loss:
                match = re.search('\((\d*);*(\d*);*(\d*)\)', self.ISCN)
                if match:
                    for n in [match.group(1), match.group(2),
                              match.group(3)]:
                        if n != '':
                            dl.append({'Chromosome': 'hs' + n,
                                       'Start': 0,
                                       'End': find_end('ter', n),
                                       'Value': -1})
        return dl


class FullGain(Aberration):
    """
    Note: Adds Y chromosomes even to female patients, this gets corrected
    by correct_ploidity.
    """
    def __init__(self, copy_number, sex):
        self.sex = sex
        self.gains = copy_number
        self.multiplier = 1
        self.bands = self.get_bands()

    def get_bands(self):
        dl = []
        self.gains -= 2
        for n in range(self.gains):
            for n in list(range(1,23)) + ['X','Y']:
                dl.append({'Chromosome' : 'hs' + str(n), 'Start' : 0,
                           'End' : find_end('ter', str(n)),
                           'Value' : 1})
        return dl


class FullLoss(Aberration):
    """
    Special class of aberration representing a loss of every
    chromosome. Arbitrarily chooses the last sex chromosome
    as a loss. Always losing X might be better behaviour.
    """

    def __init__(self, copy_number, sex):
        self.sex = sex
        self.multiplier = 1
        self.bands = self.get_bands()
    def get_bands(self):
        dl = []
        for n in list(range(1,23)) + ['X','Y']:
           dl.append({'Chromosome' : 'hs' + str(n), 'Start' : 0,\
           'End' : find_end('ter', str(n)), 'Value' : -1})
        return dl


class Tricentric(Aberration):
    """
    A complex abnormality with three chromosomes appended to each other.
    """

    def get_bands(self):
        match = re.search('\(([0-9XY]+);([0-9XY]*);([0-9XY]*)\)' +
                          '\(([pq][0-9]*);([pq][0-9]*)([pq][0-9]*)' +
                          ';([pq][0-9]*)\)',
                          self.ISCN)
        dl = []
        if match:
            chr1, chr2, chr3 = match.group(1), match.group(2), match.group(3)
            d1 = {'Chromosome': 'hs' + chr1, 'Value': -1}
            d1['Start'], d1['End'] = find_span(match.group(4), chr1)
            d2 = {'Chromosome': 'hs' + chr2, 'Value': -1}
            d2['Start'], d2['End'] = find_span(match.group(5), chr2)
            d3 = {'Chromosome': 'hs' + chr2, 'Value': -1}
            d3['Start'], d3['End'] = find_span(match.group(6), chr2)
            d4 = {'Chromosome': 'hs' + chr3, 'Value': -1}
            d4['Start'], d4['End'] = find_span(match.group(7), chr3)
            dl.extend((d1, d2, d3, d4))
            self.short_forms[self.contract()] = [self.ISCN, copy.deepcopy(dl)]
        else:
            self.ISCN, dl = self.expand()
        dl = self.get_quantitative(dl)
        dl = [swap_bands(d) for d in dl]
        return dl


class Fission(Aberration):
    """
    The rarest abnormality, represents a fission at the centromere.
    Will nearly always cancel out a loss of chromosome and always
    contain a +. If there isn't a + I seriously don't know what
    the researcher meant. Luckily they are all correctly entered.
    """

    def get_bands(self):
        dl = []
        match = re.search('\(([0-9XY])+\)\(([pq]10)\)', self.ISCN)
        if match:
            dl.append({'Chromosome': 'hs' + match.group(1), 'Value': 1})
            dl[0]['Start'], dl[0]['End'] = find_span(
                                           match.group(2), match.group(1))
            dl = [swap_bands(d) for d in dl]
            return dl
        else:
            dl = [swap_bands(d) for d in dl]
            return dl


class Insertion(Aberration):
    """
    Describes an insertion object. Insertions are non quantitative
    unless a gained chromosome or on a gained chromosome.
    """

    def get_bands(self):
        dl = []
        chromosome_match = re.search('\(([XY0-9]{1,2});?[^\)]*\)', self.ISCN)
        if chromosome_match:
            self.chromosome = chromosome_match.group(1)
            if self.is_gain or self.is_dergain:
                match = re.search(
                    '\([XY0-9]+;([XY0-9]+)\)\(([pq0-9]+)' +
                    ';([pq][0-9]+)([pq][0-9]+)\)',
                    self.ISCN)
                if match:
                    dl.append({
                                'Chromosome': 'hs' + match.group(1),
                                'Start': find_start(
                                    match.group(3),
                                    match.group(1)),
                                'End': find_end(
                                    match.group(4),
                                    match.group(1)),
                                'Value': 1})
                    self.short_forms[self.contract()] = [self.ISCN,
                                                         copy.deepcopy(dl)]
                else:
                    self.ISCN, dl = self.expand()
                dl = self.get_quantitative(dl)
        dl = [swap_bands(d) for d in dl]
        return dl


class Dicentric(Aberration):
    """
    Describes a dicentric chromosome. A dicentric chromosome is a fusion
    of two chromosomes that includes the centromeres of both chromosomes.
    ----------------------------------------------------------------------
    Example: dic(3;12)(q21;p12) Describes a dicentric chromosome made from
    chromosome 3 and chromosome 12, resulting in a fusion chromosome that
    consists of the regions for q21 to the p terminus of the 3 chromosome
    and from p12 to the q terminus of the 12 chromosome. This results in
    losses of both those regions.
    """

    def get_bands(self):
        dl = []
        match = re.search(
           '\(([XY0-9]*);([XY0-9]*)\)\(([pq0-9]*);([pq0-9]*)\)', self.ISCN)
        if match:
            chr1, chr2, band1, band2 = match.group(
                1), match.group(2), match.group(3), match.group(4)
            d1 = {'Chromosome': 'hs' + chr1, 'Value': -1}
            d1['Start'], d1['End'] = find_span(match.group(3), chr1)
            d2 = {'Chromosome': 'hs' + chr2, 'Value': -1}
            d2['Start'], d2['End'] = find_span(match.group(4), chr2)
            dl.append(d1)
            dl.append(d2)
            dl = [swap_bands(d) for d in dl]
            self.short_forms[self.contract()] = [self.ISCN,
                                                 copy.deepcopy(dl)]
        else:
            self.ISCN, dl = self.expand()
        dl = self.get_quantitative(dl)
        return dl


class Ring(Aberration):
    """
    Describes a ring chromosome
    """
    def get_bands(self):
        dl = []
        chr1, chr2 = '?', '?'  # Prevents errors during lookup if undefined
        # Monocentric Rings
        match = re.search(
            'r\(([XY0-9]+)\)\(([pq][0-9]+)([pq][0-9]+)\)', self.ISCN)
        if match:
            self.chromosome = match.group(1)
            d1 = {'Chromosome': 'hs' + self.chromosome, 'Value': -1}
            d1['Start'], d1['End'] = find_span(
                                     match.group(2), self.chromosome)
            d2 = {'Chromosome': 'hs' + self.chromosome, 'Value': -1}
            d2['Start'], d2['End'] = find_span(
                                     match.group(3), self.chromosome)
            dl = [swap_bands(d) for d in dl]
            self.short_forms[self.contract()] = [self.ISCN, copy.deepcopy(dl)]
        else:
            self.ISCN, dl = self.expand()
        dl = self.get_quantitative(dl)
        return dl
        if ';' in self.ISCN:  # Dicentric/Isocentric Rings
            match = re.search(
                '\(([XY0-9]*);([XY0-9]*)\)\(([pq][0-9]*)' +
                '([pq][0-9]*);([pq][0-9]*)([pq][0-9]*)\)',
                self.ISCN)
            if match:
                chr1, chr2 = match.group(1), match.group(2)
                d1 = {'Chromosome': 'hs' + chr1, 'Value': -1}
                d1['Start'], d1['End'] = find_span(match.group(3), chr1)
                d2 = {'Chromosome': 'hs' + chr1, 'Value': -1}
                d2['Start'], d2['End'] = find_span(match.group(4), chr1)
                d3 = {'Chromosome': 'hs' + chr2, 'Value': -1}
                d3['Start'], d3['End'] = find_span(match.group(5), chr2)
                d4 = {'Chromosome': 'hs' + chr2, 'Value': -1}
                d4['Start'], d4['End'] = find_span(match.group(6), chr2)
                dl.extend((d1, d2, d3, d4))
                self.short_forms[self.contract()] = [self.ISCN,
                                                     copy.deepcopy(dl)]
            else:
                self.ISCN, dl = self.expand()
            dl = self.get_quantitative(dl)
            dl = [swap_bands(d) for d in dl]
            return dl

class NonQuantitative(Aberration):
    """
    Describes non-quantitative aberrations including reciprocal translocations,
    inversions, insertions, homologous staining regions as these types of
    abnormalities can exist on gained chromosomes resulting in gains.

    Maybe eventually will be upgraded to include descriptions of break and
    fusion points, so that translocations can be drawn using this program.
    For now for single drawings of ISCN data I would recommend cyDas.org
    tools for visualization. For larger data sets their approach is not as
    good or fast for quantitative data as this program.
    """

    def get_bands(self):
        dl = []
        self.short_forms[self.contract()] = [self.ISCN, copy.deepcopy(dl)]
        # if no breakpoints it is a short form aberration
        if re.match('^[a-z]*\([0-9XY]\)$', self.ISCN):
            self.ISCN, dl = self.expand()
        dl = self.get_quantitative(dl)
        return dl


class Amplification(Aberration):
    """
    Describes duplications, triplications, quadrupulations
    """
    def get_bands(self):
        dl = []
        d = {}
        loci = re.search('\(([^)]+)\)\(([qp][0-9]*)([qp][0-9]*)\)', self.ISCN)
        # for rare single band amplifications
        loci_2 = re.search('\(([^)]+)\)\(([qp][0-9]*)\)', self.ISCN)
        if loci:
            self.chromosome = loci.group(1)
            band1, band2 = loci.group(2), loci.group(3)
            d['Start'] = find_start(band1, self.chromosome)
            d['End'] = find_end(band2, self.chromosome)
            # Inverted duplications
            if d['Start'] > d['End']:
                d['Start'] = find_end(band1, self.chromosome)
                d['End'] = find_start(band2, self.chromosome)
            d['Chromosome'] = 'hs' + self.chromosome
            if 'dup' in self.ISCN or self.ISCN[:2] == 'dp':
                d['Value'] = 1
            elif 't' in self.ISCN:
                d['Value'] = 2
            elif 'q' in self.ISCN:
                d['Value'] = 3
            dl.append(d)
            dl = [swap_bands(d) for d in dl]
            self.short_forms[self.contract()] = [self.ISCN, copy.deepcopy(dl)]
        # Single band duplications - very rare
        elif loci_2:
            self.chromosome = loci_2.group(1)
            band1, band2 = loci_2.group(2), loci_2.group(2)
            d['Start'] = find_start(band1, self.chromosome)
            d['End'] = find_end(band2, self.chromosome)
            # Inverted duplications
            if d['Start'] > d['End']:
                d['Start'] = find_end(band1, self.chromosome)
                d['End'] = find_start(band2, self.chromosome)
            d['Chromosome'] = 'hs' + self.chromosome
            if 'dup' in self.ISCN or self.ISCN[:2] == 'dp':
                d['Value'] = 1
            elif 't' in self.ISCN:
                d['Value'] = 2
            elif 'q' in self.ISCN:
                d['Value'] = 3
            dl.append(d)
            dl = [swap_bands(d) for d in dl]
            self.short_forms[self.contract()] = [self.ISCN, copy.deepcopy(dl)]
        else:
            self.ISCN, dl = self.expand()
        dl = self.get_quantitative(dl)
        return dl


class Isochromosome(Aberration):
    """
    Describes a isochromosome, a chromosome with one arm completely replaced
    by the other.Example: i(17)(q10) describes a chromosome where the p band
    has been entirely replaced by the qband. q10 is a special ISCN designation
    which represents the centromere. Some isodicentric chromosomes are
    miscategorized as isochromosomes, so this class is used to describe both
    isochromosomes and isodicentrics with get_bands() applicable to both.
    Conversely, some isochromosomes are also miscategorized as isodicentrics.
    """

    def get_bands(self):
        dl = []
        loci = re.search('\(([XY0-9]*)\)\(([pq0-9]*)\-?\)?', self.ISCN)
        if loci:
            self.chromosome, band = loci.group(1), loci.group(2)
            if not re.search(
                    '\([pq]10\)', self.ISCN):  # isodicentrics this way
                dl = [{'Chromosome': 'hs' + self.chromosome},
                      {'Chromosome': 'hs' + self.chromosome}]
                dl[0]['Start'], dl[0]['End'] = find_span(
                  band, self.chromosome, includes_centromere=True)
                dl[0]['Value'] = 1
                dl[1]['Start'], dl[1]['End'] = find_span(
                                               band, self.chromosome)
                dl[1]['Value'] = -1
            else:  # Real isochromosomes go this way
                dl = [{'Chromosome': 'hs' + self.chromosome},
                      {'Chromosome': 'hs' + self.chromosome}]
                dl[0]['Start'], dl[0]['End'] = find_span(
                                               band, self.chromosome)
                dl[0]['Value'] = 1
                if band[0] == 'p':
                    opposite_band = 'q10'
                else:
                    opposite_band = 'p10'
                dl[1]['Start'], dl[1]['End'] = find_span(
                                               opposite_band, self.chromosome)
                dl[1]['Value'] = -1
            self.short_forms[self.contract()] = [self.ISCN, copy.deepcopy(dl)]
        else:
            self.ISCN, dl = self.expand()
        dl = self.get_quantitative(dl)
        dl = [swap_bands(d) for d in dl]
        return dl


class Deletion(Aberration):
    """
    Describes interstital and terminal chromosomal deletions.
    Records all regions lost as losses.
    Example:
    del(6)(q11) - a terminal deletion that describes the loss of all regions
    from q11 to the q terminal.
    del(6)(q11q21) - an interstital deletion describing the loss of regions
    from q11 to q21.
    """
    def get_bands(self):
        dl = []
        d = {}
        loci = re.search(
            '\(([XY0-9]*)\)\(([pq][0-9]*)([pq][0-9]*)*\)', self.ISCN)
        if loci:
            self.chromosome, band = loci.group(1), loci.group(2)
            if loci.group(3):  # if deletion is interstitial
                endband = loci.group(3)
                # Centromere spanning interstitial deletions
                if band[0] != endband [0]:
                    # makes p first always
                    if band[0] == 'q':
                        band, endband = endband, band
                    d['Start'], d['End'] = find_span(band, self.chromosome,
                                  includes_centromere=True, endBand=endband)
                    d['Value'] = -1
                elif band[0] == 'p':
                    band, endband = endband, band
                d['Chromosome'] = 'hs' + self.chromosome
                d['Start'] = find_start(band, self.chromosome)
                d['End'] = find_end(endband, self.chromosome)
                d['Value'] = -1
            else:  # if terminal deletion
                d['Chromosome'] = 'hs' + self.chromosome
                d['Start'], d['End'] = find_span(
                    band, self.chromosome)
                d['Value'] = -1
            dl.append(swap_bands(d))
            self.short_forms[self.contract()] = [self.ISCN, copy.deepcopy(dl)]
        else:
            self.ISCN, dl = self.expand()
        dl = self.get_quantitative(dl)
        return dl


class DerTranslocation(Aberration):
    """
    Describes a translocation resulting in a derivative chromosome.
    """
    def get_bands(self):
        dl = [{}, {}]
        loci = re.search(
            '\(([0-9]*);([0-9]*)\)\(([pq0-9]*);([pq0-9]*)\)', self.ISCN)
        if loci:
            chr, donor_chr, band, donor_band = loci.group(
                1), loci.group(2), loci.group(3), loci.group(4)
            dl[0]['Chromosome'] = 'hs' + chr
            dl[1]['Chromosome'] = 'hs' + donor_chr
            dl[0]['Start'], dl[0]['End'] = find_span(band, chr)
            dl[1]['Start'], dl[1]['End'] = find_span(donor_band, donor_chr)
            for d in dl:
                if d['Chromosome'] == 'hs' + self.chromosome:
                    d['Value'] = -1
                else:
                    d['Value'] = 1
            self.short_forms[self.contract()] = [self.ISCN, copy.deepcopy(dl)]
        else:
            self.ISCN, dl = self.expand()
        dl = [swap_bands(d) for d in dl]
        dl = self.get_quantitative(dl)
        return dl


class Gain(Aberration):
    """
    Describes a gain of a chromosome.
    Example:
    +X means a gain of X. All regions of the X chromosome are recorded
    as a gain.
    """
    def get_bands(self):
        dl = []
        d = {}
        if self.chromosome == 'undefined':
            match = re.search('([0-9XY]{1,2})', self.ISCN)
            if match:
                self.chromosome = match.group(1)
        d['Chromosome'] = 'hs' + self.chromosome
        d['Start'] = 0
        d['End'] = find_end('ter', self.chromosome)
        d['Value'] = 1
        dl.append(d)
        return dl


class Loss(Aberration):
    """
    Describes a loss of a full chromosome. No band swapping needed here.
    Example:
    -X means a loss of X. All regions of the X chromosome are record as a
    loss.
    """

    def get_bands(self):
        dl = []
        d = {}
        if self.chromosome == 'undefined':
            self.chromosome = self.ISCN[1:]
        d['Chromosome'] = 'hs' + self.chromosome
        d['Start'] = 0
        d['End'] = find_end('ter', self.chromosome)
        d['Value'] = -1
        dl.append(d)
        return dl


class Additio(Aberration):
    """
    Describes an addition of additional material of unknown origin replacing
    a band. Note that unknown material that is inserted into a band is defined
    as an insertion of a ? band such as: ins?(chr)(band).
    Bands swap occurring if start is greater than end.
    Example: add(6)(q23) describes the replacement of material from q23 to the
    end of the q terminal with material of unknown origin resulting in a loss
    from q23 -> qter
    """

    def get_bands(self):
        dl = []
        d = {}
        self.chromosome = re.search('\(([^)]+)', self.ISCN).group(1)
        loci = re.search(
            '\??\([^)]+\)\((?P<band>[qp][^qp;\-)]+)\)\??', self.ISCN)
        # Makes sure there are valid loci
        # Many database entries are blank, or incomplete
        if loci:
            band = loci.group('band')
            d['Start'], d['End'] = find_span(band, self.chromosome)
            d['Value'] = -1
            d['Chromosome'] = 'hs' + self.chromosome
            dl.append(d)
            self.short_forms[self.contract()] = [self.ISCN, copy.deepcopy(dl)]
        else:
            self.ISCN, dl = self.expand()
        dl = [swap_bands(d) for d in dl]
        dl = self.get_quantitative(dl)
        return dl


class Error_ISCN:
    """
    Describes an erroneous ISCN.
    Attributes:
        error_type: The type of error.
        ISCN: The complete ISCN that contains the error.
        error: The section of ISCN that caused the error.
    """
    def __init__(self, aberration):
        self.error_type = 'Unknown'
        self.aberration = aberration

    def classify_error(self, ISCN):
        """
        classification of errors by comparing to full ISCN
        Args:
            ISCN(string): a full ISCN representing an entire patient
        """
        if self.aberration == ' ': # I have no clue why I get an empty space
                                   # in literally 1 entry of 70000+
            pass
        elif self.error_type == 'Unknown Cytogenic Band':
            question_list = re.split('[,/]', ISCN)
            questionless_list = re.split('[,/]', ISCN.replace('?',''))
            try:
                ab_index = questionless_list.index(self.aberration)
                if question_list[ab_index] == questionless_list[ab_index]:
                    self.aberration = question_list[ab_index]
                    self.error_type = 'Incorrect Cytogenic Band'
                else:
                    self.error_type = 'Unspecified Cytogenic Band'
            except ValueError:
                for index, ab in enumerate(questionless_list):
                    if self.aberration in ab:
                        der_index = index
                    else:
                        self.error_type = 'Syntax'
                        return self
                n = 0
                for ql_match in re.finditer('[a-z]{1,4}[\(\);0-9p\-qXY]*',
                                            questionless_list[der_index]):
                    if self.aberration == ql_match.group(0):
                        ab_index = n
                    else:
                        n += 1
                origin_der = re.finditer('[a-z]{1,4}[\?\(\);0-9p\-qXY]*',
                         questionless_list[der_index])
                n = 0
                for match in origin_der:
                    if n == ab_index:
                        origin = match.group(0)
                    else:
                        n += 1
                if origin == self.aberration:
                    self.error_type = 'Incorrect Cytogenic Band'
                else:
                    self.error_type = 'Unspecified Cytogenic Band'
            # Little bit more complicated to add back question marks here
        return self



class Patient:
    """
    Object for patient associated data. May later expand to get
    different information if the input data type is Mitelman.
    Attributes:
        ISCN: The ISCN associated with a patient
        quantitative: A dataframe containing the quantitative results of parsing ISCN
        errors: A list containing error objects
        dependence: A dataframe containing the cooccurance of a patients
            aberrations
        occurances (dictionary): A dictionary containing a each aberration that
           occured in this patient to be able to calucate most frequent
           aberrations across multiple patients.
    """
    def __init__(self, ISCN):
        self.ISCN = ISCN
        self.errors = []
        self.quantitative = pd.DataFrame()
        self.dependence = pd.DataFrame()
        self.occurances = {'Total patients' : 1}

    def add_errors(self, error_list):
        """
        Takes a list of errors and turns them into a list of dictionarys.
        Later this is converted into a single dataframe for output to
        tsv.
        Args:
            error_list: A list of error objects
        """
        # Turn into dictionary
        for error in error_list:
            error = error.classify_error(self.ISCN)
            self.errors.append({'error type' : error.error_type,
                                'error location' : error.aberration,
                                 'patient ISCN' : self.ISCN})
    def add_occurance(self, ISCN):
        """
        Adds occurances to a dictionary of occurances.
        Parameters:
            ISCN (string):The ISCN of a single aberration.
        Returns:
            None
        """
        try:
            self.occurances[ISCN] += 1
        except KeyError:
            self.occurances[ISCN] = 1

    def __str__(self):
        return self.ISCN, self.occurances, self.quantitative

def view_menu(parameters):
    """
    Prints the currently listed parameters.
    Called by main_menu()
    ARGUMENTS
    options -- a dictionary
    """
    # Copies as to not modify original list
    options = copy.deepcopy(parameters)
    index = 1
    if not options['analyze dependencies']:
        options['dependence quantile'] = 'N/A'
        options['links filename'] = 'N/A'
    if not options['count recurrant aberrations']:
        options['recurrance filename'] = 'N/A'
    else:
        options['gains filename'] = 'N/A'
        options['losses filename'] = 'N/A'
        options['deepgains filename'] = 'N/A'
        options['deeplosses filename'] ='N/A'
        options['raw data filename'] = 'N/A'
        options['error filename'] = 'N/A'
        options['output folder path'] = 'N/A'
    if not options['analyze errors']:
        options['error filename'] = 'N/A'
    # Prints menus
    for name, option in options.items():
        print(str(index), '--', name, '--', option)
        index += 1


def main_menu(parameters):
    """
    Prints a nice main menu to change parameters.
    ARGUMENTS
    parameters -- a dictionary of parameters from parse_file
    RETURN
    a dictionary of parameters to be outputted to parse_file
    """
    names = ['','view']
    index = 1
    indexes = []
    indexed_dict = {}
    print('')
    print('#---------------------------------------------------------------#')
    print('Welcome to ISCNSNAKE! Enter the name or number of the parameter')
    print('to change. When you\'re finished press enter again to run')
    print('Enter \"view\" to view selected options again')
    print('')
    view_menu(parameters)
    for name, parameter in parameters.items():
        indexed_dict[str(index)] = name
        names.append(name)
        indexes.append(str(index))
        index += 1
    print('')
    user_input = str(input())
    while user_input != '':
        valid_option = False
        # Turns integer indexes into strings
        if user_input in indexes:
           user_input = indexed_dict[user_input]
        if user_input not in names and user_input not in indexes:
            print('Invalid selection')
        elif user_input == 'output mode':
            print('Available options: [relative, absolute, minmax]')
            option = input(
            'Enter an option from the list of available options: ')
            while not valid_option:
                if option in ['relative', 'absolute', 'minmax']:
                    valid_option = True
                    parameters[user_input] = option
                else:
                    print('Invalid option.')
                    option = input(
                    'Enter an option from the list of available options: ')
        elif user_input == 'dependence quantile':
            option = input(
            'Enter a floating point value between 0 and 1: ')
            while not valid_option:
                try:
                    option = float(option)
                    if option >= 0 and option < 1:
                        parameters[user_input] = option
                        valid_option = True
                    else:
                        print('Invalid option.')
                        option = input(
                        'Enter a floating point value between 0 and 1: ')
                except(ValueError):
                    print('Invalid option.')
                    option = input(
                    'Enter a floating point value between 0 and 1: ')
        elif user_input == 'clone handling (first_only/seperate/merge)':
            parameters[user_input] = input(
            'Enter either "first_only", "seperate", or "merge"')
            while not valid_option:
                if parameters[user_input] not in ['first_only','seperate','merge']:
                    print('Invalid selection')
                    parameters[user_input] = input(
                        'Enter either "first_only", "seperate", or "merge"')
            else:
                valid_option = True
        elif user_input in [x for x in names if x[-4:] == 'name']:
            parameters[user_input] = input('Enter a new filename: ')
        elif user_input == 'output folder path':
            parameters[user_input] = input('Enter path to desired output folder: ')
        elif user_input == 'current filters':
            print('Enter the column name, followed by the item you want to select for')
            print('ex: Topography:Breast')
            parameters[user_input] = []
            new_filter = input()
            parameters[user_input].append(new_filter)
            end = False
            print('To add more filters, enter them now in the same format')
            print('To delete the last filter you added type \"remove\"')
            print('To stop adding filters type \"done\" or press enter')
            selection = input()
            while not end:
                 if selection == 'done' or selection == '"done"' or selection == '':
                     end = True
                 elif selection == 'remove' or selection == '"remove"':
                     del parameters[user_input][-1]
                 else:
                     new_filter = selection
                     parameters[user_input].append(new_filter)
                 if not end:
                     selection = input()
        elif user_input == 'input data type (ISCN/Mitelman)':
            parameters[user_input] = input(
            'Enter ISCN/Mitelman for ISCN only or Mitelman formatted input data: ')
        elif user_input == 'view':
            new_index = 1
            print('')
            view_menu(parameters)
            print('')
        else:
            option = input('Enter True or False: ')
            while not valid_option:
                if option in ['T','t','True','true']:
                    option = True
                    parameters[user_input] = option
                    valid_option = True
                elif option in ['F','f','False','false']:
                    option = False
                    parameters[user_input] = option
                    valid_option = True
                else:
                    print('Invalid option.')
                    option = input(
                    'Enter True or False: ')
        user_input = input()
    return parameters


def make_filters(filters_string):
    """
    Takes filters from the main menu and turns them from strings to
    dictionaries
    Parameters:
        filters: a list of strings
    Returns:
        dictionary in the format {column : [acceptable_item]}
    """
    filter_dict = {}
    if filters_string == 'none':
        return filter_dict
    elif type(filters_string) == list:
        for filter_item in filters_string:
            filters = filter_item.split(':')
            try:
                filter_dict[filters[0]].append(filters[1])
            except KeyError:
                filter_dict[filters[0]] = [filters[1]]
        return filter_dict
    else:
        filters = filters_string.split('//')
        for filter in filters:
            filter_list = filter.split(':')
            try:
                filter_dict[filter_list[0]].append(filter_list[1])
            except KeyError:
                filter_dict[filter_list[0]] = [filter_list[1]]
        return filter_dict


def apply_filters(row, filters):
    """
    Takes a Mitelman row as input and returns True or False based
    on the columns.
    Parameters:
        row: A namedtuple from the output of itertuples
        filters: A dictionary containing {column : filter}
    Return:
        bool: True if matches filter False otherwise
    """
    if filters == {}:
        return True
    else:
        mit_cols = {'Reference Number' : 1,
                    'Case Number' : 2,
                    'Investigation Number' : 3,
                    'Author, Year' : 4,
                    'Journal Name' : 5,
                    'Volume, Page' : 6,
                    'Morphology' : 7,
                    'Topography' : 8}
        for key, filterlist in filters.items():
            index = mit_cols[key]
            if row[index] not in filterlist:
                return False
        return True

class parsed_ISCN(object):
    """
    A class that stores output data from parse_file.
    Attributes:
        parsed_ISCN.quantitative(pandas.DataFrame):
        parsed_ISCN.raw(pandas.DataFrame):
        parsed_ISCN.dependence(pandas.DataFrame):
        parsed_ISCN.errors(pandas.DataFrame):
        parsed_ISCN._default_filenames(Dictionary):
            A dictionary that contains the default filenames gains.txt,
            losses.txt, deepgains.txt, and deeplosses.txt.
    Methods:
        parsed_ISCN.to_csv()
            Outputs all data to tab separated text files, default filenames
            will be used unless specified.
    """
    def __init__(self, input_filenames):
        self.quantitative = pd.DataFrame([{'gains':0,'losses':0,'deepgains':0,
                                           'deeplosses':0}])
        self.template = _template
        self.raw          = pd.DataFrame()
        self.dependence   = pd.DataFrame()
        self.errors       = []
        self.filenames    = input_filenames
        self.occurances   = {}
        self.output_errors = False

    def combine_occurances(self, occurance_dict):
        """
        Adds all occurances from a patient to a large dictionary containing
        all occurances from all previous patients.
        Parameters:
            occurance_dict (dictionary): a dictionary in the format {ISCN:int}
                containing the occurances of ISCN aberrations across a single
                patient.
        """
        for key, value in occurance_dict.items():
            if len(key) > 3:
                key = key.lstrip('+-')
                key = key.rstrip('x23456789')
            try:
                self.occurances[key] += value
            except KeyError:
                self.occurances[key] = value

    def to_csv(self, delimiter='\t'):
        owd = os.getcwd()
        if self.filenames['folder path'] != 'None':
            if not os.path.exists(self.filenames['folder path']):
                os.makedirs(self.filenames['folder path'])
            os.chdir(self.filenames['folder path'])
        pd.concat([_template, self.quantitative['gains']], axis=1).to_csv(
                  path_or_buf=self.filenames['gains'], sep=delimiter,
                  index=False)
        pd.concat([_template, self.quantitative['losses']], axis=1).to_csv(
                  path_or_buf=self.filenames['losses'], sep=delimiter,
                  index=False)
        pd.concat([_template, self.quantitative['deepgains']], axis=1).to_csv(
                  path_or_buf=self.filenames['deepgains'], sep=delimiter,
                  index=False)
        pd.concat([_template, self.quantitative['deeplosses']], axis=1).to_csv(
                  path_or_buf=self.filenames['deeplosses'], sep=delimiter,
                  index=False)
        self.raw.to_csv(
                   path_or_buf=self.filenames['raw'], sep=delimiter,
                   index=False)
        if self.output_errors and len(self.errors) > 0:
            pd.DataFrame(self.errors)[['error type','error location',
                                     'patient ISCN']].to_csv(self.filenames['errors'],
                                     sep=delimiter, index=False)
        if not self.occurances == {}:
            occurance_frame = pd.DataFrame([self.occurances]).T
            occurance_frame = occurance_frame.reset_index(drop=False)
            occurance_frame.columns = ['Aberration', 'Occurances']
            occurance_frame = occurance_frame.sort_values('Occurances',
                                                          ascending=False)
            occurance_frame.to_csv(self.filenames['recurrance'], index=False,
                                   sep=delimiter)
        if not self.dependence.empty:
            self.dependence.to_csv(
                     path_or_buf=self.filenames['links'], sep=delimiter,
                     header=False, index=False)
        os.chdir(owd)


def parse_ISCN(patient, clone_method='merge', dependence=False,
               dependency_dict={}, standalone = True, patient_index=1,
               recurrance=True):
    """
    Analyzes an ISCN, returning a pandas dataframe. ISCNs need to be in short
    form with the largest possible resolution (as in the mitelman database)
    If no variation in gains or losses are found returns an empty dataframe.
    Automatically corrects copy number variation for ploidity.
    Called by ISCN.parse_file.
    Args:
        patient (Patient object): an ISCN representing a patient
    Keyword Arguments
        clone_method (bool): If 'first_only', Only analyzes the first clone in a
            heterogenous tumour karyotype. (Analyzes only first monoclonal
            ISCN if ISCN is polyclonal. No effect on monoclonal ISCNs. If 'merge'
            clonal ISCNs are merged into a single result. If 'seperate' each clone
            is outputted as a seperate patient.
        dependence (bool): *default:False* True if you want a links file
            containing dependence of cytogenic events. In this context this
            answers the question of if event X occurs, how frequent does it
            occur with event Y? Can be very computationally intense on larger
            more aberrant karyotypes.
        standalone (bool): *default:True* Should be True if calling this
            function from the command line False, otherwise. If this is False
            and you call from the command line your results will be lost
            to the aether but I guess you can just use the _ variable to
            get it back.
        recurrance (bool): *default:False* If True, patient object attribute
            'recurrances' is added to, allowing a total of recurrant
            recurrant aberrations to be tallied.
    Returns:
        Patient(object): a container object containing the data
    a dataframe where each patient is represented by a column. Also see kwarg standalone.
    """
    if type(patient) == str:
        patient = Patient(patient)
    full_ISCN = PolyclonalISCN(patient.ISCN)
    all_clones = full_ISCN.clones
    if clone_method == 'first_only':
        all_clones = [all_clones[0]]
    ISCNFrame = pd.DataFrame()
    for index, karyotype in enumerate(all_clones):
        all_aberrations    = []
        all_deraberrations = []
        all_ploidity       = []
        clone_index = index
        all_idems   = []
        # Derivatives analyzed first
        for der in karyotype.ders:
            for aberr in der.aberrs:
                karyotype.errors += aberr.errors
                for n in range(int(der.multiplier)):
                    all_deraberrations = all_deraberrations + aberr.bands
                if recurrance:
                    patient.add_occurance(aberr.ISCN)
        # Analyzes remaining quantitative aberrations
        for aberr in karyotype.aberrs:
            karyotype.errors += aberr.errors
            for n in range(int(aberr.multiplier)):
                all_aberrations = all_aberrations + aberr.bands
            if recurrance:
                patient.add_occurance(aberr.ISCN)
        karyotype.update_errors()
        patient.add_errors(karyotype.errors)
        # Analysis of idem statements
        if karyotype.idem_multiplier > 0:
            for idem in range(karyotype.idem_multiplier):
                for item in karyotype.idems:
                    for n in range(int(item.multiplier)):
                        all_idems = all_idems + item.bands
        # Adding gains and losses from changes in ploidity
        if len(karyotype.ploidity_list) > 0:
            for item in karyotype.ploidity_list:
                all_ploidity = all_ploidity + item.bands
        if len(all_aberrations) + len(all_deraberrations) + len(all_idems)\
           > 0:
            patient_frame = pd.DataFrame(all_deraberrations +
                                         all_aberrations + all_idems +
                                         all_ploidity
                                         )[['Chromosome', 'Start',
                                            'End', 'Value']]
            patient_frame = sum_patient(patient_frame, _template)
            if not patient_frame.empty:
                patient_frame = patient_frame.drop(['Chromosome',
                                                    'Start', 'End'], axis=1)
            patient_frame = correct_ploidity(patient_frame, karyotype)
            patient_i = ('Patient_' + str(patient_index)
                         + '.' + str(clone_index))
            patient_frame.columns = [patient_i]
            # Removes unvariant patients
            if patient_frame[patient_i].var() == 0.0:
                patient_frame = pd.DataFrame()
            if dependence:
                dependency_dict = analyze_dependencies(dependency_dict,
                                                       patient_frame)
            ISCNFrame = pd.concat([_template, patient_frame], axis=1)
            full_ISCN.patients.append(ISCNFrame)
        else:
            pass
    # merge clones, depending on argument
    final_frame = full_ISCN.merge_patients(clone_method)

    # drops the template columns
    if not standalone and not final_frame.empty:
        final_frame = final_frame.drop(['Chromosome','Start','End'], axis=1)
    if dependence:
        patient.dependence = dependency_dict
    patient.quantitative = final_frame
    return patient


def parse_file(filename,
               clone_method='merge', verbose=False, dependence=False,
               skip_menu=False, autocsv=True,
               dependence_quantile = 0.9, datatype='ISCN',
               mode='relative', folderpath='pySCN_results',
               gainname='gains.txt', lossname='losses.txt',
               deepgainname='deepgains.txt', rawname='rawISCN.txt',
               deeplossname='deeplosses.txt', linksname='links.txt',
               errorname='errors.txt', error_analysis=False,
               filters='None', recurrance=True,
               recurrance_filename = 'recurrant_aberrations.txt'):
    """
    Analyzes a file of ISCN data.

    Notes:
        One entry per line only. Make sure the file has only the ISCN data and not
        any headers or other columns. Feel free to accomplish this with your
        favourite unix command (such as cut) or alternatively use microsoft excel
        to remove unwanted columns and rows then export as csv.

    Args:

        filename (string): The path to the file to be analyzed.

    Keyword args:
        datatype(string): *default: ISCN* this specifies the type of input
            you are passing to this program. If 'ISCN' is specified then it
            will assume that the only column in your file is your ISCN.
            If Mitelman is selection
        clone_method(string): *default: 'merge'* Three options:'merge' reads
            and analyzes all clones, then merges them into a consensus at the
            end. 'seperate' outputs each clone as a seperate patient.
            'first_only' analyzes only the fist clone.
        mode (string): *default:'relative'* One of:
            ``['relative', 'absolute', 'minmax','raw']``
            Determines the format of the output and statistical treatment of
            data. See the quickstart guide for an explanation of output types.
        verbose (bool): *default:False* Prints each ISCN to the console as it
            is analyzed. Also prints when it reaches the final stages of the
            algorithm.
        folderpath (string): *default:'..\\pySCN_outputs'* Path to the folder
            where all files are outputted. If you want to have the files in
            the same folder as the one you are working in enter this as ".".
        rawname (string): *default:'rawISCN.txt'* Name of the file where raw
            data is outputed if mode is set to raw.
        gainname (string): *default:'gains.txt'* Name of the file where
            single gains are outputted.
        lossname (string): *default:'losses.txt'* Name of the file where
            single losses are outputted.
        deepgainname (string): *default:'deepgains.txt'* Name of the file
            where gains of 2+ are outputted.
        deeplossname (string): *default:'deeplosses.txt'* Name of the file
            where deep losses are outputted. A deep loss is a chromosomal
            region where there is no longer a single copy of that region
            remaining in the patient karyotype (all copies of a given
            region have been deleted).
        autocsv (bool): *default:True* If True, automatically outputs the
            results to files. If False, only returns results object. From
            this object you can still output to file using the
            parsed_ISCN.to_csv method.
        skip_menu (bool): *default True* Skips the main menu and uses keyword
            arguments as all parameters. Essential if you want to use in a
            pipeline or script as otherwise the program will pause and wait
            for user input.
        linksname(string):

            *default:'links.txt'*.

            Name of the file where the
            co-occurances are outputted if dependence is specified as True.
            Format of this file is circos single line link format. For
            example a co-occurance between a loss of 1q21 and 2p21 will be
            outputted as:

            ``hs1 142600000 155000000 hs2 41800000 47800000 *info``

            For an explanation as to the contents of the info column see the
            quickstart tutorial.
        dependence (bool): *default:False* Whether or not to calculate
            co-occurance in lost and gained regions. Calculation of this is
            extremely computationally taxing so it is recommended to use on
            only subsets of data. It hasn't even been tested on much more than
            1000 patient entries in ISCN format but the number of patients
            doesn't effect this nearly as much as the complexity of patients.
        dependence_quantile (float):*default:0.9*

            The desired quantile to be applied to the dependence dataframe.
            Only co-occurances that occur with a frequency above the quantile
            point are outputted. This is necessary to avoid enormously large
            output files that contain aberrations that co-occur only once or
            twice (the vast majority of co-occurances). It is recommended that
            you set this fairly high. (0.99 or above for large datasets)
        filters (list): *default*: 'None' Filters to apply to the Mitelman
            database in Mitelman datatype mode. Should be a list of strings
            in the format 'columnname:item'.
    Warning:
        If autocsv is False, and you are running this from a script you must
        declare the results object to a variable or else your data won't exist
        anymore.
    Returns:
        pandas.DataFrame:
            This depends on the output mode selected but in general this is
            a dataframe that contains some interpretation of ISCN data in a
            quantitative format. See the quickstart guide for an in depth
            explanation of output formats.
    """
    if mode not in ['relative', 'absolute','minmax']:
        raise Exception('Option: ' + mode + ' not supported.')
    if not skip_menu:
        # Makes a dictionary of keyword arguments
        parameters = {
        'input filename' : filename,
        'input data type (ISCN/Mitelman)' : datatype,
        'clone handling (first_only/seperate/merge)' : clone_method,
        'output to file' : autocsv,
        'output folder path' : folderpath,
        'output mode' : mode,
        'current filters' : filters,
        'gains filename' : gainname,
        'losses filename' : lossname,
        'deepgains filename' : deepgainname,
        'deeplosses filename' : deeplossname,
        'raw data filename' : rawname,
        'count recurrant aberrations' : recurrance,
        'recurrant aberration filename' : recurrance_filename,
        'analyze dependencies' : dependence,
        'dependence quantile' : dependence_quantile,
        'links filename' : linksname,
        'analyze errors' : error_analysis,
        'error filename' : errorname,
        'verbose' : verbose }
        parameters = main_menu(parameters)
        # Gets the parameters back
        filename = parameters['input filename']
        filters = parameters['current filters']
        clone_method = parameters['clone handling (first_only/seperate/merge)']
        datatype = parameters['input data type (ISCN/Mitelman)']
        autocsv = parameters['output to file']
        mode = parameters['output mode']
        folderpath = '.\\' + parameters['output folder path']
        gainname = parameters['gains filename']
        lossname = parameters['losses filename']
        deepgainname = parameters['deepgains filename']
        deeplossname = parameters['deeplosses filename']
        rawname = parameters['raw data filename']
        errorname = parameters['error filename']
        error_analysis = parameters['analyze errors']
        linksname = parameters['links filename']
        recurrance = parameters['count recurrant aberrations']
        recurrance_filename = parameters['recurrant aberration filename']
        dependence = parameters['analyze dependencies']
        dependence_quantile = parameters['dependence quantile']
        verbose = parameters['verbose']
    # filename dictionary to be passed to results_object
    filenames = {'gains' : gainname,
                 'losses' : lossname,
                 'deepgains' : deepgainname,
                 'deeplosses' : deeplossname,
                 'raw' : rawname,
                 'links' : linksname,
                 'errors' : errorname,
                 'recurrance' : recurrance_filename,
                 'folder path' : folderpath}
    patient_index = 0
    dependency_dict = {}
    filters = make_filters(filters)
    all_patients = pd.DataFrame()
    results_object = parsed_ISCN(filenames)
    if datatype == 'ISCN':
        input_file = pd.read_csv(filename, delimiter='\t',header=None)
    else:
        input_file = pd.read_csv(filename, delimiter='\t', dtype=str)
    for line in input_file.itertuples():
        if datatype =='ISCN':
            ISCN = line[1]
        else:
            if apply_filters(line, filters):
                ISCN = line[9]
            else:
                continue
        if verbose:
            print(ISCN)
        # Catches nan values
        if ISCN != ISCN:
            continue
        patient = Patient(ISCN)
        patient_index += 1
        patient = parse_ISCN(patient,
                             clone_method=clone_method,
                             dependence=dependence,
                             dependency_dict=dependency_dict,
                             standalone=False,
                             patient_index=patient_index,
                             recurrance=recurrance)
        all_patients = pd.concat([all_patients, patient.quantitative], axis=1)
        if recurrance:
            results_object.combine_occurances(patient.occurances)
        results_object.errors += patient.errors
    # Output modification
    results_object.raw = pd.concat([_template, all_patients], axis=1)
    if verbose:
            print('Summing final results')
    results_object.quantitative = sum_all_patients(all_patients)
    if dependence:
        if verbose:
            print('Analyzing dependencies - This may take a while.')
        dependency_frame = make_dependency_frame(dependency_dict,
                                pd.concat([_template, results_object.quantitative],
                                axis=1),
                                dependence_quantile=dependence_quantile)
        results_object.dependence = dependency_frame
        if autocsv:
            dependency_frame.to_csv(path_or_buf=linksname, sep= '\t',
                                    header=False, index=False)
    if mode != 'absolute':
        for column in results_object.quantitative:
            results_object.quantitative[column] = (results_object.quantitative[column]/
                                     all_patients.shape[1])
    if mode == 'minmax':
        for column in results_object.quantitative:
            results_object.quantitative[column] = minmax(
                                             results_object.quantitative[column])
    if error_analysis:
        results_object.output_errors = True
    if autocsv:
        results_object.to_csv()
    return results_object

def correct_ploidity(uncorrected_column, monoclonal_ISCN):
    """
    Corrects haploid and multiploid patients copy number variation for
    chromosomal regions. Patients that have significant degrees of 
    multiploidity present a challenge as it may take many losses to 
    create a deep loss.
    ARGUMENTS
    ISCNFrame       --  DataFrame
                        The outputted results for a patient, uncorrected
                        for ploidity as a single column.
    monoclonal_ISCN --  MonoclonalISCN Object
                        The object that created the ISCNFrame.
    """
    if monoclonal_ISCN.ploidity == 2:
        return uncorrected_column
    variation = monoclonal_ISCN.ploidity - 2
    # Corrects losses and deep losses, gains/deep gains already correct_ploidity
    # after above statement
    corrected_column = uncorrected_column - variation
    corrected_column[(corrected_column > (monoclonal_ISCN.ploidity * -1)) &
                     (corrected_column < 0)] = -1
    corrected_column[corrected_column <= (monoclonal_ISCN.ploidity * -1)] = -2
    return corrected_column

 
def sum_patient(in_frame, _template):
    """
    ARGUMENTS
    KEYWORD ARGUMENTS
    RETURN
    DataFrame representing the patients karyotype
    """
    data_frame = copy.deepcopy(_template)
    data_frame['Patient'] = 0 # creates a new column for each patient
    for row in in_frame.itertuples(index=False):
        if row[1] < row[2]:
            start_index = int(data_frame.loc[(
                data_frame['Chromosome'] == row[0]) & (
                data_frame['Start'] == row[1])].index.values)
            end_index = int(data_frame.loc[(data_frame['Chromosome'] == row[0]) & (
                data_frame['End'] == row[2])].index.values)
            data_frame.loc[(data_frame.index >= start_index) &
                          (data_frame.index <= end_index), 'Patient'] += row[3]
    return data_frame


def minmax(datacolumn):
    """
    Takes a column of data and scales it between the minimum and maximum to 
    between 0 and 1.0. Returns minmax scaled columns.
    ARGUMENTS
    datacolumn -- 
    RETURN
    """
    result = copy.deepcopy(datacolumn)
    if len(result) == 0:
        return
    normalized_df=(result-result.min())/(result.max()-result.min())
    return normalized_df

 
def sum_all_patients(inframe):
    """
    Sums all patients
    ARGUMENTS
    inframe -- 
    RETURN
    """
    # Gains: +1 if 1 or more copies of a region are gained
    gains = copy.deepcopy(inframe)
    gains[gains < 0] = 0
    gains[gains > 0] = 1
    gains = gains.sum(1)
    # Losses: +1 if 1 or more copies of a region are lost
    losses = copy.deepcopy(inframe)
    losses[losses > 0] = 0
    losses[losses < 0] = 1
    losses = losses.sum(1)
    # Deep gains: +1 if 2 or more copies of a region are gained
    deepgains = copy.deepcopy(inframe)
    deepgains[deepgains < 2] = 0
    deepgains[deepgains >= 2] = 1
    deepgains = deepgains.sum(1)
    # Deep losses: +1 if 2 or more copies of a region are lost
    deeplosses = copy.deepcopy(inframe)
    deeplosses[deeplosses > -2] = 0
    deeplosses[deeplosses <= -2] = 1
    deeplosses = deeplosses.sum(1)
    outframe = pd.concat([gains,losses,deepgains,deeplosses], axis=1)
    outframe.columns = ['gains', 'losses',
                        'deepgains', 'deeplosses']
    return outframe

def create_key(row):
    """
    Takes a row of a pandas frame describing losses and gains of chromosomes
    and returns a string to be used as a key in the cooccurance dictionary.
    The key is created this way to be easily and quickly accessed.
    """
    if row[4] > 0:
        value = 'gains-'
    else:
        value = 'losses-'
    key = value + row[1]+'-'+str(row[2]) + '-' + str(row[3])
    return key


def analyze_dependencies(dependency_dict, patient_frame):
    """
    Creates a cytogenic dependency network between gained and lost regions.
    Takes gained regions and lost regions and creates a circos links file.
    Called by
    Args:
        dependency_dict (dictionary):
        patient_frame(pandas.DataFrame):
    """
    patient_frame = pd.concat([_template, patient_frame],axis=1)
    patient_frame = patient_frame.loc[patient_frame[
                                      patient_frame.columns[3]] != 0]
    patient_frame = patient_frame.reset_index(drop=True)
    if len(patient_frame) <= 1:
        return dependency_dict
    for row_1 in patient_frame.itertuples():
        row_1_key = create_key(row_1)
        for row_2 in patient_frame.iloc[row_1[0] + 1:].itertuples():
            row_2_key = create_key(row_2)
            value = max(abs(row_1[4]), abs(row_2[4]))
            # organizes so link on lowest chromosome is written first
            # (alphabetical order thus 19 before 2)
            if (row_1[1]) > (row_2[1]):
                start = row_2_key
                end = row_1_key
            elif row_1[1] == row_2[1] and row_1[2] > row_2[2]:
                start = row_2_key
                end = row_1_key
            elif row_1[1] == row_2[1]:
                start = 0
                end = 0
            else:
                start = row_1_key
                end = row_2_key                
            if start == end:
                pass
            elif start in dependency_dict:
                if end in dependency_dict[start]:
                    dependency_dict[start][end]+= value
                else:
                    dependency_dict[start][end] = value
            else:
                dependency_dict[start] = {end : value}
    return dependency_dict


def make_link(parent_event, child_event, occurances, final_frame):
    """
    Makes a link from the data in a dictionary containing 
    the data required to make a link. Returns a pandas data frame
    row describing a cooccurance between two cytogenic events. Thickness 
    is currently arbitrarily divided by 50. Colors represent the type of 
    cooccurance. Red = mutually lost, blue = mutual gains, purple = one
    loss and one gain. 
    Called by make_dependency_frame() to make links from the data
    stored in the dependence dictionary. 
    ARGUMENTS
    parent_event -- A loss or gain of a chromosome region
    child_event  -- A loss or gain of a chromosome region
    occurances   -- A tuple containing the number of occurances of 
                    the parent and child events respectively
    final_frame  -- The output from parse_file
    RETURN
    A single row of a pandas dataframe consisting of all the data
    required for a single line circos link. 
    """
    output = pd.DataFrame()
    # Deconstruction of the keys
    parent_type, parent_chr, parent_start, parent_end = parent_event.split('-')
    child_type, child_chr, child_start, child_end = child_event.split('-')
    # Statisical sorcery
    # Finds the two locations in the final frame
    parent_val = int(final_frame[parent_type].loc[(final_frame['Chromosome']
                                               == parent_chr) &
                                               (final_frame['Start']
                                               == int(parent_start))])
    child_val = int(final_frame[child_type].loc[(final_frame['Chromosome']
                                               == child_chr) &
                                               (final_frame['Start']
                                               == int(child_start))])
    # Calculates a p value
    significance = ((2*(log2(((parent_val+child_val)/2)))*occurances)
                              /(parent_val+child_val))
    if child_type == parent_type:
        if parent_type == 'gains':
            color = 'color=blue,'
        else:
            color = 'color=red,'
    else:
        color = 'color=purple,'
    thickness = 'thickness=' + str(significance) + 'p'
    data = {'Chromosome1' : [parent_chr],
            'Start1' : [parent_start],
            'End1' : [parent_end],
            'Chromosome2' : [child_chr],
            'Start2' : [child_start],
            'End2' : [child_end],
            'Info' : [color + thickness],
            'Significance' : [significance]}
    output = output.append(pd.DataFrame(data))[['Chromosome1', 'Start1','End1',
                                 'Chromosome2', 'Start2','End2',
                                 'Info', 'Significance']]
    return output


def make_dependency_frame(dependency_dict, final_frame, dependence_quantile):
    """
    From an inputted dictionary of cooccurances and cooccurance frequencies,
    add them together to get values, change colours, analyze frequency etc.
    Returns a dataframe of links in circos format.
    Called by parse_file if dependence is True.
    ARGUMENTS
    dependency_dict -- a dictionary containing aberrations and the aberrations
    that co-occur with them as a dictionary of the aberration and the number
    of cooccurances.
    final_frame     -- the output frame of a parse_file run
    RETURN          
    a pandas dataframe containing the summed information for each aberration
    and its cooccurances.
    """
    link_num = 0
    link_frame = pd.DataFrame()
    
    for key, value in dependency_dict.items():
        for subkey, subvalue in dependency_dict[key].items():
            link_frame = link_frame.append(make_link(
                                           key, subkey, subvalue, final_frame))
    if link_frame.empty:
        return pd.DataFrame()
    # Takes the upper 10% of links default - changed with dependence_quantile
    n_quantile = link_frame['Significance'].quantile(dependence_quantile)
    link_frame = link_frame.loc[(link_frame['Significance'] >= n_quantile) &
                                (link_frame['Significance'] >= 1)]
    return link_frame

