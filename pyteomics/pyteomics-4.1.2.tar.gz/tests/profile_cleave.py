import cProfile

#import custommgf as mgf
from pyteomics import parser, fasta
from collections import deque
from itertools import chain
import re

def custom_cleave(sequence, rule, missed_cleavages=0, min_length=None, **kwargs):
    "Based on pyteomics cleave"
    peptides = set()
    cslen = 1
    cslen_max = missed_cleavages+2
    tmp_range = list(range(cslen_max - 1))
    cleavage_sites = deque([0], maxlen=cslen_max)

    for i in chain([x.end() for x in re.finditer(rule, sequence)],
                   [None]):
        cleavage_sites.append(i)
        if cslen < cslen_max:
            cslen += 1
        for j in tmp_range[:cslen - 1]:
            seq = sequence[cleavage_sites[j]:cleavage_sites[-1]]
            if seq:
                if min_length is None or parser.length(seq, **kwargs) >= min_length:
                    peptides.add(seq)
    return peptides

cProfile.run('''
with fasta.read('/home/lev/Downloads/fasta/sprot_human.fasta') as f:
    for p in f:
        parser.cleave(p[1], parser.expasy_rules['trypsin'])
    ''', 'cleave_profile.out')