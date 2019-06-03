__description__ = \
"""
Various data regarding codons, bases, etc.
"""
__author__ = "Michael J. Harms"
__date__ = "2019-05-31"

import os, glob


codons = {"TTT":"F","TTC":"F","TTA":"L","TTG":"L",
          "TCT":"S","TCC":"S","TCA":"S","TCG":"S",
          "TAT":"Y","TAC":"Y","TAA":"*","TAG":"*",
          "TGT":"C","TGC":"C","TGA":"*","TGG":"W",

          "CTT":"L","CTC":"L","CTA":"L","CTG":"L",
          "CCT":"P","CCC":"P","CCA":"P","CCG":"P",
          "CAT":"H","CAC":"H","CAA":"Q","CAG":"Q",
          "CGT":"R","CGC":"R","CGA":"R","CGG":"R",

          "ATT":"I","ATC":"I","ATA":"I","ATG":"M",
          "ACT":"T","ACC":"T","ACA":"T","ACG":"T",
          "AAT":"N","AAC":"N","AAA":"K","AAG":"K",
          "AGT":"S","AGC":"S","AGA":"R","AGG":"R",

          "GTT":"V","GTC":"V","GTA":"V","GTG":"V",
          "GCT":"A","GCC":"A","GCA":"A","GCG":"A",
          "GAT":"D","GAC":"D","GAA":"E","GAG":"E",
          "GGT":"G","GGC":"G","GGA":"G","GGG":"G"}

# Find unique base and amino acid names within the genetic code
aa_names = []
base_names = []
for codon in list(codons.keys()):
    aa_names.append(codons[codon])
    base_names.extend(list(codon))

# Create list of amino acid names
aa_names = list(set(aa_names))
aa_names.sort()
 
# Create dictionary of amino acid names to numbers
aa_nums = dict([(k,v) for v,k in enumerate(aa_names)])

# Amino acids in human-readable order
human_aa_order = [0,7,9,10,17,4,18,20,11,13,15,16,2,3,6,8,14,1,5,12,19]

# Create list of base names 
base_names = list(set(base_names))
base_names.sort()
base_names.append("-")
base_names.append("+")

# Create dictionary of base names to numbers
base_nums = dict([(k,v) for v,k in enumerate(base_names)])

# Get index of the deletion and insertions in base_names
deletion_index = len(base_names) - 2
insertion_index = len(base_names) - 1

# Create a number-based genetic code
gen_code = {}
for c in list(codons.keys()):
    triplet = tuple([base_nums[p] for p in c])
    aa = aa_nums[codons[c]]
    gen_code[triplet] = aa

# Create a list of stop codons
stop_codons = [k for k in list(gen_code.keys()) if aa_names[gen_code[k]] == "*"]
       
# Create dictionary of recognizable built-in spectra
data_dir = os.path.split(os.path.realpath(__file__))[0]
spectra_dir = os.path.join(data_dir,"mutation_spectra")
files = glob.glob("{}/*.csv".format(spectra_dir))
print(spectra_dir,files)

built_in_spectra = {}
for f in files:
    key = os.path.split(f)[1][:-4]
    built_in_spectra[key] = f

