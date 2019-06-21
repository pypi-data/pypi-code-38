"""Useful dictionaries to have around for bioinformatics."""

aa = {'A': 'Ala',
      'R': 'Arg',
      'N': 'Asn',
      'D': 'Asp',
      'C': 'Cys',
      'Q': 'Gln',
      'E': 'Glu',
      'G': 'Gly',
      'H': 'His',
      'I': 'Ile',
      'L': 'Leu',
      'K': 'Lys',
      'M': 'Met',
      'F': 'Phe',
      'P': 'Pro',
      'S': 'Ser',
      'T': 'Thr',
      'W': 'Trp',
      'Y': 'Tyr',
      'V': 'Val'}

aa_3_to_1 = {'ALA': 'A',
             'ARG': 'R',
             'ASN': 'N',
             'ASP': 'D',
             'CYS': 'C',
             'GLN': 'Q',
             'GLU': 'E',
             'GLY': 'G',
             'HIS': 'H',
             'ILE': 'I',
             'LEU': 'L',
             'LYS': 'K',
             'MET': 'M',
             'PHE': 'F',
             'PRO': 'P',
             'SER': 'S',
             'THR': 'T',
             'TRP': 'W',
             'TYR': 'Y',
             'VAL': 'V',
             'Ala': 'A',
             'Arg': 'R',
             'Asn': 'N',
             'Asp': 'D',
             'Cys': 'C',
             'Gln': 'Q',
             'Glu': 'E',
             'Gly': 'G',
             'His': 'H',
             'Ile': 'I',
             'Leu': 'L',
             'Lys': 'K',
             'Met': 'M',
             'Phe': 'F',
             'Pro': 'P',
             'Ser': 'S',
             'Thr': 'T',
             'Trp': 'W',
             'Tyr': 'Y',
             'Val': 'V',
             'ala': 'A',
             'arg': 'R',
             'asn': 'N',
             'asp': 'D',
             'cys': 'C',
             'gln': 'Q',
             'glu': 'E',
             'gly': 'G',
             'his': 'H',
             'ile': 'I',
             'leu': 'L',
             'lys': 'K',
             'met': 'M',
             'phe': 'F',
             'pro': 'P',
             'ser': 'S',
             'thr': 'T',
             'trp': 'W',
             'tyr': 'Y',
             'val': 'V'}


# The set of DNA bases
bases = ['T', 'C', 'A', 'G']

# Build list of codons
codon_list = []
for first_base in bases:
    for second_base in bases:
        for third_base in bases:
            codon_list += [first_base + second_base + third_base]

# The amino acids that are coded for (* = STOP codon)
amino_acids = 'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'

# Build dictionary from tuple of 2-tuples (technically an iterator, but it works)
codons = dict(zip(codon_list, amino_acids))

