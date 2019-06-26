import os
from multiprocessing import Pool
from .defaults import (
    REPEAT_CHAR, FASTA_CHARS,
    ENCODE_ORDER,
    INCLUDE_URACIL, INCLUDE_REPEAT,
    FASTA_ENCODEX, FASTA_DECODEX
)

from .utils import (is_fasta, is_uracil)

class Codex:

    def __init__(
        self,
        include_uracil:bool = INCLUDE_URACIL,
        include_repeat:bool = INCLUDE_REPEAT,
        encode_order: list  = ENCODE_ORDER,
        repeat_char: str    = REPEAT_CHAR, # repeated masked regions
        encodex: dict       = FASTA_ENCODEX,
        decodex: dict       = FASTA_DECODEX,
        nts_chars: str      = 'actgu',
        fasta_chars: str    = 'actgrykmswbdhvn-',
        processes: int      = 1
    ):
        '''
        Arguments:
            include_uracil (bool): whether or not uracil should be included in the
                embedding. By default False.

            include_repeat (bool): wehtehr or not repeated masked regions should be
                included in the embedding. By default False.

            encode_order (list): the order in which the channels for the embedding
                should be placed. By default `['a', 'c', 't', 'g', 'u']`.

            repeat_char (str): the character to use for repeated masked regions.
                By default `"."`.

            encodex (dict): the dictionary converting fasta characters to
                nucleotides.

            decodex (dict): the dictionary converting nucleotide characters to
                fasta characters.

            nts_chars (str): valid nucleotide characters: By default: `"actgu"`

            fasta_chars (str): valid fasta characters. By default:
                `"actgrykmswbdhvn-"`

            processes (int): number of CPU cores to use when encoding / decoding.
                By default 1. If set to None, uses all.
        '''
        if processes is None: processes = os.cpu_count()
        self.processes = processes
        self.include_uracil = include_uracil
        self.include_repeat = include_repeat

        if include_uracil and 'u' not in encode_order:
            encode_order += ['u']
        if not include_uracil and 'u' in encode_order:
            encode_order = list(filter(lambda c: not is_uracil(c), encode_order))


        if include_repeat and repeat_char not in encode_order:
            encode_order += [repeat_char]
        self.encode_order = encode_order

        self.repeat_char = repeat_char
        self.encodex = encodex
        self.decodex = decodex
        self.nts_chars = nts_chars
        self.fasta_chars = fasta_chars

    def processes_to_use(self, n):
        '''
        Only intialize at most self.processes, but less if less is needed

        Arguments:
            n (int): number of things to process
        Returns:
            number of processes to use
        '''
        return min(n, self.processes)

    def encode_char(self, char:str):
        '''
        Arguments:
            char (str): a character to encode
        Returns:
            encoding (list): the encoding of the corresponding character.
        '''
        # lowercase letters indicate repeat-masked regions
        is_repeat = char.islower()
        as_lookup = char.lower()

        # what nts are specified by fasta character
        nts = list(self.encodex[as_lookup])

        # filter out uracil
        nts = list(filter(lambda nt: self.include_uracil or not is_uracil(nt), nts))

        encoding = [0 for nt in self.encode_order]
        for nt in nts:
            i = self.encode_order.index(nt)
            encoding[i] = 1


        # indicating if it is a repeat seperately requires custom solution
        if is_repeat and self.include_repeat:
            i = self.encode_order.index(self.repeat_char)
            encoding[i] = 1

        return encoding


    def decode_char(self, char:list):
        '''
        Arguments:
            char (list): an encoding of a character
        Returns:
            fasta (str): the decoded fastas character
        '''
        nts = [
            self.encode_order[i]
            for i, indicator in enumerate(char)
            if indicator > 0
        ]
        is_repeat = self.repeat_char in nts
        clean_nts = [nt for nt in nts if nt != self.repeat_char]
        clean_nts.sort()
        fasta = self.decodex[''.join(clean_nts)]
        if not is_repeat: fasta = fasta.upper()
        return fasta


    def decode(self, emb):
        '''
        Arguments:
            emb (list): a list of embedded characters
        Returns:
            fasta (str): the decoded embedding
        '''
        if self.processes == 1:
            return ''.join(list(map(self.decode_char, emb)))
        else:
            processes = self.processes_to_use(len(emb))
            with Pool(processes=processes) as pool:
                return ''.join(pool.starmap(self.decode_char, [[emb_c] for emb_c in emb]))


    def encode(self, seq):
        '''
        Arguments:
            seq (str): a string of characters to embed
        Returns:
            emb (list): the embedded sequence.
        '''
        if (not is_fasta(seq, self.fasta_chars)):
            raise ValueError('{} is not a valid fasta sequence')
        if self.processes == 1:
            return list(map(self.encode_char, list(seq)))
        else:
            processes = self.processes_to_use(len(list(seq)))
            with Pool(processes=processes) as pool:
                return pool.starmap(self.encode_char, list(seq))
