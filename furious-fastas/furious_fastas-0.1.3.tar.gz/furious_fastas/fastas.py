"""Classes representing collections of fastas."""
from collections import defaultdict

from .parse import parse_uniprot_fastas, parse_ncbi_general_fastas


class Fastas(object):
    def __init__(self):
        self.fastas = []

    def read(self, path):
        pass

    def write(self, path, append=False):
        """Write file under the given path.

        Arguments
        =========
        path : str
            Path where to dump the file.
        """
        fp = 'a' if append else 'w+'
        with open(path, fp) as h:
            for f in self.fastas:
                h.write("{}\n{}\n".format(f.header, f.sequence))

    def __iter__(self):
        """Iterate over sequences."""
        for f in self.fastas:
            yield f

    def __len__(self):
        """Return the number of sequences in the fasta file.""" 
        return len(self.fastas)

    def __getitem__(self, key):
        """Return the key-th fasta sequence."""
        return self.fastas[key]

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, len(self))

    def reverse(self):
        """Produce new Fastas containing reversed copy of sequences."""
        rev_self = self.copy()
        for f in self:
            rev_self.fastas.append(f.reverse())
        return rev_self

    def copy(self):
        r = self.__class__()
        for f in self:
            r.fastas.append(f.copy())
        return r

    def append(self, other):
        """Append copies of fastas."""
        assert issubclass(other.__class__, self.__class__), "Can only add the same type of fastas."
        if self != other:
            for f in other:
                self.fastas.append(f.copy())

    def __add__(self, other):
        """Add two fastas.

        Args:
            other (Fastas): The other fastas, e.g. contaminants.
        """
        assert issubclass(other.__class__, self.__class__), "Can only add the same type of fastas."
        res = self.copy()
        res.append(other)
        return res

    def find_repeating_sequences(self):
        """Find all the fastas with the same sequences.

        Returns:
            dict: maps a sequence to a lists of fastas with that sequence.
        """
        rep_seq_prots = defaultdict(list)
        prot_seqs = {}
        for f in self:
            seq = str(f)
            if seq in prot_seqs:
                if not seq in rep_seq_prots:# need to add previous f
                    rep_seq_prots[seq].append(prot_seqs[seq])
                rep_seq_prots[seq].append(f)
            else:
                prot_seqs[seq] = f
        return dict(rep_seq_prots)



class UniprotFastas(Fastas):
    def read(self, path):
        """Read the fastas from a file.

        Args:
            path (str): path to the file.
        """
        with open(path, 'r') as f:
            raw = f.read()
        self.fastas.extend(parse_uniprot_fastas(raw))

    def parse_raw(self, raw):
        self.fastas.extend(parse_uniprot_fastas(raw))

    def to_ncbi_general(self):
        other = NCBIgeneralFastas()
        for f in self.fastas:
            other.fastas.append(f.to_gnl())
        return other


class NCBIgeneralFastas(Fastas):
    def read(self, path):
        """Read the fastas from a file.

        Args:
            path (str): path to the file.
        """
        with open(path, 'r') as f:
            raw = f.read()
        self.fastas.extend(parse_ncbi_general_fastas(raw))

    def parse_raw(self, raw):
        self.fastas.extend(parse_ncbi_general_fastas(raw))

    def add_reversed_fastas_for_plgs(self):
        for i in range(len(self.fastas)):
            self.fastas.append(self.fastas[i].reverse_for_plgs(i+1))