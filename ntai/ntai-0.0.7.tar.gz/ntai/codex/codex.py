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
        fasta_chars: str    = 'actgrykmswbdhvn-'
    ):
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







    def encode_char(self, char:str):
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
        return ''.join(list(map(self.decode_char, emb)))

    def encode(self, seq):
        if (not is_fasta(seq, self.fasta_chars)):
            raise ValueError('{} is not a valid fasta sequence')
        return list(map(self.encode_char, list(seq)))
