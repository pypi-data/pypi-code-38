import re

uniprot_pattern = re.compile(r">(.+)\|(.+)\|(.*)")
gnl_pattern = re.compile(r">(.*)\|(.*)\|(\w+)\s(.*)")

class Fasta(object):
    """Class representing one particular fasta object."""
    def __init__(self, sequence, header):
        self.sequence = sequence
        self.header = header

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.header)

    def __str__(self):
        return self.sequence

    def reverse(self):
        new_header = self.header
        return self.__class__(self.sequence[::-1], new_header)

    def copy(self):
        return self.__class__(self.sequence, self.header)

    def __hash__(self):
        return hash((self.sequence, self.header))


class UniprotFasta(Fasta):
    """Fasta with a uniprot header."""
    def to_gnl(self):
        """Reformat the uniprot header to general ncbi format."""
        db, prot, desc = self.header.split('|')
        new_header = ">gnl|db|{} {}".format(prot, desc)
        return NCBIgeneralFasta(self.sequence, new_header)

    def to_ncbi_general(self):
        """Reformat the uniprot header to general ncbi format."""
        return self.to_gnl()


class NCBIgeneralFasta(Fasta):
    """Fasta with a ncbi general header (according to PLGS)."""
    def to_uniprot(self):
        """Reformat the NCBI general header to uniprot format."""
        tag, db, pdbno, desc = re.match(gnl_pattern, self.header)
        new_header = ">sp|{}|{}".format(pdbno, desc)
        return UniprotFasta(new_header, self.sequence)

    def reverse_for_plgs(self, i):
        h = ">REVERSE{} Reversed Sequence {}".format(i,i)
        return self.__class__(self.sequence[::-1], h)