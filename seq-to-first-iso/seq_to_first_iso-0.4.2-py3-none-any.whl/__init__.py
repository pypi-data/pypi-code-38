
"""Seq-to-first-iso: compute first isotopologues intensities from sequences.

The program differentiate labelled and unlabelled amino acids
for the case of a 99.99 % C[12] enrichment.

Read a file composed of sequences of amino acids on each line and return :
    sequence, mass, formula, formula_X, M0_NC, M1_NC, M0_12C and M1_12C
as a tsv file.
Where formula X is the chemical formula with carbon of unlabelled
amino acids marked as X.
NC are Normal Conditions, 12C are C[12] enrichment Conditions.


Example
-------
Running the script after installation
    $ seq-to-first-iso sequences.txt
will provide file 'sequences_stfi.tsv'


Notes
-----
Carbon of unlabelled amino acids keep default isotopic abundance,
and are represented as X in formulas.
Naming conventions for isotopes follow pyteomics's conventions.

"""

__authors__ = "Lilian Yang-crosson, Pierre Poulain"
__license__ = "BSD 3-Clause License"
__version__ = "0.4.2"
__maintainer__ = "Pierre Poulain"
__email__ = "pierre.poulain@cupnet.net"

from .seq_to_first_iso import (AMINO_ACIDS,
                               C12_abundance,
                               isotopic_abundance,
                               UNIMOD_MODS,
                               sequence_parser,
                               separate_labelled,
                               compute_M0_nl,
                               compute_M1_nl,
                               formula_to_str,
                               seq_to_midas,
                               get_mods_composition,
                               seq_to_tsv,
                               )
__all__ = ["AMINO_ACIDS",
           "C12_abundance",
           "isotopic_abundance",
           "UNIMOD_MODS",
           "sequence_parser",
           "separate_labelled",
           "compute_M0_nl",
           "compute_M1_nl",
           "formula_to_str",
           "seq_to_midas",
           "get_mods_composition",
           "seq_to_tsv",
           ]
