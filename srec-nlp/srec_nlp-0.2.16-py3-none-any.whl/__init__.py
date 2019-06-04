__version__ = "0.2.10"
from .srec_nlp import ParallelDots, TextProcessing, Aylien

from .exc import RateError

try:
    from .srec_nlp import FastText
except:
    pass
