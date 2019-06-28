
# -*- coding: utf-8 -*-


import random
import json
import pkgutil


def generate_codon_to_amino_table(codon_usage_table):
    codon_to_amino_table = {}
    for amino in codon_usage_table:
            for codon in codon_usage_table[amino]:
                codon_to_amino_table[codon] = amino
    return codon_to_amino_table


RANDOM_CODON_USAGE_TABLE = json.loads(pkgutil.get_data('copter', 'codon_usage_tables/random.json').decode('utf-8'))
BACTERIAL_CODON_TO_AMINO_TABLE = generate_codon_to_amino_table(RANDOM_CODON_USAGE_TABLE)


def generate_gene(aa_seq):
    return ''.join([amino_to_codon(amino) for amino in aa_seq])


def amino_to_codon(amino, codon_usage_table=RANDOM_CODON_USAGE_TABLE):
    r = random.random()
    sum = 0
    for codon, prob in codon_usage_table[amino].items():
        sum += prob
        if sum >= r:
            return str(codon)


def codon_to_codon(codon,
                   codon_to_amino_table=BACTERIAL_CODON_TO_AMINO_TABLE,
                   codon_usage_table=RANDOM_CODON_USAGE_TABLE):
    amino = codon_to_amino_table[codon]
    return amino_to_codon(amino, codon_usage_table=codon_usage_table)


def has_ng_sequences(codons, ng_sequences):
    gene = ''.join(codons)
    return True in [ng_seq in gene for ng_seq in ng_sequences]
