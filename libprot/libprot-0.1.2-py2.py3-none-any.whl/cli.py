# -*- coding: utf-8 -*-
import re
import sys

import click
import numpy as np
import requests
from Bio import SeqIO
from Bio.PDB import PDBParser, Superimposer, PPBuilder
from Bio.SeqRecord import SeqRecord

from libprot.pdb import get_amino_acids


def error(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


@click.group()
def main():
    pass


@click.command()
@click.option('-i', '--id', 'pdb_id', required=True)
def fetch_pdb(pdb_id):
    pdb_file = f'{pdb_id}.pdb'
    url = f'https://files.rcsb.org/download/{pdb_file}'
    r = requests.get(url)
    with open(pdb_file, 'w') as f:
        f.write(r.text)

    print('saved', pdb_file)


@click.command()
@click.argument('pdb1', type=click.Path(exists=True))
@click.argument('pdb2', type=click.Path(exists=True))
def calc_rmsd(pdb1, pdb2):
    parser = PDBParser()
    first = parser.get_structure(pdb1.replace('.pdb', ''), pdb1)
    second = parser.get_structure(pdb2.replace('.pdb', ''), pdb2)

    fixed = list(first.get_atoms())
    moving = list(second.get_atoms())
    if len(fixed) != len(moving):
        error(f'There is a different number of atoms in {pdb1} ({len(fixed)}) than in {pdb2} ({len(moving)})')

    sup = Superimposer()
    # fixed and moving are lists of atom objects
    sup.set_atoms(fixed, moving)


def edit_distance(seq1, seq2):
    mat = np.zeros(shape=(len(seq1) + 1, len(seq2) + 1), dtype=int)

    # base cases
    for idx in range(mat.shape[0]):
        mat[idx, 0] = idx

    for idx in range(mat.shape[1]):
        mat[0, idx] = idx

    def transition_fn(row, col):
        from_diag = mat[row - 1, col - 1] + int(seq1[row - 1] != seq2[col - 1])
        from_above = mat[row - 1, col] + 1
        from_left = mat[row, col - 1] + 1

        mat[row, col] = min(from_diag, from_above, from_left)

    indices = [(row, col) for row in range(1, mat.shape[0]) for col in range(1, mat.shape[1])]
    for row, col in indices:
        transition_fn(row, col)

    return mat[len(seq1), len(seq2)]


def to_fasta_impl(structure, pdb_id, description, mutations, out_stream):
    if pdb_id is None:
        pdb_id = ""
    if description is None:
        description = ""

    ppb = PPBuilder()
    seq = [pp.get_sequence() for pp in ppb.build_peptides(structure)][0]

    if mutations:
        mut_seq = seq.tomutable()
        mutations = [re.search(r'(?P<original>\D)(?P<index>\d+)(?P<mutation>\D)', line) for line in mutations]
        for mut in mutations:
            idx = int(mut.group('index')) - 1
            old_aa = mut.group('original')
            new_aa = mut.group('mutation')
            if old_aa != mut_seq[idx]:
                raise Exception(
                    f'The amino acid in {pdb_id} at index {mut.group("index")} is {mut_seq[idx]}, not {old_aa}')
            mut_seq[idx] = new_aa
        seq = mut_seq.toseq()

    sequence_record = SeqRecord(seq, id=pdb_id, description=description)
    SeqIO.write([sequence_record], out_stream, "fasta")


@click.command()
@click.argument('pdb', type=click.Path(exists=True))
@click.option('-i', '--id', 'pdb_id', required=False)
@click.option('-d', '--description', 'description', required=False)
@click.option('-m', '--mutation-file', 'mut_file', type=click.Path(exists=True), required=False)
def to_fasta(pdb, pdb_id, description, mut_file):
    parser = PDBParser()

    mutations = []
    if mut_file:
        with open(mut_file, 'r') as mut:
            mutations = [line.strip() for line in mut.readlines()]

    parser = PDBParser()
    structure = parser.get_structure(pdb.replace('.pdb', ''), pdb)

    to_fasta_impl(structure, pdb_id, description, mutations, sys.stdout)


@click.command()
@click.argument('path', type=click.Path(exists=True))
def dump_residues(path):
    amino_acids = get_amino_acids(path)
    for aa in amino_acids:
        print(aa)


@click.command()
def check_dihedrals():
    print('checking dihedrals')


main.add_command(fetch_pdb)
main.add_command(calc_rmsd)
main.add_command(check_dihedrals)
main.add_command(to_fasta)
main.add_command(dump_residues)

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
