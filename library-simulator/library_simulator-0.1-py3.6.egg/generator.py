__description__ = \
"""
Main class for generating new clones from the library.
"""
__author__ = "Michael J. Harms"
__date__ = "2019-05-31"

from . import data

import pandas as pd
import numpy as np

import warnings, os, copy

class LibraryGenerator:
    """
    Main class for generating new clones from the library.
    """

    def __init__(self,fasta_file,mutation_spectrum="published",spectrum_tolerance=0.01):
        """
    
        fasta_file: strring indicating a fasta file
        mutation_spectrum: string.  If the string is a file, this will be loaded
                           as a csv file.  If the string is not a file, this will
                           be interpreted as a key pointing to one of the built-in
                           mutation spectra.
        mutation_tolerance: float. The probabilities in the file must sum to 1.0 
                            within the tolerance indicated by mutation_tolerance.
        """

        self._read_fasta_file(fasta_file)
        self._load_mutation_spectrum(mutation_spectrum,spectrum_tolerance)
        self._prep_generator()

        
    def _load_mutation_spectrum(self,mutation_spectrum,spectrum_tolerance):
        """
        Load a mutation spectrum. 
        
        mutation_spectrum: string.  If the string is a file, this will be loaded
                           as a csv file.  If the string is not a file, this will
                           be interpreted as a key pointing to one of the built-in
                           mutation spectra.
        mutation_tolerance: float. The probabilities in the file must sum to 1.0 
                            within the tolerance indicated by mutation_tolerance.
        """
        
        self._mutation_spectrum = mutation_spectrum

        # Load spectrum file
        if not os.path.isfile(self._mutation_spectrum):
            try:
                self._mutation_spectrum = data.built_in_spectra[self._mutation_spectrum]
            except KeyError:
                err = "mutation_spectrum must either be a .csv file OR be one \n"
                err += "the following built-in keys:\n"
                for k in data.built_in_spectra.keys():
                    err += "    {}\n".format(k)
                raise ValueError(err)
            
        self._mut_spect_df = pd.read_csv(self._mutation_spectrum,comment="#") 

        # Check sanity of spectrum file
        if np.abs(1 - np.sum(self._mut_spect_df.prob)) > spectrum_tolerance:
            err = "spectrum probabilites do not sum to 1 within spectrum_tolerance.\n"
            err += "tolerance: {}\n".format(spectrum_tolerance)
            err += "observed sum: {}\n".format(np.sum(self._mut_spect_df))
            raise ValueError(err)

        # Renormalize probabilities to avoid numerical errors later
        self._mut_spect_df.prob = self._mut_spect_df.prob/np.sum(self._mut_spect_df.prob)   

        # Convert to dictionary
        self._mut_spect_dict = {}
        for i in range(len(self._mut_spect_df.start)):

            # Deal with mutate start... 
            mut_start = self._mut_spect_df.start[i]
            if mut_start not in data.base_names:
                err = "base {} (seen in {}) not recognized.\n".format(mut_start,
                                                                      self._mutation_spectrum)
                raise ValueError(err)

            # Deal with mutate end ...
            mut_end = self._mut_spect_df.end[i]
            if mut_end not in data.base_names:
                err = "base {} (seen in {}) not recognized.\n".format(mut_end,
                                                                      self._mutation_spectrum)
                raise ValueError(err)

            # Key the mut_spect_dict to mut_start
            try:
                self._mut_spect_dict[mut_start]
            except KeyError:
                self._mut_spect_dict[mut_start] = {}

            try:
                # Make sure that we see each from/to pair once and only once in
                # the mutatino spectrum.
                self._mut_spect_dict[mut_start][mut_end]
            except KeyError:
                self._mut_spect_dict[mut_start][mut_end] = self._mut_spect_df.prob[i]

 
    def _read_fasta_file(self,fasta_file):
        """
        Read a fasta file, doing some basic sanity checks.

        fasta_file: string indicating a fasta file
        """

        self._fasta_file = fasta_file

        f = open(self._fasta_file,'r')
        lines = f.readlines()
        f.close()

        # Remove blank lines
        lines = [l.strip() for l in lines if l.strip() != ""]

        # Make sure this is a sane, reasonable fasta file
        seq = []
        for i, l in enumerate(lines):
           
            # Make sure first line starts with ">"
            if i == 0:
                if not l[0].startswith(">"):
                    err = "Problem with fasta file.  First line must start with '>'.\n"
                    raise ValueError(err)
           
            # For remaining lines... 
            else:
                # Make sure there is not another ">" -- extra sequence is ambiguous
                if l[0].startswith(">"):
                    err = "Problem with fasta file.  Must only contain one sequence.\n"
                    raise ValueError(err)

                # Grab each base, making sure the base type is recognized
                for s in l:
                    try:
                        data.base_nums[s]
                        seq.append(s)
                    except KeyError:
                        err = "Problem with fasta file. Base '{}' not recognized.\n".format(s)
                        raise ValueError(err)

        self._base_seq = "".join(seq)

        # Create a list of the amino acids encoded in the fasta file
        self._aa_seq = self._translate(self._base_seq)


    def _prep_generator(self):
        """
        Prep the clone generator.  Must be run after the fasta file and mutation
        spectrum have been loaded. 
        """

        mut_sites = []
        mut_probs = []
        self._mut_outcomes = []

        # Go along the bases in sequence
        for i, b in enumerate(self._base_seq):
            try:

                # Sum of all possible moves from the starting base
                weight = sum(self._mut_spect_dict[b].values())
                mut_probs.append(weight)
                mut_sites.append(i)

                # Possible outcomes if this base were mutated
                mut_poss = list(self._mut_spect_dict[b].keys())
                mut_poss = np.array(mut_poss)

                # Weight to give each possible outcome if this base were mutated
                mut_poss_weights = [self._mut_spect_dict[b][m] for m in mut_poss]
                mut_poss_weights = np.array(mut_poss_weights)
                mut_poss_weights = mut_poss_weights/np.sum(mut_poss_weights)
                
                self._mut_outcomes.append((mut_poss,mut_poss_weights))
                
            except KeyError:
                w = "fasta file contains base '{}' which is not seen in the "
                w += "mutation spectrum\n".format(b)
                warnings.warn(w)

        self._mut_sites = np.array(mut_sites)

        # Weight site mutation probabilities to go from zero to 1.0.
        mut_probs = np.array(mut_probs)
        mut_probs = mut_probs/np.sum(mut_probs)
        self._mut_probs = mut_probs

    def _translate(self,base_seq):
        """
        Given a list of bases, return a list of amino acids.  Stop if a stop
        codon is hit.
        """
        
        aa_seq = [] 
        for i in range(len(base_seq) // 3):
            try:
                codon = "".join(base_seq[(3*i):(3*(i+1))])
                aa_seq.append(data.codons[codon])
                if aa_seq[-1] == "*":
                    break
            except KeyError:
                err = "codon {} not recognized\n".format(codon)
                raise ValueError(err)

        return aa_seq


    def generate_clone(self,num_mutations):
        """
        Generate a random clone with num_mutations given the reference sequence
        and mutation spectrum.

        input:
        num_mutations: number of mutations to sample

        returns:
        aa_diffs: list of amino acid differences as tuples (ref_aa,codon,new_aa)
        base_diffs: list of base differences as tuples (ref_base,position,new_base)
        num_diff: number of amino acid differences
        has_indel: bool indicating whether there is an insertion or deletion
        has_stop: bool indicating whether there is a new stop codon introduced
        altered_start: bool indicating whether the start codon was mutated
        """

        # These will store whether or not we have an indel, new stop codon, or
        # altered start codon
        has_indel = False
        has_stop = False
        altered_start = False
    
        # Choose which sites to mutate
        if num_mutations > len(self._mut_sites):
            num_mutations = len(self._mut_sites)

        sites_to_mutate = np.random.choice(self._mut_sites,
                                           size=num_mutations,
                                           replace=False,
                                           p=self._mut_probs)

        # Sort the sites from smallest to largest
        sites_to_mutate = np.sort(sites_to_mutate)
        
        # Choose what the site will be mutated to, recording which codon got hit
        seq = list(self._base_seq)
        altered_codons = []
        base_diffs = []
        for i in sites_to_mutate:
            seq[i] = np.random.choice(self._mut_outcomes[i][0],
                                      p=self._mut_outcomes[i][1])

            base_diffs.append((self._base_seq[i],i,seq[i]))

            # Note if there is an indel
            if seq[i] in ["-","+"]:
                has_indel = True

            # Figure out what codon got modified
            codon_start = (i // 3)
            altered_codons.append(codon_start)

        # Get set of unique codons that were altered.  (Can be less than the
        # num_mutations, as two mutations might have been to the same codon)
        altered_codons = list(set(altered_codons))
        altered_codons.sort()

        # If there is no indel, go through each codon individually
        if not has_indel:

            aa_diffs = []
            for a in altered_codons:
           
                new_codon = "".join(seq[a:(a+3)])

                try:
                    new_aa = data.codons[new_codon]
                except KeyError:
                    err = "mutated codon {} not recognized.\n".format(new_codon)
                    raise ValueError(err)

                # If the amino acid did not change, move on
                if new_aa == self._aa_seq[a//3]:
                    continue
               
                # If there is a stop, break out and do more complicated
                # calc of sequence differences below.
                if new_aa == "*":
                    has_stop = True
                    break

                if a == 0 and self._aa_seq[0] == "M":
                    altered_start = True       

                aa_diffs.append((self._aa_seq[a//3],a,new_aa))

            num_diff = len(aa_diffs)
 
        # If there is an indel or new stop codon, re-translate the entire
        # sequence and compare the number of sequence differences between 
        # them.  
        if has_indel or has_stop:

            seq = [s for s in seq if s not in ["+","-"]]

            new_aa_seq = self._translate(seq)

            shortest_len = min([len(new_aa_seq),len(self._aa_seq)])
            longest_len =  max([len(new_aa_seq),len(self._aa_seq)])

            aa_diffs = [(self._aa_seq[i],i,new_aa_seq[i]) for i in range(shortest_len)
                        if self._aa_seq[i] != new_aa_seq[i]]
           
            num_diff = len(aa_diffs)
            num_diff += (longest_len - shortest_len)
     
            if self._aa_seq[0] == "M" and new_aa_seq[0] != "M":
                altered_start = True
  
                
        return aa_diffs, base_diffs, num_diff, has_indel, has_stop, altered_start

    @property
    def fasta_file(self):
        return self._fasta_file

    @property
    def mutation_spectrum(self):
        return self._mutation_spectrum

    @property
    def mut_spect_dict(self):
        return self._mut_spect_dict

    @property
    def mut_spect_df(self):
        return self._mut_spect_df

    @property
    def base_seq(self):
        return self._base_seq

    @property
    def aa_seq(self):
        return self._aa_seq

    @property
    def mut_sites(self):
        return self._mut_sites

    @property
    def mut_probs(self):
        return self._mut_probs

    @property
    def mut_outcomes(self):
        return self._mut_outcomes
