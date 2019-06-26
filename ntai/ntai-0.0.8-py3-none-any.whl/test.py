from random import choices, random, randint
from .settings import FASTA_CHARS
def random_fasta(min_length:int=0, max_length:int=100, repeat_likelihood:float=0.5) -> str:
    n = randint(min_length, max_length)
    chars = choices(FASTA_CHARS, k=n)
    return ''.join([e if random() < repeat_likelihood else e.upper() for e in chars])
