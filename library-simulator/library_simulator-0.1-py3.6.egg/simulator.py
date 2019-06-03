__description__ = \
"""
Base class for simulating libraries.
"""
__author__ = "Michael J. Harms"
__date__ = "2019-05-31"



from . import generator

import numpy as np
import pandas as pd

class LibrarySimulator:
    
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

        self._generator = generator.LibraryGenerator(fasta_file=fasta_file,
                                                     mutation_spectrum=mutation_spectrum,
                                                     spectrum_tolerance=spectrum_tolerance)

    def simulate(self,num_samples=1000,mutation_rate=1):
        """
        generate a library.

        num_samples: number of samples to create
        mutation_rate: mutation rate
        """

        aa = []
        base = []
        num = []
        indel = []
        stop = []
        start = []

        for i in range(num_samples):
            num_muts = np.random.poisson(mutation_rate)
           
            aa_diffs, base_diffs, num_diff, has_indel, has_stop, altered_start = self._generator.generate_clone(num_muts)

            aa_diffs = ["{}{}{}".format(a[0],a[1],a[2]) for a in aa_diffs]
            aa_diffs = ",".join(aa_diffs)

            base_diffs = ["{}{}{}".format(b[0],b[1],b[2]) for b in base_diffs]
            base_diffs = ",".join(base_diffs)

            aa.append(aa_diffs)
            base.append(base_diffs)
            num.append(num_diff)
            indel.append(has_indel)
            stop.append(has_stop)
            start.append(altered_start)

        self._df = pd.DataFrame({"aa":aa,
                                 "base":base,
                                 "num":num,
                                 "indel":indel,
                                 "stop":stop,
                                 "start":start})

    @property
    def clones(self):

        try:
            return self._df
        except AttributeError:
            return None
             
